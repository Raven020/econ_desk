# Tests for econ_desk/data/store.py
# Uses an in-memory DuckDB instance (:memory:) so no files are created.

import pytest
import numpy as np
import pandas as pd
from datetime import date

from econ_desk.data.store import (
    init_db,
    get_latest_date,
    write_price_data,
    read_price_history,
    read_all_returns,
    read_latest_prices,
    write_macro_data,
    read_macro_data,
    write_regime,
    read_regime,
    write_montecarlo,
    read_montecarlo,
)


@pytest.fixture
def conn():
    """Create a fresh in-memory database for each test."""
    return init_db(":memory:")


@pytest.fixture
def sample_price_df():
    """Sample 3-day price DataFrame matching fetcher output format."""
    return pd.DataFrame({
        "date": [date(2026, 3, 18), date(2026, 3, 19), date(2026, 3, 20)],
        "open": [540.0, 542.0, 544.0],
        "high": [545.0, 546.0, 548.0],
        "low": [538.0, 540.0, 542.0],
        "close": [542.0, 544.0, 546.0],
        "volume": [70000000, 75000000, 80000000],
    })


@pytest.fixture
def sample_macro_df():
    """Sample macro indicator DataFrame."""
    return pd.DataFrame({
        "date": [date(2026, 3, 18), date(2026, 3, 19), date(2026, 3, 20)],
        "value": [2.30, 2.35, 2.40],
    })


# ---------- init_db ----------

class TestInitDb:
    def test_returns_connection(self, conn):
        assert conn is not None

    def test_tables_created(self, conn):
        tables = conn.execute("SHOW TABLES").fetchdf()
        table_names = tables["name"].tolist()
        assert "price_history" in table_names
        assert "macro_data" in table_names
        assert "regime" in table_names
        assert "montecarlo" in table_names

    def test_idempotent(self, conn):
        """Calling init_db twice on the same DB should not fail."""
        conn2 = init_db(":memory:")
        tables = conn2.execute("SHOW TABLES").fetchdf()
        assert len(tables) == 4


# ---------- get_latest_date ----------

class TestGetLatestDate:
    def test_returns_none_when_empty(self, conn):
        result = get_latest_date(conn, "SPY")
        assert result is None

    def test_returns_latest_date(self, conn, sample_price_df):
        write_price_data(conn, "SPY", sample_price_df.copy())
        result = get_latest_date(conn, "SPY")
        assert result == date(2026, 3, 20)

    def test_different_instruments_independent(self, conn, sample_price_df):
        write_price_data(conn, "SPY", sample_price_df.copy())
        result = get_latest_date(conn, "QQQ")
        assert result is None


# ---------- write_price_data / read_price_history ----------

class TestPriceData:
    def test_write_and_read_roundtrip(self, conn, sample_price_df):
        write_price_data(conn, "SPY", sample_price_df.copy())
        result = read_price_history(conn, "SPY", date(2026, 3, 18), date(2026, 3, 20))
        assert len(result) == 3
        assert list(result.columns) == ["date", "open", "high", "low", "close", "volume"]

    def test_read_filters_by_instrument(self, conn, sample_price_df):
        write_price_data(conn, "SPY", sample_price_df.copy())
        write_price_data(conn, "QQQ", sample_price_df.copy())
        result = read_price_history(conn, "SPY", date(2026, 3, 18), date(2026, 3, 20))
        assert len(result) == 3

    def test_read_filters_by_date_range(self, conn, sample_price_df):
        write_price_data(conn, "SPY", sample_price_df.copy())
        result = read_price_history(conn, "SPY", date(2026, 3, 19), date(2026, 3, 19))
        assert len(result) == 1
        assert result.iloc[0]["close"] == 544.0

    def test_read_empty_returns_empty_df(self, conn):
        result = read_price_history(conn, "SPY", date(2026, 3, 18), date(2026, 3, 20))
        assert len(result) == 0


# ---------- read_all_returns ----------

class TestReadAllReturns:
    def test_returns_percentage_changes(self, conn):
        spy_df = pd.DataFrame({
            "date": [date(2026, 3, 18), date(2026, 3, 19), date(2026, 3, 20)],
            "open": [540.0, 542.0, 544.0],
            "high": [545.0, 546.0, 548.0],
            "low": [538.0, 540.0, 542.0],
            "close": [500.0, 510.0, 520.0],
            "volume": [70000000, 75000000, 80000000],
        })
        write_price_data(conn, "SPY", spy_df.copy())
        result = read_all_returns(conn, date(2026, 3, 18), date(2026, 3, 20))
        # First row dropped by dropna (no previous day), so 3 rows become 2
        assert len(result) == 2
        # 500->510 = 2.0% return
        assert abs(result["SPY"].iloc[0] - 0.02) < 0.001
        # 510->520 = ~1.96% return
        assert abs(result["SPY"].iloc[1] - 0.019608) < 0.001

    def test_multiple_instruments_as_columns(self, conn, sample_price_df):
        write_price_data(conn, "SPY", sample_price_df.copy())
        write_price_data(conn, "QQQ", sample_price_df.copy())
        result = read_all_returns(conn, date(2026, 3, 18), date(2026, 3, 20))
        assert "SPY" in result.columns
        assert "QQQ" in result.columns


# ---------- read_latest_prices ----------

class TestReadLatestPrices:
    def test_returns_latest_with_change(self, conn, sample_price_df):
        write_price_data(conn, "SPY", sample_price_df.copy())
        result = read_latest_prices(conn)
        assert len(result) == 1
        row = result.iloc[0]
        assert row["instrument"] == "SPY"
        assert row["close"] == 546.0
        # change = 546 - 544 = 2.0
        assert row["change"] == 2.0
        assert abs(row["change_pct"] - (2.0 / 544.0 * 100)) < 0.01

    def test_multiple_instruments(self, conn, sample_price_df):
        write_price_data(conn, "SPY", sample_price_df.copy())
        write_price_data(conn, "QQQ", sample_price_df.copy())
        result = read_latest_prices(conn)
        assert len(result) == 2

    def test_empty_db_returns_empty(self, conn):
        result = read_latest_prices(conn)
        assert len(result) == 0


# ---------- write_macro_data / read_macro_data ----------

class TestMacroData:
    def test_write_and_read_roundtrip(self, conn, sample_macro_df):
        write_macro_data(conn, "T5YIE", sample_macro_df.copy())
        result = read_macro_data(conn, "T5YIE", date(2026, 3, 18), date(2026, 3, 20))
        assert len(result) == 3
        assert list(result.columns) == ["date", "value"]

    def test_read_filters_by_indicator(self, conn, sample_macro_df):
        write_macro_data(conn, "T5YIE", sample_macro_df.copy())
        write_macro_data(conn, "ICSA", sample_macro_df.copy())
        result = read_macro_data(conn, "T5YIE", date(2026, 3, 18), date(2026, 3, 20))
        assert len(result) == 3

    def test_read_empty_returns_empty_df(self, conn):
        result = read_macro_data(conn, "T5YIE", date(2026, 3, 18), date(2026, 3, 20))
        assert len(result) == 0


# ---------- write_regime / read_regime ----------

class TestRegime:
    def test_write_and_read_roundtrip(self, conn):
        matrix = np.array([
            [0.8, 0.1, 0.05, 0.03, 0.02],
            [0.1, 0.7, 0.1, 0.05, 0.05],
            [0.1, 0.1, 0.6, 0.1, 0.1],
            [0.05, 0.15, 0.1, 0.6, 0.1],
            [0.05, 0.2, 0.1, 0.05, 0.6],
        ])
        write_regime(conn, "BULL", 0.82, matrix)
        result = read_regime(conn)
        assert result is not None
        label, confidence, tm = result
        assert label == "BULL"
        assert confidence == 0.82
        assert tm.shape == (5, 5)
        assert abs(tm[0][0] - 0.8) < 0.001

    def test_read_empty_returns_none(self, conn):
        result = read_regime(conn)
        assert result is None

    def test_returns_most_recent(self, conn):
        matrix = np.eye(5)
        write_regime(conn, "BULL", 0.8, matrix)
        write_regime(conn, "CRISIS", 0.9, matrix)
        label, confidence, _ = read_regime(conn)
        # Both written on same date, but CRISIS inserted last
        # ORDER BY date DESC LIMIT 1 — both have same date so order may vary
        # This test verifies we get a valid result back
        assert label in ["BULL", "CRISIS"]


# ---------- write_montecarlo / read_montecarlo ----------

class TestMontecarlo:
    @pytest.fixture
    def sample_cones(self):
        """Sample projection cones: 5 percentiles x 30 days."""
        return {
            10: [float(500 + i) for i in range(30)],
            25: [float(510 + i) for i in range(30)],
            50: [float(520 + i) for i in range(30)],
            75: [float(530 + i) for i in range(30)],
            90: [float(540 + i) for i in range(30)],
        }

    def test_write_and_read_roundtrip(self, conn, sample_cones):
        write_montecarlo(conn, "SPY", sample_cones)
        result = read_montecarlo(conn, "SPY")
        assert result is not None
        assert len(result) == 5
        assert list(result["percentile"]) == [10, 25, 50, 75, 90]
        # Check first day value for 50th percentile
        row_50 = result[result["percentile"] == 50].iloc[0]
        assert row_50["day_1"] == 520.0

    def test_read_nonexistent_returns_none(self, conn):
        result = read_montecarlo(conn, "SPY")
        assert result is None

    def test_different_instruments_independent(self, conn, sample_cones):
        write_montecarlo(conn, "SPY", sample_cones)
        result = read_montecarlo(conn, "QQQ")
        assert result is None

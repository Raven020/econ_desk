# Tests for econ_desk/data/fred.py
# Mocks fredapi so no real API calls are made.

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import date

from econ_desk.data.fred import fetch


@pytest.fixture
def mock_fred_series():
    """Fake pandas Series that fredapi.Fred.get_series() would return."""
    index = pd.to_datetime(["2026-03-18", "2026-03-19", "2026-03-20"])
    return pd.Series([2.30, 2.35, 2.40], index=index)


@pytest.fixture
def mock_fred_series_with_nan():
    """Fake Series with NaN gaps (holidays/weekends)."""
    index = pd.to_datetime(["2026-03-18", "2026-03-19", "2026-03-20"])
    return pd.Series([2.30, float("nan"), 2.40], index=index)


class TestFetch:
    @patch("econ_desk.data.fred.Fred")
    def test_returns_dataframe_with_correct_columns(self, MockFred, mock_fred_series):
        mock_instance = MagicMock()
        mock_instance.get_series.return_value = mock_fred_series
        MockFred.return_value = mock_instance

        result = fetch("T5YIE", "2026-03-18", "2026-03-20")

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["date", "value"]

    @patch("econ_desk.data.fred.Fred")
    def test_returns_correct_number_of_rows(self, MockFred, mock_fred_series):
        mock_instance = MagicMock()
        mock_instance.get_series.return_value = mock_fred_series
        MockFred.return_value = mock_instance

        result = fetch("T5YIE", "2026-03-18", "2026-03-20")
        assert len(result) == 3

    @patch("econ_desk.data.fred.Fred")
    def test_correct_values(self, MockFred, mock_fred_series):
        mock_instance = MagicMock()
        mock_instance.get_series.return_value = mock_fred_series
        MockFred.return_value = mock_instance

        result = fetch("T5YIE", "2026-03-18", "2026-03-20")
        assert result.iloc[0]["value"] == 2.30
        assert result.iloc[2]["value"] == 2.40

    @patch("econ_desk.data.fred.Fred")
    def test_drops_nan_values(self, MockFred, mock_fred_series_with_nan):
        mock_instance = MagicMock()
        mock_instance.get_series.return_value = mock_fred_series_with_nan
        MockFred.return_value = mock_instance

        result = fetch("T5YIE", "2026-03-18", "2026-03-20")
        assert len(result) == 2
        assert 2.30 in result["value"].values
        assert 2.40 in result["value"].values

    @patch("econ_desk.data.fred.Fred")
    def test_calls_fred_with_correct_args(self, MockFred, mock_fred_series):
        mock_instance = MagicMock()
        mock_instance.get_series.return_value = mock_fred_series
        MockFred.return_value = mock_instance

        fetch("ICSA", "2026-03-18", "2026-03-20")

        mock_instance.get_series.assert_called_once_with(
            "ICSA",
            observation_start="2026-03-18",
            observation_end="2026-03-20",
        )

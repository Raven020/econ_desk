# Tests for econ_desk/data/yahoo.py
# Mocks yfinance so no real API calls are made.

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from datetime import date

from econ_desk.data.yahoo import fetch


@pytest.fixture
def mock_yf_history():
    """Fake DataFrame that yfinance Ticker.history() would return."""
    return pd.DataFrame({
        "Open": [540.0, 542.0],
        "High": [545.0, 546.0],
        "Low": [538.0, 540.0],
        "Close": [542.0, 544.0],
        "Volume": [70000000, 75000000],
        "Dividends": [0.0, 0.0],
        "Stock Splits": [0.0, 0.0],
    }, index=pd.to_datetime(["2026-03-18", "2026-03-19"]))


class TestFetch:
    @patch("econ_desk.data.yahoo.yf")
    def test_returns_dataframe_with_correct_columns(self, mock_yf, mock_yf_history):
        mock_yf_history.index.name = "Date"
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_yf_history
        mock_yf.Ticker.return_value = mock_ticker

        result = fetch("SPY", "2026-03-18", "2026-03-19")

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["date", "open", "high", "low", "close", "volume"]

    @patch("econ_desk.data.yahoo.yf")
    def test_returns_correct_number_of_rows(self, mock_yf, mock_yf_history):
        mock_yf_history.index.name = "Date"
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_yf_history
        mock_yf.Ticker.return_value = mock_ticker

        result = fetch("SPY", "2026-03-18", "2026-03-19")
        assert len(result) == 2

    @patch("econ_desk.data.yahoo.yf")
    def test_excludes_extra_columns(self, mock_yf, mock_yf_history):
        """Dividends and Stock Splits from yfinance should be dropped."""
        mock_yf_history.index.name = "Date"
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_yf_history
        mock_yf.Ticker.return_value = mock_ticker

        result = fetch("SPY", "2026-03-18", "2026-03-19")
        assert "Dividends" not in result.columns
        assert "Stock Splits" not in result.columns

    @patch("econ_desk.data.yahoo.yf")
    def test_correct_values(self, mock_yf, mock_yf_history):
        mock_yf_history.index.name = "Date"
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_yf_history
        mock_yf.Ticker.return_value = mock_ticker

        result = fetch("SPY", "2026-03-18", "2026-03-19")
        assert result.iloc[0]["close"] == 542.0
        assert result.iloc[1]["volume"] == 75000000

    @patch("econ_desk.data.yahoo.yf")
    def test_calls_yfinance_with_correct_args(self, mock_yf, mock_yf_history):
        mock_yf_history.index.name = "Date"
        mock_ticker = MagicMock()
        mock_ticker.history.return_value = mock_yf_history
        mock_yf.Ticker.return_value = mock_ticker

        fetch("GC=F", "2026-03-18", "2026-03-19")

        mock_yf.Ticker.assert_called_once_with("GC=F")
        mock_ticker.history.assert_called_once_with(start="2026-03-18", end="2026-03-19")

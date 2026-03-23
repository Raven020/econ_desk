# Tests for econ_desk/data/coingecko.py
# Mocks requests so no real API calls are made.

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from econ_desk.data.coingecko import fetch


@pytest.fixture
def mock_coingecko_response():
    """Fake CoinGecko /market_chart/range JSON response."""
    # Two days of data: timestamps in milliseconds
    return {
        "prices": [
            [1742256000000, 87200.0],  # 2025-03-18
            [1742342400000, 88100.0],  # 2025-03-19
        ],
        "total_volumes": [
            [1742256000000, 24000000000.0],
            [1742342400000, 25000000000.0],
        ],
    }


class TestFetch:
    @patch("econ_desk.data.coingecko.requests")
    def test_returns_dataframe_with_correct_columns(self, mock_requests, mock_coingecko_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_coingecko_response
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        result = fetch("bitcoin", "2025-03-18", "2025-03-19")

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["date", "open", "high", "low", "close", "volume"]

    @patch("econ_desk.data.coingecko.requests")
    def test_returns_correct_number_of_rows(self, mock_requests, mock_coingecko_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_coingecko_response
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        result = fetch("bitcoin", "2025-03-18", "2025-03-19")
        assert len(result) == 2

    @patch("econ_desk.data.coingecko.requests")
    def test_correct_close_prices(self, mock_requests, mock_coingecko_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_coingecko_response
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        result = fetch("bitcoin", "2025-03-18", "2025-03-19")
        assert result.iloc[0]["close"] == 87200.0
        assert result.iloc[1]["close"] == 88100.0

    @patch("econ_desk.data.coingecko.requests")
    def test_volume_merged_correctly(self, mock_requests, mock_coingecko_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_coingecko_response
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        result = fetch("bitcoin", "2025-03-18", "2025-03-19")
        assert result.iloc[0]["volume"] == 24000000000.0

    @patch("econ_desk.data.coingecko.requests")
    def test_calls_correct_endpoint(self, mock_requests, mock_coingecko_response):
        mock_response = MagicMock()
        mock_response.json.return_value = mock_coingecko_response
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        fetch("ethereum", "2025-03-18", "2025-03-19")

        call_args = mock_requests.get.call_args
        assert "ethereum" in call_args[0][0]
        assert call_args[1]["params"]["vs_currency"] == "usd"

    @patch("econ_desk.data.coingecko.requests")
    def test_raises_on_http_error(self, mock_requests):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("404 Not Found")
        mock_requests.get.return_value = mock_response

        with pytest.raises(Exception):
            fetch("invalidcoin", "2025-03-18", "2025-03-19")

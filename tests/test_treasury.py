# Tests for econ_desk/data/treasury.py
# Mocks requests so no real API calls are made.

import pytest
import pandas as pd
from unittest.mock import patch, MagicMock

from econ_desk.data.treasury import fetch


SAMPLE_XML = """<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom"
      xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
      xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices">
  <entry>
    <content type="application/xml">
      <m:properties>
        <d:NEW_DATE>2026-03-18T00:00:00</d:NEW_DATE>
        <d:BC_2YEAR>4.12</d:BC_2YEAR>
        <d:BC_10YEAR>3.70</d:BC_10YEAR>
      </m:properties>
    </content>
  </entry>
  <entry>
    <content type="application/xml">
      <m:properties>
        <d:NEW_DATE>2026-03-19T00:00:00</d:NEW_DATE>
        <d:BC_2YEAR>4.15</d:BC_2YEAR>
        <d:BC_10YEAR>3.72</d:BC_10YEAR>
      </m:properties>
    </content>
  </entry>
</feed>"""


class TestFetch:
    @patch("econ_desk.data.treasury.requests")
    def test_returns_dataframe_with_correct_columns(self, mock_requests):
        mock_response = MagicMock()
        mock_response.content = SAMPLE_XML.encode()
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        result = fetch("2026-03-18", "2026-03-19")

        assert isinstance(result, pd.DataFrame)
        assert list(result.columns) == ["date", "indicator", "value"]

    @patch("econ_desk.data.treasury.requests")
    def test_returns_two_indicators_per_date(self, mock_requests):
        mock_response = MagicMock()
        mock_response.content = SAMPLE_XML.encode()
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        result = fetch("2026-03-18", "2026-03-19")
        # 2 dates x 2 indicators = 4 rows
        assert len(result) == 4

    @patch("econ_desk.data.treasury.requests")
    def test_correct_indicator_names(self, mock_requests):
        mock_response = MagicMock()
        mock_response.content = SAMPLE_XML.encode()
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        result = fetch("2026-03-18", "2026-03-19")
        indicators = result["indicator"].unique().tolist()
        assert "YIELD_2Y" in indicators
        assert "YIELD_10Y" in indicators

    @patch("econ_desk.data.treasury.requests")
    def test_correct_values(self, mock_requests):
        mock_response = MagicMock()
        mock_response.content = SAMPLE_XML.encode()
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        result = fetch("2026-03-18", "2026-03-19")
        yield_2y_mar18 = result[(result["date"] == "2026-03-18") & (result["indicator"] == "YIELD_2Y")]
        assert yield_2y_mar18.iloc[0]["value"] == 4.12

    @patch("econ_desk.data.treasury.requests")
    def test_raises_on_http_error(self, mock_requests):
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = Exception("500 Server Error")
        mock_requests.get.return_value = mock_response

        with pytest.raises(Exception):
            fetch("2026-03-18", "2026-03-19")

    @patch("econ_desk.data.treasury.requests")
    def test_empty_response(self, mock_requests):
        empty_xml = """<?xml version="1.0" encoding="utf-8"?>
        <feed xmlns="http://www.w3.org/2005/Atom"
              xmlns:m="http://schemas.microsoft.com/ado/2007/08/dataservices/metadata"
              xmlns:d="http://schemas.microsoft.com/ado/2007/08/dataservices">
        </feed>"""
        mock_response = MagicMock()
        mock_response.content = empty_xml.encode()
        mock_response.raise_for_status.return_value = None
        mock_requests.get.return_value = mock_response

        result = fetch("2026-03-18", "2026-03-19")
        assert len(result) == 0

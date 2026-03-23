# Configuration constants for Econ Desk.
# Instrument ticker lists, API keys, database path, HMM parameters,
# Monte Carlo settings, and regime definitions.

import os
from dotenv import load_dotenv

load_dotenv()

# API Keys
FRED_API_KEY = os.getenv("FRED_API_KEY")
COINGECKO_API_KEY = os.getenv("COINGECKO_API_KEY")

# Database
DB_PATH = "data/econ_desk.duckdb"

# Yahoo Finance tickers
EQUITY_TICKERS = ["SPY", "IWM", "QQQ", "DIA"]
COMMODITY_TICKERS = ["CL=F", "GC=F", "SI=F", "NG=F", "HG=F", "ZW=F"]
VOLATILITY_TICKERS = ["^VIX"]
FX_TICKERS = ["DX-Y.NYB"]
YAHOO_TICKERS = EQUITY_TICKERS + COMMODITY_TICKERS + VOLATILITY_TICKERS + FX_TICKERS

# CoinGecko IDs
CRYPTO_IDS = {
    "BTC": "bitcoin",
    "ETH": "ethereum",
    "SOL": "solana",
}

# FRED series IDs
FRED_SERIES = {
    "FED_FUNDS": "FEDFUNDS",
    "INFLATION_5Y_BE": "T5YIE",
    "JOBLESS_CLAIMS": "ICSA",
    "YIELD_SPREAD_2S10S": "T10Y2Y",
}

# HMM settings
HMM_LOOKBACK_YEARS = 5
HMM_NUM_REGIMES = 5
REGIME_LABELS = ["BULL", "BEAR", "STAGNATION", "STAGFLATION", "CRISIS"]

# Monte Carlo settings
MC_NUM_PATHS = 10000
MC_HORIZON_DAYS = 30
MC_PERCENTILES = [10, 25, 50, 75, 90]

# All instrument names (for tab autocompletion)
ALL_INSTRUMENTS = (
    EQUITY_TICKERS
    + COMMODITY_TICKERS
    + VOLATILITY_TICKERS
    + FX_TICKERS
    + list(CRYPTO_IDS.keys())
)

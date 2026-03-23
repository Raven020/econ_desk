# Drilldown detail view for a single instrument.
# Shows current price, daily high/low, volume, 24h volume change,
# a price chart, Monte Carlo projection cones with percentile bands,
# and regime context for the selected asset.

from textual.screen import Screen
from textual.widgets import Static, Header, Footer
from textual.widgets import Sparkline

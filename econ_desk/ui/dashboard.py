# Main dashboard screen.
# Displays the price table for all tracked instruments with current price,
# daily change, and directional indicators. Shows the current HMM regime
# banner with confidence and transition probabilities.

from textual.screen import Screen
from textual.widgets import DataTable, Header, Footer, Static

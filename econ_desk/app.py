# Textual application entry point.
# Initializes the app, sets up screen routing between dashboard and drilldown,
# and coordinates data refresh and model recalibration.

from textual.app import App

from econ_desk.data.store import Store
from econ_desk.ui.dashboard import DashboardScreen
from econ_desk.ui.drilldown import DrilldownScreen

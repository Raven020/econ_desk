# Multivariate Monte Carlo simulation engine.
# Takes regime-conditioned mean returns and covariance matrix,
# simulates 10,000 correlated return paths over a 30-day horizon
# using Student's t-distribution for fat tails.
# Produces per-asset projection cones (10/25/50/75/90 percentiles).

import numpy as np
from scipy.stats import t as students_t

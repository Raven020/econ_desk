# Hidden Markov Model for macro regime detection.
# Wraps hmmlearn to train a 5-state Gaussian HMM on rolling asset returns
# and macro indicators. Outputs current regime, confidence score,
# and 30-day transition probability matrix.
# Retrains daily on a 5-year rolling window.

from hmmlearn.hmm import GaussianHMM
import numpy as np

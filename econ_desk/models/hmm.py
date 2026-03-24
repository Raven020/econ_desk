# Hidden Markov Model for macro regime detection.
# Wraps hmmlearn to train a 5-state Gaussian HMM on rolling asset returns
# and macro indicators. Outputs current regime, confidence score,
# and 30-day transition probability matrix.
# Retrains daily on a 5-year rolling window.

from hmmlearn.hmm import GaussianHMM
import numpy as np


def build_feature_matrix(returns: np.ndarray, macro: np.ndarray) -> np.ndarray:
    """Combine asset returns and macro indicators into a single feature matrix.

    Args:
        returns: Array of shape (T, n_assets) with rolling daily returns
            for all tracked instruments.
        macro: Array of shape (T, n_macro) with macro indicators
            (yields, spreads, VIX, DXY, inflation expectations, jobless claims).

    Returns:
        Feature matrix of shape (T, n_assets + n_macro) ready for HMM training.
    """
    pass


def train_hmm(features: np.ndarray, n_states: int = 5, n_iter: int = 100) -> GaussianHMM:
    """Train a Gaussian HMM on the feature matrix.

    Fits a 5-state Gaussian HMM using EM on the provided feature matrix.
    Uses a 5-year rolling window of data.

    Args:
        features: Feature matrix of shape (T, n_features) from build_feature_matrix.
        n_states: Number of hidden states (default 5: Bull, Bear,
            Stagnation, Stagflation, Crisis).
        n_iter: Maximum EM iterations for training.

    Returns:
        Trained GaussianHMM model instance.
    """
    pass


def decode_regime(model: GaussianHMM, features: np.ndarray) -> tuple[int, np.ndarray]:
    """Decode the most likely current regime and state probabilities.

    Runs the Viterbi algorithm on the feature sequence to determine
    the current hidden state, then computes posterior state probabilities
    for the most recent observation.

    Args:
        model: Trained GaussianHMM instance.
        features: Feature matrix of shape (T, n_features).

    Returns:
        Tuple of:
            - current_state: int index of the most likely current regime (0-4).
            - state_probs: Array of shape (n_states,) with posterior
              probabilities for each state at the latest time step
              (the max value is the confidence score).
    """
    pass


def get_transition_matrix(model: GaussianHMM) -> np.ndarray:
    """Extract the 30-day transition probability matrix from the trained model.

    Raises the single-step transition matrix to the 30th power to get
    the probability of transitioning between any two regimes over a
    30-day horizon.

    Args:
        model: Trained GaussianHMM instance.

    Returns:
        Transition matrix of shape (n_states, n_states) where entry [i, j]
        is the probability of moving from regime i to regime j in 30 days.
    """
    pass

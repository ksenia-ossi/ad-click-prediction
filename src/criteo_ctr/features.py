"""Feature engineering for Criteo CTR.

Two representations are produced from the same raw frame:
- `make_linear_features`: sparse matrix for logistic regression
  (log-transformed numerics + missing indicators + hashed one-hot categoricals).
- `make_tree_features`: dense frame for LightGBM (raw numerics, categoricals as
  pandas `category` with rare values grouped).
"""
import numpy as np
import pandas as pd
import scipy.sparse as sp
from sklearn.feature_extraction import FeatureHasher

from .config import CAT_COLS, INT_COLS, LABEL, TEST_FRACTION

N_HASH_FEATURES = 2**18
RARE_THRESHOLD = 10


def time_split(df: pd.DataFrame, test_fraction: float = TEST_FRACTION):
    """Rows are chronological -> last `test_fraction` of rows is the test set."""
    cut = int(len(df) * (1 - test_fraction))
    return df.iloc[:cut], df.iloc[cut:]


def transform_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """log1p compresses heavy-tailed count features; a *_missing flag keeps the
    information that the value was absent (missingness itself predicts clicks)."""
    out = pd.DataFrame(index=df.index)
    for c in INT_COLS:
        x = df[c].astype("float32")
        out[f"{c}_missing"] = x.isna().astype("float32")
        out[c] = np.log1p(x.clip(lower=0).fillna(0)).astype("float32")
    return out


def _cat_tokens(df: pd.DataFrame) -> list[list[str]]:
    """Each row -> ["c1=68fd1e64", "c2=80e26c9b", ...]; missing -> "c1=NA"."""
    vals = df[CAT_COLS].fillna("NA").astype(str).to_numpy()
    return [[f"{c}={v}" for c, v in zip(CAT_COLS, row)] for row in vals]


def make_linear_features(df: pd.DataFrame, n_features: int = N_HASH_FEATURES) -> sp.csr_matrix:
    """Hashing trick: no vocabulary to store, unseen values at test time are handled
    for free, and dimensionality is bounded (2^18 columns) regardless of cardinality."""
    hasher = FeatureHasher(n_features=n_features, input_type="string", alternate_sign=False)
    cats = hasher.transform(_cat_tokens(df))
    nums = sp.csr_matrix(transform_numeric(df).to_numpy())
    return sp.hstack([nums, cats], format="csr")


def fit_rare_maps(train: pd.DataFrame, threshold: int = RARE_THRESHOLD) -> dict[str, set]:
    """Values seen fewer than `threshold` times in TRAIN are mapped to 'RARE'.
    Fitted on train only to avoid leaking test-set statistics."""
    return {c: set(train[c].value_counts().loc[lambda s: s >= threshold].index) for c in CAT_COLS}


def make_tree_features(df: pd.DataFrame, keep: dict[str, set]) -> pd.DataFrame:
    out = df[INT_COLS].astype("float32").copy()
    for c in CAT_COLS:
        col = df[c].fillna("NA")
        col = col.where(col.isin(keep[c]), "RARE")
        out[c] = pd.Categorical(col, categories=sorted(keep[c] | {"NA", "RARE"}))
    return out


def labels(df: pd.DataFrame) -> np.ndarray:
    return df[LABEL].to_numpy()

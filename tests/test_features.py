import numpy as np
import pandas as pd

from criteo_ctr.config import CAT_COLS, COLUMNS, INT_COLS
from criteo_ctr.features import (
    fit_rare_maps, make_linear_features, make_tree_features, time_split, transform_numeric,
)


def _frame(n=20):
    rng = np.random.default_rng(0)
    df = pd.DataFrame({"label": rng.integers(0, 2, n)})
    for c in INT_COLS:
        df[c] = rng.integers(0, 100, n).astype("float32")
    for c in CAT_COLS:
        df[c] = pd.Series(rng.choice(["aaaaaaaa", "bbbbbbbb", "cccccccc"], n), dtype="string")
    df.loc[0, "i1"] = np.nan
    df.loc[1, "c1"] = pd.NA
    return df[COLUMNS]


def test_time_split_keeps_order_and_fraction():
    df = _frame(100)
    train, test = time_split(df, 0.2)
    assert len(train) == 80 and len(test) == 20
    assert train.index.max() < test.index.min()


def test_transform_numeric_flags_missing_and_logs():
    out = transform_numeric(_frame())
    assert out.loc[0, "i1_missing"] == 1 and out.loc[0, "i1"] == 0
    assert out.loc[1, "i1_missing"] == 0
    assert (out[INT_COLS] >= 0).all().all()
    assert out.shape[1] == 2 * len(INT_COLS)


def test_linear_features_shape_and_missing_cat():
    df = _frame()
    X = make_linear_features(df, n_features=1024)
    assert X.shape == (len(df), 2 * len(INT_COLS) + 1024)
    # every row has exactly 26 categorical tokens (missing -> "NA" token)
    cat_part = X[:, 2 * len(INT_COLS):]
    assert np.allclose(cat_part.sum(axis=1).A1, len(CAT_COLS))


def test_tree_features_groups_rare_values():
    train = _frame(50)
    train.loc[:, "c2"] = "aaaaaaaa"
    train.loc[0, "c2"] = "zzzzzzzz"  # seen once -> rare
    keep = fit_rare_maps(train, threshold=2)
    X = make_tree_features(train, keep)
    assert X.loc[0, "c2"] == "RARE"
    assert X["c2"].dtype == "category"
    # unseen test value also becomes RARE, no crash
    test = _frame(5)
    test.loc[:, "c2"] = "yyyyyyyy"
    assert (make_tree_features(test, keep)["c2"] == "RARE").all()

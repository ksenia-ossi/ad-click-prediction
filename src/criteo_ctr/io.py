import pandas as pd

from .config import CAT_COLS, COLUMNS, INT_COLS, RAW_FILE


def load_raw(path=RAW_FILE, nrows: int | None = None) -> pd.DataFrame:
    """Read the tab-separated Criteo file. Empty fields become NaN."""
    dtypes = {c: "float32" for c in INT_COLS} | {c: "string" for c in CAT_COLS}
    df = pd.read_csv(path, sep="\t", header=None, names=COLUMNS, dtype=dtypes, nrows=nrows)
    df["label"] = df["label"].astype("int8")
    return df

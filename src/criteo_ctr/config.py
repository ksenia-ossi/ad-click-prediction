from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
RAW_FILE = RAW_DIR / "dac_sample.txt"
REPORTS = ROOT / "reports"
FIGURES = REPORTS / "figures"

SAMPLE_URL = "https://huggingface.co/datasets/Recommenders/criteo/resolve/main/dac_sample.tar.gz"

LABEL = "label"
INT_COLS = [f"i{i}" for i in range(1, 14)]
CAT_COLS = [f"c{i}" for i in range(1, 27)]
COLUMNS = [LABEL] + INT_COLS + CAT_COLS

PG_DSN = "postgresql://criteo:criteo@localhost:5432/criteo"

# Rows are chronologically ordered, so we split by time (last 20% = test),
# which mimics production: train on the past, predict the future.
TEST_FRACTION = 0.2
SEED = 42

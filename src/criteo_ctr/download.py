"""Download and extract the official Criteo Display Advertising sample (100k rows)."""
import tarfile
import urllib.request

from .config import RAW_DIR, RAW_FILE, SAMPLE_URL


def main() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    if RAW_FILE.exists():
        print(f"{RAW_FILE} already exists")
        return
    archive = RAW_DIR / "dac_sample.tar.gz"
    print(f"downloading {SAMPLE_URL}")
    urllib.request.urlretrieve(SAMPLE_URL, archive)
    with tarfile.open(archive) as tar:
        tar.extractall(RAW_DIR, filter="data")
    print(f"extracted to {RAW_FILE}")


if __name__ == "__main__":
    main()

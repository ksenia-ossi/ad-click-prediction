"""Exploratory data analysis with pandas/Matplotlib -> reports/eda.md + reports/figures/."""
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from .config import CAT_COLS, FIGURES, INT_COLS, LABEL, REPORTS
from .io import load_raw


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    df = load_raw()
    md = [f"# EDA — Criteo sample\n\nRows: {len(df):,} · CTR: {df[LABEL].mean():.3f}\n"]

    # 1. Missing values
    miss = df.isna().mean().drop(LABEL).sort_values(ascending=False)
    md.append("## Missing rate per feature (top 10)\n\n" + miss.head(10).to_frame("missing_rate").round(3).to_markdown() + "\n")
    miss.plot.bar(figsize=(10, 3.5), color="#2a4a7f", title="Missing rate per feature")
    plt.tight_layout(); plt.savefig(FIGURES / "missing_rate.png", dpi=120); plt.close()

    # 2. Numeric distributions are heavy-tailed -> log scale
    fig, axes = plt.subplots(3, 5, figsize=(15, 8))
    for ax, c in zip(axes.flat, INT_COLS):
        x = df[c].dropna().clip(lower=0)
        ax.hist(np.log1p(x), bins=40, color="#2a4a7f")
        ax.set_title(f"log1p({c})"); ax.set_yticks([])
    for ax in axes.flat[len(INT_COLS):]:
        ax.axis("off")
    fig.suptitle("Numeric features (log1p) — heavy tails justify the log transform")
    plt.tight_layout(); plt.savefig(FIGURES / "numeric_hist.png", dpi=110); plt.close()

    desc = df[INT_COLS].describe().T[["mean", "50%", "max"]].round(1)
    md.append("## Numeric features: mean vs median vs max (skew)\n\n" + desc.to_markdown() + "\n")

    # 3. Categorical cardinality
    card = df[CAT_COLS].nunique().sort_values(ascending=False)
    md.append("## Cardinality of categorical features\n\n" + card.to_frame("distinct_values").to_markdown() + "\n")
    card.plot.bar(figsize=(10, 3.5), logy=True, color="#2a4a7f", title="Distinct values per categorical feature (log scale)")
    plt.tight_layout(); plt.savefig(FIGURES / "cardinality.png", dpi=120); plt.close()

    # 4. CTR vs numeric feature (binned) — does the feature carry signal?
    fig, axes = plt.subplots(1, 4, figsize=(15, 3.5))
    for ax, c in zip(axes, ["i1", "i5", "i6", "i11"]):
        bins = pd.qcut(df[c], 8, duplicates="drop")
        ctr = df.groupby(bins, observed=True)[LABEL].mean()
        ctr.plot(ax=ax, marker="o", color="#2a4a7f"); ax.set_title(f"CTR by {c} octile"); ax.tick_params(axis="x", rotation=60, labelsize=7)
    plt.tight_layout(); plt.savefig(FIGURES / "ctr_by_numeric.png", dpi=120); plt.close()

    # 5. CTR drift over time (file is chronological)
    decile = pd.qcut(np.arange(len(df)), 10, labels=False)
    drift = df.groupby(decile)[LABEL].mean()
    md.append("## CTR by time decile (rows are chronological)\n\n" + drift.to_frame("ctr").round(3).to_markdown() + "\n")
    drift.plot(marker="o", figsize=(6, 3), color="#2a4a7f", title="CTR by time decile"); plt.ylim(0, 0.4)
    plt.tight_layout(); plt.savefig(FIGURES / "ctr_drift.png", dpi=120); plt.close()

    (REPORTS / "eda.md").write_text("\n".join(md))
    print("\n".join(md))
    print(f"figures -> {FIGURES}")


if __name__ == "__main__":
    main()

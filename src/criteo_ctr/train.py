"""Train and evaluate CTR models -> reports/metrics.md + reports/figures/calibration.png.

Models, in order of complexity:
1. Constant baseline  (predict the train CTR for everyone)      -> floor for log-loss
2. Logistic regression on hashed one-hot + log numerics          -> classic CTR model
3. LightGBM on raw numerics + categoricals                        -> gradient boosting
"""
import time

import matplotlib

matplotlib.use("Agg")
import lightgbm as lgb
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.calibration import calibration_curve
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score

from .config import FIGURES, REPORTS, SEED
from .features import (
    fit_rare_maps, labels, make_linear_features, make_tree_features, time_split,
)
from .io import load_raw


def evaluate(name: str, y_true, p, seconds: float) -> dict:
    return {
        "model": name,
        "log_loss": round(log_loss(y_true, p), 4),
        "auc": round(roc_auc_score(y_true, p), 4),
        "train_time_s": round(seconds, 1),
    }


def main() -> None:
    df = load_raw()
    train, test = time_split(df)
    y_tr, y_te = labels(train), labels(test)
    results, preds = [], {}

    # 1. Constant baseline
    p0 = np.full(len(test), y_tr.mean())
    results.append(evaluate("constant (train CTR)", y_te, p0, 0))

    # 2. Logistic regression
    t = time.time()
    X_tr, X_te = make_linear_features(train), make_linear_features(test)
    lr = LogisticRegression(C=0.5, max_iter=1000, solver="liblinear", random_state=SEED)
    lr.fit(X_tr, y_tr)
    preds["logreg"] = lr.predict_proba(X_te)[:, 1]
    results.append(evaluate("logistic regression (hashed one-hot)", y_te, preds["logreg"], time.time() - t))

    # 3. LightGBM
    t = time.time()
    keep = fit_rare_maps(train)
    T_tr, T_te = make_tree_features(train, keep), make_tree_features(test, keep)
    gbm = lgb.LGBMClassifier(
        n_estimators=400, learning_rate=0.05, num_leaves=63, min_child_samples=50,
        subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=SEED, verbose=-1,
    )
    gbm.fit(T_tr, y_tr, categorical_feature=[c for c in T_tr.columns if str(T_tr[c].dtype) == "category"])
    preds["lightgbm"] = gbm.predict_proba(T_te)[:, 1]
    results.append(evaluate("LightGBM (categorical)", y_te, preds["lightgbm"], time.time() - t))

    # Report
    table = pd.DataFrame(results)
    md = ["# Model results (time-based split, last 20% of rows = test)\n", table.to_markdown(index=False), ""]
    imp = pd.Series(gbm.feature_importances_, index=T_tr.columns).sort_values(ascending=False).head(10)
    md.append("## LightGBM top-10 features by split count\n\n" + imp.to_frame("importance").to_markdown() + "\n")
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "metrics.md").write_text("\n".join(md))
    print("\n".join(md))

    # Calibration: in advertising the *probability* is used for bidding, so a
    # well-calibrated model matters as much as a high AUC.
    FIGURES.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(5, 5))
    for name, p in preds.items():
        frac, mean_p = calibration_curve(y_te, p, n_bins=10)
        plt.plot(mean_p, frac, marker="o", label=name)
    plt.plot([0, 1], [0, 1], "k--", lw=1, label="perfect")
    plt.xlabel("predicted probability"); plt.ylabel("observed click rate"); plt.title("Calibration")
    plt.legend(); plt.tight_layout(); plt.savefig(FIGURES / "calibration.png", dpi=120); plt.close()


if __name__ == "__main__":
    main()

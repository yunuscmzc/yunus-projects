#!/usr/bin/env python3
"""
Replication of MINIROCKET accuracy benchmark from:
Dempster, Schmidt & Webb (2021), KDD, pp. 248-257.

Usage:
    python src/replicate.py
"""

import os
import sys
import time
import json
import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from minirocket import MiniRocketClassifier

SEED = 2021402078
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
DATA_DIR    = os.path.join(BASE_DIR, "..", "data", "UCR")
RESULTS_DIR = os.path.join(BASE_DIR, "..", "results")

PAPER_RESULTS = {
    "ItalyPowerDemand": 0.9718,
    "SyntheticControl": 0.9933,
    "Wafer":            0.9996,
    "FaceAll":          0.8337,
    "ECG200":           0.8900,
    "Plane":            1.0000,
    "Beef":             0.7667,
    "Coffee":           1.0000,
    "OliveOil":         0.8667,
    "Trace":            1.0000,
}


def load_ucr_dataset(name):
    base = os.path.join(DATA_DIR, name)
    for suffix_train, suffix_test in [
        (f"{name}_TRAIN.tsv", f"{name}_TEST.tsv"),
        (f"{name}_TRAIN.txt", f"{name}_TEST.txt"),
    ]:
        train_path = os.path.join(base, suffix_train)
        test_path  = os.path.join(base, suffix_test)
        if os.path.exists(train_path) and os.path.exists(test_path):
            break
    else:
        raise FileNotFoundError(f"Cannot find files for '{name}' in {base}. Run: python data/download_data.py")

    def _read(path):
        delimiter = "\t" if path.endswith(".tsv") else None
        data = np.loadtxt(path, delimiter=delimiter)
        y = data[:, 0].astype(int)
        X = np.nan_to_num(data[:, 1:].astype(np.float32), nan=0.0)
        return X, y

    return *_read(train_path), *_read(test_path)


def run_dataset(name):
    print(f"\n  {name}")
    try:
        X_train, y_train, X_test, y_test = load_ucr_dataset(name)
    except FileNotFoundError as e:
        print(f"    [SKIP] {e}")
        return None

    n_train, n_timepoints = X_train.shape
    n_test    = X_test.shape[0]
    n_classes = len(np.unique(y_train))
    print(f"    train={n_train}, test={n_test}, length={n_timepoints}, classes={n_classes}")

    clf = MiniRocketClassifier(num_features=9_996, random_state=SEED)

    t0      = time.perf_counter()
    clf.fit(X_train, y_train)
    t_train = time.perf_counter() - t0

    t0     = time.perf_counter()
    acc    = clf.score(X_test, y_test)
    t_test = time.perf_counter() - t0

    paper_acc = PAPER_RESULTS.get(name)
    diff      = round(acc - paper_acc, 4) if paper_acc is not None else None

    print(f"    accuracy={acc:.4f}  paper={paper_acc}  diff={diff:+.4f}" if diff is not None else f"    accuracy={acc:.4f}")
    print(f"    train_time={t_train:.2f}s  test_time={t_test:.2f}s")

    return {
        "dataset":        name,
        "n_train":        n_train,
        "n_test":         n_test,
        "n_timepoints":   n_timepoints,
        "n_classes":      n_classes,
        "our_accuracy":   round(float(acc), 4),
        "paper_accuracy": paper_acc,
        "difference":     diff,
        "train_time_s":   round(t_train, 3),
        "test_time_s":    round(t_test, 3),
    }


def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)

    datasets = list(PAPER_RESULTS.keys())
    print("=" * 60)
    print("MINIROCKET Replication — Dempster et al. (2021)")
    print(f"Seed: {SEED}  |  Datasets: {len(datasets)}")
    print("=" * 60)

    rows = [r for name in datasets if (r := run_dataset(name)) is not None]

    if not rows:
        print("\n[ERROR] No datasets loaded. Run: python data/download_data.py")
        sys.exit(1)

    df = pd.DataFrame(rows).set_index("dataset")
    print("\n" + "=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(df[["our_accuracy", "paper_accuracy", "difference", "train_time_s"]].to_string())

    valid = df.dropna(subset=["paper_accuracy"])
    if len(valid) > 0:
        print(f"\nMean — Ours: {valid['our_accuracy'].mean():.4f} | Paper: {valid['paper_accuracy'].mean():.4f} | Diff: {valid['difference'].mean():+.4f}")
        print(f"Datasets where our acc >= paper: {(valid['difference'] >= 0).sum()}/{len(valid)}")

    out_csv  = os.path.join(RESULTS_DIR, "replication_results.csv")
    out_json = os.path.join(RESULTS_DIR, "replication_results.json")
    df.reset_index().to_csv(out_csv, index=False)
    with open(out_json, "w") as f:
        json.dump(rows, f, indent=2)

    print(f"\nResults saved to:\n  {out_csv}\n  {out_json}")
    print("\nDone.")


if __name__ == "__main__":
    main()

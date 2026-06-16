# Real-Time Soccer Event Prediction with Statistical Process Control

An **online (minute-by-minute) Statistical Process Control system** that monitors a live soccer match and issues early warnings predicting upcoming **goals** and **red cards** — *before* they occur. Built under strict real-time constraints: at every minute, decisions use only the information available up to that minute (no future-data leakage).

The system is scored on **predictive timing** — a warning issued shortly before an event scores high, while false alarms and warning-spam are heavily penalized — so the design centers on issuing *confident, well-timed* warnings rather than many of them.

## Method

The core is a custom **EWMA–CUSUM hybrid control chart** that updates incrementally for each match:

- **EWMA baseline** — an exponentially weighted moving average tracks the adaptive mean and variance of each monitored signal, so the "in-control" baseline evolves with the match.
- **CUSUM detector** — accumulates standardized deviations above a reference slack `k`, making it sensitive to subtle, sustained shifts in match dynamics that precede an event.

### Signal Engineering
Raw match variables are cumulative (and therefore non-stationary), so they are transformed into per-minute **deltas** and combined into rolling-window signals:

| Signal | Captures | Built from |
|--------|----------|-----------|
| **X** | Overall attacking intensity | Attacks + (weighted) dangerous attacks |
| **Y** | Home/away imbalance | Normalized differences in attack pressure |
| **Z** | Directional scoring threat | Key passes, corners, shots on target (per side) |
| **PEN** | Immediate red-card/goal risk | Penalty events |

### False-Alarm Control
To avoid the heavy penalty for warning-spam, the trigger logic includes:
- a **warmup period** before any warning can fire (stabilizes early-match estimates),
- a **cooldown** window after each warning,
- an **arm / re-arm gate** — once a warning fires the system disarms, and only re-arms after signals fall back below relaxed thresholds.

## Design Constraints
- **No data leakage** — all control limits and baselines are computed online, using only observations up to the current minute.
- **Generalization** — the algorithm is fully parametric with no hardcoded match-specific values, so it runs on unseen matches.
- **Course-bounded toolbox** — only SPC methods (Shewhart/EWMA/CUSUM-style charts and rule-based logic) are used.

## Files

| File | Description |
|------|-------------|
| `prediction.py` | The online predictor: per-match state, EWMA–CUSUM charts, signal transformations, and the arm/cooldown warning policy. The `predict()` function is called once per minute and returns `1` (warning) or `0`. |

## Tech Stack

- **Python** — NumPy, pandas

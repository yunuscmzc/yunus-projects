# Replicate a Result — MINIROCKET

**IE 48B: Special Topics in Time Series Analytics**  
Boğaziçi University — Spring 2026  
Student ID: `2021402078` (used as random seed throughout)

---

## Paper

> Dempster, A., Schmidt, D. F., & Webb, G. I. (2021).  
> **MiniRocket: A Very Fast (Almost) Deterministic Transform for Time Series Classification.**  
> *KDD '21: Proceedings of the 27th ACM SIGKDD Conference*, pp. 248–257.  
> https://doi.org/10.1145/3447548.3467231

**arXiv preprint:** https://arxiv.org/abs/2012.08791  
**Official code:** https://github.com/angus924/minirocket

---

## What Was Replicated

**Target result:** Classification accuracy on 10 representative UCR Time Series Archive datasets,
compared against the paper's reported benchmark numbers (official results repository).

The implementation is from scratch — the official code was not consulted.

---

## Repository Structure

```
replicate-result/
├── README.md
├── requirements.txt          # Pinned dependencies
├── src/
│   ├── minirocket.py         # From-scratch MINIROCKET implementation
│   └── replicate.py          # Main replication script
├── data/
│   ├── download_data.py      # Downloads UCR datasets automatically
│   └── UCR/                  # Dataset files (created by download_data.py)
├── results/
│   ├── replication_results.csv
│   └── replication_results.json
├── report/
│   ├── summary.qmd           # Quarto source
│   └── summary.html          # Rendered HTML report
└── presentation/
    └── slides.pdf            # Presentation slides (due May 18)
```

---

## Setup & Reproduction

### Requirements
- Python 3.10+
- pip

### Step-by-step

```bash
# 1. Clone the repository
git clone https://github.com/yunuscmzc/yunus-projects.git
cd yunus-projects/MINIROCKET_Replicate_Result

# 2. Install pinned dependencies
pip install -r requirements.txt

# 3. Download UCR datasets
python data/download_data.py

# 4. Run the replication
python src/replicate.py
```

Results are printed to stdout and saved to:
- `results/replication_results.csv`
- `results/replication_results.json`

---

## Key Design Choices

| Choice | Detail |
|--------|--------|
| **Kernels** | 84 fixed kernels, length 9, weights ∈ {−1, +2}, all C(9,3) = 84 combinations of 3 positions with weight +2 |
| **Dilations** | Log-uniformly sampled: d = ⌊2^u⌋, u ~ Uniform(0, log₂(max_d + 1)) |
| **Biases** | Quantile points of convolution outputs on a random subsample of training data |
| **Pooling** | PPV (Proportion of Positive Values) — only pooling operator used |
| **Features** | 9,996 ≈ 10,000 (84 kernels × 119 features per kernel, rounded to multiple of 84) |
| **Classifier** | RidgeClassifierCV, α ∈ [10⁻³, 10³] |
| **Seed** | `2021402078` — controls dilation sampling and bias estimation |

---

## Results Summary

| Dataset | Paper | Ours | Diff |
|---------|-------|------|------|
| ItalyPowerDemand | 0.9718 | 0.9631 | −0.0087 |
| SyntheticControl | 0.9933 | 0.9800 | −0.0133 |
| Wafer | 0.9996 | 0.9976 | −0.0020 |
| FaceAll | 0.8337 | 0.7876 | −0.0461 |
| ECG200 | 0.8900 | 0.9200 | +0.0300 |
| Plane | 1.0000 | 1.0000 | 0.0000 |
| Beef | 0.7667 | 0.8333 | +0.0666 |
| Coffee | 1.0000 | 1.0000 | 0.0000 |
| OliveOil | 0.8667 | 0.9333 | +0.0666 |
| Trace | 1.0000 | 1.0000 | 0.0000 |
| **Mean** | **0.9322** | **0.9415** | **+0.0093** |

See `report/summary.html` for full critical analysis of discrepancies.

---

## Citation

```bibtex
@inproceedings{dempster_etal_2021,
  author    = {Dempster, Angus and Schmidt, Daniel F and Webb, Geoffrey I},
  title     = {{MiniRocket}: A Very Fast (Almost) Deterministic Transform for Time Series Classification},
  booktitle = {Proceedings of the 27th ACM SIGKDD Conference on Knowledge Discovery and Data Mining},
  publisher = {ACM},
  address   = {New York},
  year      = {2021},
  pages     = {248--257},
  doi       = {10.1145/3447548.3467211}
}
```

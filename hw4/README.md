# IE 48B — Homework 4: Neural Nets and Additive Modules

**Student:** Yunus Emre Camızcı | **ID:** 2021402078  
**Course:** Special Topics in Time Series Analytics, Spring 2026  
**Due:** May 25, 2026, 23:59

---

## Overview

This homework builds on HW3 by replacing the GAM with neural models for hourly Turkish solar generation forecasting. Three neural architectures are trained and compared against the HW3 baselines:

- **MLP** — standard multi-layer perceptron (black-box)
- **NAM** — Neural Additive Model with one subnet per feature (interpretable)
- **NAM + Interaction** — NAM extended with an ExNN-style hour × shortwave radiation subnet

---

## Repository Structure

```
hw4/
├── HW4_NeuralNets_AdditiveModules.qmd   # source notebook
├── HW4_NeuralNets_AdditiveModules.html  # rendered output (submit this)
├── data/
│   └── solar_dataset.csv                # hourly solar + weather, Jan 2022 - Mar 2026
├── models/
│   ├── mlp_state_dict.pt                # saved MLP weights (best seed)
│   └── nam_state_dict.pt                # saved NAM weights (best seed)
└── requirements.txt
```

---

## Data

`data/solar_dataset.csv` contains 37,224 hourly observations (January 2022 through March 2026) with the target variable `solar_mwh` and weather predictors from three Turkish locations (Konya, Gaziantep, Izmir) sourced from the Open-Meteo Historical Weather API. This is identical to the HW3 dataset.

**Train/test split:**
- Train: before 2026-01-01 (35,064 observations)
- Test: January 1 to March 31, 2026 (2,160 observations)

---

## How to Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Render the notebook (this also trains all models, takes 10-20 minutes on CPU):

```bash
quarto render HW4_NeuralNets_AdditiveModules.qmd
```

---

## Reproducibility

All random seeds are set to `STUDENT_ID % 2**31 = 2021402078`. Each model is trained three times with sub-seeds `[2021402078, 2021402079, 2021402080]` and test RMSE is reported as mean ± std.

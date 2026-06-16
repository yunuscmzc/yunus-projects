# Solar Power Forecasting with Neural Networks and Additive Modules

Hourly Turkish solar generation forecasting using three neural architectures, benchmarked against a GAM baseline. The dataset contains 37,224 hourly observations (January 2022 – March 2026) with weather predictors from Konya, Gaziantep, and Izmir.

## Models

| Model | Description |
|-------|-------------|
| **MLP** | Standard multi-layer perceptron (black-box) |
| **NAM** | Neural Additive Model — one subnet per feature (interpretable) |
| **NAM + Interaction** | NAM extended with an ExNN-style hour × shortwave radiation subnet |

## Repository Structure

```
NeuralNets_AdditiveModules/
├── NeuralNets_AdditiveModules.qmd   # source notebook
├── NeuralNets_AdditiveModules.html  # rendered report
├── data/
│   └── solar_dataset.csv            # 37,224 hourly observations
├── models/
│   ├── mlp_state_dict.pt            # saved MLP weights
│   └── nam_state_dict.pt            # saved NAM weights
└── requirements.txt
```

## Train/Test Split

- **Train:** before 2026-01-01 (35,064 observations)
- **Test:** January 1 – March 31, 2026 (2,160 observations)

## Setup

```bash
pip install -r requirements.txt
```

## Usage

Render the notebook (trains all models — ~10–20 min on CPU):

```bash
quarto render NeuralNets_AdditiveModules.qmd
```

## Reproducibility

Each model is trained three times with consecutive seeds and test RMSE is reported as mean ± std.

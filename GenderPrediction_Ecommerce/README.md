# E-commerce User Gender Prediction

A machine-learning model that predicts the **gender of e-commerce users** from their browsing and shopping behavior on a Turkish online marketplace. Built for a competition where submissions were scored on classification performance (the model outputs a `probability_female` for each user).

The model reached **~0.89 AUC** in cross-validation.

## Approach

The core of the project is **heavy feature engineering** from raw user-interaction logs, feeding an **XGBoost** classifier.

### Feature Engineering
- **Action scoring** — user actions (`visit`, `search`, `favorite`, `basket`, `order`) are weighted by purchase intent, and per-user action ratios are computed.
- **Product-gender signals** — counts and ratios of female / male / unisex products each user interacted with.
- **Brand-gender profiling** — brands whose user base is ≥90% female or ≥80% male are identified from the training data, then used to score each user's brand affinity (weighted by action intent).
- **Keyword detection** — a data-driven word-extraction routine surfaces the most gender-discriminative words in Turkish product names; these were curated into male/female keyword lists and used to tag products.
- **Category diversity** — measures how broadly a user shops across female-tagged vs. male-tagged product categories.

### Modeling
- **XGBoost** binary classifier with `scale_pos_weight` to handle class imbalance.
- **Optuna** (TPE sampler) hyperparameter search over depth, learning rate, regularization, and sampling parameters, optimizing 5-fold cross-validated AUC.

## Files

| File | Description |
|------|-------------|
| `prediction.py` | Full pipeline — feature engineering, model training, and prediction. |
| `test_prediction.csv` | Sample output: per-user female probability and predicted gender. |

> **Note:** The competition training/test data (`IE425_Spring25_train_data.csv`, `IE425_Spring25_test_data.csv`) is not included as it is competition-provided data. The script expects these files in the working directory.

## Attribution

This was a **two-person collaboration**. My partner and I worked jointly on every part of the project — feature engineering, modeling, keyword curation, and analysis — rather than splitting it into separate pieces.

## Setup

```bash
pip install pandas numpy scikit-learn xgboost optuna
```

## Usage

```bash
python prediction.py
```

Produces `test_prediction.csv` with predicted gender and female-probability for each user.

## Tech Stack

- **Python** — pandas, NumPy, scikit-learn, XGBoost, Optuna

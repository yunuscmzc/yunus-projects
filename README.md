# Yunus Emre Camızcı — Data Science Projects

A collection of machine learning and time series projects covering forecasting, classification, predictive modeling, and paper replication.

---

## Projects

### [Time Domain & Frequency Analysis](./TimeDomainFrequency/)
Analyzes the Coffee dataset using time-domain statistics and spectral analysis. Implements a nearest-centroid classifier built on dominant frequency, spectral concentration, peak power, and short-lag autocorrelation features. Includes controlled noise injection experiments to assess spectral robustness.

**Tools:** Python, Quarto, NumPy, SciPy

---

### [Time Series Representations, Similarity & Classification](./RepresentationsSimilarityClassification/)
Explores PAA and SAX representations alongside Euclidean and DTW distance measures for time series classification. Benchmarks k-NN classifiers on the Coffee dataset and extends to multivariate gesture recognition with UWaveGestureLibrary.

**Tools:** Python, Quarto, tslearn, scikit-learn

---

### [Solar Power Forecasting with GAMs](./GAMs_SolarForecasting/)
Forecasts hourly solar generation in Turkey using Generalized Additive Models with spline terms and interaction effects. Uses 4+ years of weather data (shortwave radiation, temperature, cloud cover) from three locations via the Open-Meteo API.

**Tools:** Python, Quarto, pygam, pandas, matplotlib

---

### [Solar Power Forecasting with Neural Networks](./NeuralNets_AdditiveModules/)
Compares three neural architectures for solar generation forecasting: a standard MLP, a Neural Additive Model (NAM), and a NAM extended with an ExNN-style interaction subnet. Benchmarked against the GAM baseline above.

**Tools:** Python, Quarto, PyTorch, pandas, scikit-learn

---

### [Live Next-Day Solar Forecasting](./SolarForecasting_LiveCompetition/)
A real-time forecasting pipeline for a live competition: pulls fresh weather forecasts from the Open-Meteo API for 5 Turkish solar plants, engineers cyclical and interaction features, fits an OLS regression, and predicts the next 24 hours of solar production. Submitted and scored daily against actual measurements.

**Tools:** Python, R, statsmodels, pandas, Open-Meteo API

---

### [MINIROCKET Replication](./MINIROCKET_Replicate_Result/)
From-scratch replication of the MINIROCKET paper (Dempster et al., KDD 2021) — a fast, near-deterministic transform for time series classification. Evaluated on 10 UCR datasets; mean accuracy matched or exceeded the paper's reported results (+0.009 mean improvement).

**Tools:** Python, NumPy, scikit-learn, Quarto

---

### [E-commerce User Gender Prediction](./GenderPrediction_Ecommerce/)
Predicts the gender of e-commerce users from their browsing and shopping behavior. Combines extensive behavioral feature engineering (action scoring, brand-gender profiling, Turkish product-name keyword detection, category diversity) with an Optuna-tuned XGBoost classifier, reaching ~0.89 AUC. *(Two-person collaboration.)*

**Tools:** Python, XGBoost, Optuna, scikit-learn, pandas

---

## Tech Stack

- **Languages:** Python, R
- **Notebooks:** Quarto (`.qmd` → rendered `.html`)
- **ML / Stats:** PyTorch, XGBoost, scikit-learn, statsmodels, Optuna, pygam, tslearn, SciPy
- **Data:** UCR Time Series Archive, Open-Meteo API, EPIAS (Turkish electricity market)

# Time Series Representations, Similarity, and Classification

Analysis of time series classification using dimensionality reduction, distance measures, and k-NN classifiers. Applied to the **Coffee** dataset (2 classes, 28 train / 28 test, length 286) and the multivariate **UWaveGestureLibrary** dataset.

## Topics Covered

- Time series representations: PAA (Piecewise Aggregate Approximation) and SAX (Symbolic Aggregate approXimation)
- Distance measures: Euclidean and DTW (Dynamic Time Warping)
- Classification benchmarking and noise robustness analysis
- Multivariate k-NN classification on gesture recognition data

## Setup

```bash
pip install -r requirements.txt
```

## Usage

Render the full analysis report:

```bash
quarto render RepresentationsSimilarityClassification.qmd
```

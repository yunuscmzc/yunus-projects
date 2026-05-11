"""
MINIROCKET: A Very Fast (Almost) Deterministic Transform for Time Series Classification
Replication of: Dempster, Schmidt & Webb (2021), KDD, pp. 248-257.
Student ID (seed): 2021402078
"""

import numpy as np
from numba import njit, prange
from sklearn.linear_model import RidgeClassifierCV

NUM_KERNELS = 84
KERNEL_LENGTH = 9


def _get_kernel_weights():
    from itertools import combinations
    kernels = np.full((NUM_KERNELS, KERNEL_LENGTH), -1, dtype=np.float32)
    for i, positions in enumerate(combinations(range(KERNEL_LENGTH), 3)):
        for p in positions:
            kernels[i, p] = 2.0
    return kernels


KERNELS = _get_kernel_weights()


@njit(fastmath=True, parallel=True)
def _transform(X, kernels, dilations, biases, num_features_per_kernel):
    n_samples, n_timepoints = X.shape
    n_kernels = kernels.shape[0]
    n_features = n_kernels * num_features_per_kernel
    features = np.zeros((n_samples, n_features), dtype=np.float32)

    for i in prange(n_samples):
        x = X[i]
        f_idx = 0
        for k in range(n_kernels):
            kernel = kernels[k]
            dilation = dilations[k]

            output = np.empty(n_timepoints, dtype=np.float32)
            for t in range(n_timepoints):
                val = 0.0
                for j in range(KERNEL_LENGTH):
                    t_idx = t + (j - KERNEL_LENGTH // 2) * dilation
                    if 0 <= t_idx < n_timepoints:
                        val += kernel[j] * x[t_idx]
                output[t] = val

            for b_idx in range(num_features_per_kernel):
                bias = biases[f_idx]
                ppv = 0.0
                for t in range(n_timepoints):
                    if output[t] > bias:
                        ppv += 1.0
                ppv /= n_timepoints
                features[i, f_idx] = ppv
                f_idx += 1

    return features


class MiniRocketTransform:
    def __init__(self, num_features=9_996, random_state=2021402078):
        self.num_features = (num_features // NUM_KERNELS) * NUM_KERNELS
        self.num_features_per_kernel = self.num_features // NUM_KERNELS
        self.random_state = random_state
        self._fitted = False

    def fit(self, X):
        X = np.asarray(X, dtype=np.float32)
        n_samples, n_timepoints = X.shape
        rng = np.random.default_rng(self.random_state)

        max_dilation = max((n_timepoints - 1) // (KERNEL_LENGTH - 1), 1)
        log2_max = np.log2(max_dilation + 1)
        dilations = np.floor(
            2 ** rng.uniform(0, log2_max, size=NUM_KERNELS)
        ).astype(np.int32)
        dilations = np.clip(dilations, 1, max_dilation)

        biases = np.empty(self.num_features, dtype=np.float32)
        idx = 0
        for k in range(NUM_KERNELS):
            kernel = KERNELS[k]
            dilation = int(dilations[k])
            n_sub = min(n_samples, 100)
            sub_idx = rng.choice(n_samples, size=n_sub, replace=False)
            outputs = []
            for i in sub_idx:
                x = X[i]
                out = np.zeros(n_timepoints, dtype=np.float32)
                for t in range(n_timepoints):
                    val = np.float32(0.0)
                    for j in range(KERNEL_LENGTH):
                        t_idx = t + (j - KERNEL_LENGTH // 2) * dilation
                        if 0 <= t_idx < n_timepoints:
                            val += kernel[j] * x[t_idx]
                    out[t] = val
                outputs.append(out)
            outputs = np.concatenate(outputs)
            quantiles = np.linspace(0, 100, self.num_features_per_kernel + 2)[1:-1]
            bias_vals = np.percentile(outputs, quantiles).astype(np.float32)
            biases[idx: idx + self.num_features_per_kernel] = bias_vals
            idx += self.num_features_per_kernel

        self.dilations_ = dilations
        self.biases_ = biases
        self._fitted = True
        return self

    def transform(self, X):
        if not self._fitted:
            raise RuntimeError("Call fit() before transform().")
        X = np.asarray(X, dtype=np.float32)
        return _transform(X, KERNELS, self.dilations_, self.biases_, self.num_features_per_kernel)

    def fit_transform(self, X):
        return self.fit(X).transform(X)


class MiniRocketClassifier:
    def __init__(self, num_features=9_996, random_state=2021402078):
        self.num_features = num_features
        self.random_state = random_state
        self.transform_ = MiniRocketTransform(num_features=num_features, random_state=random_state)
        self.classifier_ = RidgeClassifierCV(alphas=np.logspace(-3, 3, 10))

    def fit(self, X_train, y_train):
        X_tr = self.transform_.fit_transform(X_train)
        self.classifier_.fit(X_tr, y_train)
        return self

    def predict(self, X_test):
        X_te = self.transform_.transform(X_test)
        return self.classifier_.predict(X_te)

    def score(self, X_test, y_test):
        return np.mean(self.predict(X_test) == y_test)

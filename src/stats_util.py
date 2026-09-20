import numpy as np
from scipy import stats as sps

Z = 1.959963984540054

def wilson(k, n, z=Z):
    if n == 0:
        return (np.nan, np.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * np.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - h, c + h)

def newcombe_diff(k1, n1, k2, n2, z=Z):
    """CI for p1 - p2 (Newcombe method 10)."""
    if n1 == 0 or n2 == 0:
        return (np.nan, np.nan)
    p1, p2 = k1 / n1, k2 / n2
    l1, u1 = wilson(k1, n1, z)
    l2, u2 = wilson(k2, n2, z)
    lo = (p1 - p2) - np.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2)
    hi = (p1 - p2) + np.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)
    return (lo, hi)

def two_prop_test(k1, n1, k2, n2):
    if n1 == 0 or n2 == 0:
        return np.nan, np.nan
    tbl = [[k1, n1 - k1], [k2, n2 - k2]]
    try:
        _, p = sps.fisher_exact(tbl)
    except Exception:
        p = np.nan
    # Cohen's h effect size
    p1, p2 = k1 / n1, k2 / n2
    h = 2 * np.arcsin(np.sqrt(p1)) - 2 * np.arcsin(np.sqrt(p2))
    return p, h

def binom_p(k, n, p0):
    if n == 0:
        return np.nan
    return sps.binomtest(int(k), int(n), p0).pvalue

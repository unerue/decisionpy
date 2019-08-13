import numpy as np
import pandas as pd
from scipy.stats import gmean


class AnalyticHierarchyProcess:
    """Analytic Hierarchy Process
    
    Parameters:
    -----------

    Returns:
    --------

    
    """
    def __init__(self, inputs):
        self.random_indices = [0, 0, 0.58, 0.90, 1.12, 1.24, 1.32, 1.41, 1.45, 1.49]
        self.inputs = inputs
        self.num_criteria = 4

    def noramlize(self, x):
        return x / x.sum(0)

    def geo_mean(self, x):
        return gmean(x, axis=1)

    def _check_consistency(self, x):
        l = np.max(np.linalg.eigvals(x).real)
        CI = (l - self.num_criteria) / (self.num_criteria - 1)
        CR = CI / RI[self.num_criteria - 1]
        return CI, CR

    def solve(self):
        pass

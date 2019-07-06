import pandas as pd
import numpy as np
import numba
import time
from pulp import *
from utils import _check_datatype


class DataEnvelopmentAnalysis:
    """DataEnvelopmentAnalysis

    A container for the elements of a data envelopment analysis. Sets
    up the linear programmes and solves them with pulp.

    Parameters:
    -----------
    returns : return to scale 'CCR', 'BCC', or 'AR'
    inputs : a pandas dataframe of the inputs to the DMUs
             ----------------------------
             | DMUs | Input 1 | Input 2 |
             ----------------------------
             | DMU1 |     20  |     30  |
             | DMU2 |     25  |     27  |
             ----------------------------
    outputs : a pandas dataframe of the outputs from the DMUs
    in_weights : the weight restriction to apply to all inputs to all DMUs
                (default is [0, inf])
    out_weights : the weight restriction to apply to all outputs to all DMUs
                    (default is [0, inf)
    Weight restrictions must be specified as a list. To specify only one bound
    leave the other as None, eg. in_weights=[1, None].

    Returns:
    --------

    """
    def __init__(self, returns='CCR', inputs, outputs,
                 in_weights=[0, None], out_weights=[0, None]):
        """
        Set up the DMUs' problems, ready to solve.

        """
        self.returns = returns
        self.inputs = _check_datatype(inputs)
        self.outputs = _check_datatype(outputs)

        self.num_alters = self.inputs.shape[0]
        self.num_inputs = self.inputs.shape[1]
        self.num_outputs = self.outputs.shape[1]

        self.in_weights = in_weights
        self.out_weights = out_weights

        self.J, self.I = self.inputs.shape  # no of firms, inputs
        _, self.R = self.outputs.shape  # no of outputs
        self._i = range(self.I)  # inputs
        self._r = range(self.R)  # outputs
        self._j = range(self.J)  # DMUs

        self._in_weights = in_weights  # input weight restrictions
        self._out_weights = out_weights  # output weight restrictions

        # creates dictionary of pulp.LpProblem objects for the DMUs
        self.dmus = self._create_problems()

    def _create_problems(self):
        problems = {}
        for alter in range(self.num_alters):
            problems[alter] = self._create_problem(alter)
        return problems

    def _create_problem(self, alter):
        # Set up pulp
        prob = LpProblem('DMU{}'.format(alter), LpMaximize)
        self.input_weights = LpVariable.dicts('input_weights', (range(self.num_alters), range(self.num_inputs)),
                                                                lowBound=self.in_weights[0], upBound=self.in_weights[1])
        self.output_weights = LpVariable.dicts('output_weights', (range(self.num_alters), range(self.num_outputs)),
                                                   lowBound=self.out_weights[0], upBound=self.out_weights[1])

        # Set returns to scale
        if self.returns == 'CCR':
            w = 0
        elif self.returns == 'BCC':
            w = LpVariable.dicts("w", (self._j, self._r))
        elif self.returns == 'AR':
            pass
        else:
            raise Exception(ValueError)

        # Set up objective function
        prob += LpAffineExpression(
            [(self.outputWeights[j0][r1], self.outputs.values[j0][r1]) for r1 in self._r]) - w

        # Set up constraints
        prob += LpAffineExpression([(self.input_weights[j0][i1],
                                          self.inputs.values[j0][i1]) for i1 in self._i]) == 1, "Norm_constraint"
        for alter in range(self.num_alters):
            prob += self._dmu_constraint(j0, j1) - \
                w <= 0, ''.join(['DMU_constraint_', str(j1)])
        return prob

    def _constraints(self, j0, j1):
        """
        Calculate and return the DMU constraint for a single DMU's LP problem.

        """

        eOut = LpAffineExpression(
            [(self.outputWeights[j0][r1], self.outputs.values[j1][r1]) for r1 in self._r])
        eIn = LpAffineExpression(
            [(self.inputWeights[j0][i1], self.inputs.values[j1][i1]) for i1 in self._i])
        return eOut - eIn

    def solve(self):
        pass
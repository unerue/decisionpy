import pandas as pd
import numpy as np
import numba
import time
from pulp import *


class DataEnvelopmentAnalysis:
    """Data Envelopment Analysis

    A container for the elements of a data envelopment analysis. Sets
    up the linear programmes and solves them with pulp.

    Parameters:
    -----------
    inputs : a pandas dataframe of the inputs to the DMUs
            ----------------------------
            | DMUs | Input 1 | Input 2 |
            ----------------------------
            | DMU1 |     20  |     30  |
            | DMU2 |     25  |     27  |
            ----------------------------
    outputs : a pandas dataframe of the outputs from the DMUs
            ------------------------------
            | DMUs | Output 1 | Output 2 |
            ------------------------------
            | DMU1 |     20   |      30  |
            | DMU2 |     25   |      27  |
            ------------------------------

    Returns:
    --------
    efficiency : result
    """
    def __init__(self, inputs, outputs):
        self.inputs = inputs
        self.outputs = outputs
        
        self.num_dmus = len(inputs)
        self.num_inputs = inputs.shape[1]
        self.num_outputs = outputs.shape[1]

        self.weights = {}
        self.efficiency = {}
    
    def _generate_problems(self):
        return {k: self._create_problem(v) for k, v in enumerate(range(self.num_dmus))}
    
    def _create_problem(self, dmu):
        prob = LpProblem('DMU{}'.format(dmu), LpMaximize)
        input_weights = LpVariable.dicts('input_weights', (range(self.num_dmus), range(self.num_inputs)),
                                         lowBound=0)
        output_weights = LpVariable.dicts('output_weights', (range(self.num_dmus), range(self.num_outputs)),
                                         lowBound=0)
        weight = 0
        
        prob += LpAffineExpression([(output_weights[dmu][i], self.outputs.iloc[dmu, i]) for i in range(self.num_outputs)]) - weight
        prob += LpAffineExpression([(input_weights[dmu][i], self.inputs.iloc[dmu, i]) for i in range(self.num_inputs)]) == 1
        
        for i in range(self.num_dmus):
            prob += self._constraint(dmu, i, input_weights, output_weights) - weight <= 0
        
        return prob
    
    def _constraint(self, dmu, i, input_weights, output_weights):
        e_output = LpAffineExpression([(output_weights[dmu][j], self.outputs.iloc[i,j]) for j in range(self.num_outputs)])
        e_input = LpAffineExpression([(input_weights[dmu][j], self.inputs.iloc[i,j]) for j in range(self.num_inputs)])

        return e_output - e_input
    
    def solve(self):
        print('Generating problems...')
        problems = self._generate_problems()

        for dmu, problem in problems.items():
            problem.solve()
            print('DMU {}: {}'.format(dmu, LpStatus[problem.status]))
            self.weights[dmu] = {}
            for v in problem.variables():
                self.weights[dmu][v.name] = v.varValue
            self.efficiency[dmu] = np.round(value(problem.objective), 4)
        
        return self.efficiency


branches = ['Croydon', 'Dorking', 'Redhill', 'Reigate']
inputs = pd.DataFrame(data=[18, 16, 17, 11], index=branches)
outputs = pd.DataFrame(data=[125, 44, 80, 23], index=branches)

dea = DataEnvelopmentAnalysis(inputs, outputs)
dea.solve()
print(dea.efficiency)

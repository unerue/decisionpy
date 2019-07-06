import pandas as pd
import numpy as np
import numba
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
        """
        Iterate over the inputs and create a dictionary of LP problems, one
        for each DMU.

        """

        problems = {}
        for alter in range(self.num_alters):
            problems[alter] = self._create_problem(alter)
        return problems

    def _create_problem(self, alter):
        """
        Create a pulp.LpProblem for a DMU.
        Parameter:
        ----------
        alter : 

        """
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

    def _constraint(self, j0, j1):
        """
        Calculate and return the DMU constraint for a single DMU's LP problem.

        """

        eOut = LpAffineExpression(
            [(self.outputWeights[j0][r1], self.outputs.values[j1][r1]) for r1 in self._r])
        eIn = LpAffineExpression(
            [(self.inputWeights[j0][i1], self.inputs.values[j1][i1]) for i1 in self._i])
        return eOut - eIn

    def _solver(self):
        """
        Iterate over the dictionary of DMUs' problems, solve them, and collate
        the results into a pandas dataframe.

        """

        sol_status = {}
        sol_weights = {}
        sol_efficiency = {}

        for ind, problem in list(self.dmus.items()):
            problem.solve()
            sol_status[ind] = pulp.LpStatus[problem.status]
            sol_weights[ind] = {}
            for v in problem.variables():
                sol_weights[ind][v.name] = v.varValue
            sol_efficiency[ind] = pulp.value(problem.objective)
        return sol_status, sol_efficiency, sol_weights

    def _build_weight_results_dict(self, sol_weights):
        """
        Rename weights from input and output column names, then build a
        pandas dataframe of all weights.

        """
        import re
        tmp_dict = {}
        for dmu, d in list(sol_weights.items()):
            tmp_dict[dmu] = {}
            for key, _ in list(d.items()):
                m = re.search(r'[0-9]+$',key)
                i = int(m.group(0))
                if key.startswith("input"):
                    tmp_dict[dmu]["in_" + str(self.inputs.columns[i])] = d[key]
                if key.startswith("output"):
                    tmp_dict[dmu][
                        "out_" + str(self.outputs.columns[i])] = d[key]
        weight_results = pd.DataFrame.from_dict(tmp_dict).T

        return weight_results

    def solve(self, sol_type='technical'):
        """"
        Solve the problem and create attributes to hold the solutions.

        Takes:
            sol_type: 'technical'/'allocative'/'economic'
            dmus: tuple defining range of DMUs to solve for.

        """

        if sol_type == 'technical':
            sol_status, sol_efficiency, sol_weights = self._solver()
            weight_results = self._build_weight_results_dict(sol_weights)
            status_df = pd.Series(sol_status, name='Status')
            status_df.index = self.inputs.index
            efficiency_df = pd.Series(sol_efficiency, name='Efficiency')
            efficiency_df.index = self.inputs.index

            return DEAResults((('Status', status_df),
                               ('Efficiency', efficiency_df),
                               ('Weights', weight_results)))
        else:
            print("Solution type not yet implemented.")
            print("Solving for technical efficiency instead.")
            self.solve()


class PrintResults(dict):
    """ PrintResults
    A class to hold the results of a DEAProblem and provide methods for
    their examination. Essentially a dictionary of pandas Series with
    methods for conducting particular operations on DEA results.


    """
    def __init__(self):
        super(PrintResults, self).__init__()
        pass

    def find_comparators(self, dmu):
        """
        Return the DMUs that form the frontier for the specified DMU.

        """
        pass

    def env_corr(self, env_vars, coeff_plot=False, qq_plot=False):
        """
        Determine correlations with environmental/non-discretionary variables
        using a logit regression. Tobit will be implemented when available
        upstream in statsmodels.

        Takes:
            env_vars: A pandas dataframe of environmental variables

        Returns:
            corr_mod: the statsmodels' model instance containing the inputs
                      and results from the logit model.

        Note that there can be no spaces in the variables' names.
        """

        import matplotlib.pyplot as plt
        from statsmodels.regression.linear_model import OLS
        from statsmodels.graphics.gofplots import qqplot
        from seaborn import coefplot

        env_data = _to_dataframe(env_vars)
        corr_data = env_data.join(self['Efficiency'])
        corr_mod = OLS.from_formula(
            "Efficiency ~ " + " + ".join(env_vars.columns), corr_data)
        corr_res = corr_mod.fit()

        #plot coeffs
        if coeff_plot:
            coefplot("Efficiency ~ " + " + ".join(env_vars.columns),
                     data=corr_data)
            plt.xticks(rotation=45, ha='right')
            plt.title('Regression coefficients and standard errors')

        #plot qq of residuals
        if qq_plot:
            qqplot(corr_res.resid, line='s')
            plt.title('Distribution of residuals')

        print(corr_res.summary())

        return corr_res



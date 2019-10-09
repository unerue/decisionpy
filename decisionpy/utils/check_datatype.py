import pandas as pd
import numpy as np
from sklearn.utils import check_array


def _check_datatype(input_data):
    if type(input_data) is pd.DataFrame:
        return input_data
    elif type(input_data) is pd.Series:
        return input_data
    elif type(input_data) is np.array:
        return _to_dataframe(input_data)
    else:
        raise TypeError('Input dataset is not a valid pandas.core.DataFrame, Series or Numpy array')

            
def _to_dataframe(input_data):
    num_columns = input_data.shape[1]
    columns = ['Column {}'.format(i+1) for i in num_columns]
    input_data = pd.DataFrame(input_data, columns=columns)
    return input_data


def check_dataframe(input_data):
    if type(input_data) is pd.DataFrame:
        return data
    elif type(input_data) is pd.Series:
        return pd.DataFrame(input_data, columns=['input_data'])
    else:
        raise TypeError('Input data is not a valid pandas.core.DataFrame or Series.')





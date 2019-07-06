import pandas as pd
import numpy as np
from sklearn.utils import check_array


def _check_datatype(input_data):
    """ A wrapper for _check_datatype

    Parameters:
    -----------
    input_data :

    Returns:
    --------
    input_data:

    Raises:
    -------
    TypeError :
    """
    if type(input_data) is pd.DataFrame:
        return input_data
    elif type(input_data) is pd.Series:
        return input_data
    elif type(input_data) is np.array:
        return _to_dataframe(input_data)
    else:
        raise TypeError('Input dataset is not a valid pandas DataFrame, Series or Numpy array')

            
def _to_dataframe(input_data):
    """ _to_dataframe
    """
    num_columns = input_data.shape[1]
    columns = ['Column {}'.format(i+1) for i in num_columns]
    input_data = pd.DataFrame(input_data, columns=columns)
    return input_data


def check_dataframe(input_data):
    """
    Indexers require input to be a dataframe but the user may pass a
    series. Check and cast series to dataframes.

    """
    if type(input_data) is pd.DataFrame:
        return data
    elif type(input_data) is pd.Series:
        return pd.DataFrame(input_data, columns=['input_data'])
    else:
        raise TypeError('Input data is not a valid pandas DataFrame or Series.')





def check_array_pandas(X: pd.DataFrame,
                       feature_names: List,
                       *args, **kwargs):
    ''' A wrapper for sklearn check_array

    Used to check and enforce column names if pandas dataframes are used.

    Parameters
    --------
    X: pd.DataFrame
        The input you want to check.
    feature_names: list of column names
        The column names you'd like to check and their ordering you want to enforce.
    *args
        *args for check_array
    **kwargs
        **kwargs for check_array

    Returns
    --------
    X: array like
        With columns ordered like feature_names and all other columns removed.
        Also then put through check_array.

    Raises
    --------
    KeyError:
        If any feature_names aren't in X.columns.
    TypeError:
        If X is not a pd.DataFrame.
    ValueError:
        If feature_names is None.

    '''
    if feature_names is not None:
        if isinstance(X, pd.DataFrame):
            if isinstance(feature_names, (collections.Iterable)):
                X = X[feature_names]
            else:
                raise TypeError('feature_names should be iterable.')
        else:
            raise TypeError('X should be a DataFrame for safety purposes.')

    return check_array(X, *args, **kwargs)




def _to_dataframe(indata):
    """
    Indexers require input to be a dataframe but the user may pass a
    series. Check and cast series to dataframes.

    """

    if type(indata) == pd.core.frame.DataFrame:
        return indata
    elif type(indata) == pd.core.series.Series:
        return pd.DataFrame(indata, columns=['input_data'])
    else:
        raise TypeError(
            "Input data is not a valid pandas DataFrame or Series.")

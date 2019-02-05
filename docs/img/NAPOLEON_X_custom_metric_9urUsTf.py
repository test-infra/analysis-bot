import numpy as np
import pandas as pd

def napoleon_metric(y_true, y_estim):
    """
    Compute a kind of distance between two vectors such that:
    f(x, y) = mean(abs(g(x) - g(y)))
    where g is a sigmoid function:
    g(x) = sign(x) * exp(- 1 / abs(x))

    Parameters
    ----------
    y_true :
        Vector of true value of the target.
    y_estim :
        Vector of the estimated values of the target.
    Returns
    -------
    score : np.float64
        Score of the estimation.
    """
    # Check type of y_true
    if isinstance(y_true, list):
        y_true = np.asarray(y_true)
    elif isinstance(y_true, pd.core.frame.DataFrame):
        y_true = np.asarray(y_true).flatten()
    elif isinstance(y_true, pd.core.series.Series):
        y_true = np.asarray(y_true).flatten()
    # Check type of y_est
    if isinstance(y_estim, list):
        y_estim = np.asarray(y_estim)
    elif isinstance(y_estim, pd.core.frame.DataFrame):
        y_estim = np.asarray(y_estim).flatten()
    elif isinstance(y_estim, pd.core.series.Series):
        y_estim = np.asarray(y_estim).flatten()
    # Check shapes
    if y_estim.shape != y_true.shape:
        print('y_estim and y_true must be the same shape.')
        raise ValueError

    # Score computation
    return np.mean(np.abs(napoleon_sigmoid(y_true.squeeze()) -
                          napoleon_sigmoid(y_estim.squeeze())))


def napoleon_sigmoid(y):
    """
    For a given vector of values compute the vector values between ]-1, 1[ by
    the follwing function:
    f(x) = sign(x) * exp(- 1 / abs(x))

    Parameters
    ----------
    y : np.ndarray[dtype=np.float64, ndim=1]
        Vector of unsigned real values.

    Returns
    -------
    x : np.ndarray[dtype=np.float64, ndim=1]
        Vector of real values between ]-1, 1[.
    """
    # Check type of y
    if isinstance(y, list):
        y = np.asarray(y)
    elif isinstance(y, pd.core.frame.DataFrame):
        y = np.asarray(y).flatten()
    elif isinstance(y, pd.core.series.Series):
        y = np.asarray(y).flatten()
    # Compute sigmoid
    x = np.zeros(y.size)
    x[y != 0] = np.sign(y[y != 0]) * np.exp(- 1 / np.abs(y[y != 0]))
    return x

if __name__ == '__main__':
    import pandas as pd
    CSV_FILE_1 = '--------.csv'
    CSV_FILE_2 = '--------.csv'
    df_1 = pd.read_csv(CSV_FILE_1, index_col=0, sep=',')
    df_2 = pd.read_csv(CSV_FILE_2, index_col=0, sep=',')
    print(napoleon_metric(df_1, df_2))

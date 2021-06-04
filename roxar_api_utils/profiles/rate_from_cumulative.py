import numpy as np

def rate_from_cumulative(vtime, v):
    """Calculate rate from cumulative
    Args:
        vt (np array): Time vector
        v (np array): Cumulative vector
    Returns:
        np array with rate values
    """

    leng = vtime.size
    vrat = np.zeros(leng)
    for i in range(1, leng):
        vrat[i] = (v[i] - v[i-1])/(vtime[i] - vtime[i-1])

    return vrat

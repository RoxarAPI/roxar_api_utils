import numpy as np

def cumulative_from_rate(vtime, v):
    """Calculate cumulative from rate
    Args:
        vt (np array): Time vector
        v (np array): Rate vector
    Returns:
        np array with cumulatives
    """

    leng = vtime.size
    vcum = np.zeros(leng)
    for i in range(1, leng):
        vcum[i] = vcum[i-1] + v[i]*(vtime[i] - vtime[i-1])

    return vcum

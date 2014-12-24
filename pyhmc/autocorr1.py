# This code is adapted from https://github.com/dfm/emcee (MIT license)
from __future__ import division, print_function, absolute_import
import sys
import numpy as np
from ._utils import find_first
try:
    from scipy.signal.signaltools import _next_regular
except ImportError:
    print('scipy >= 0.14 is required.')
    raise


__all__ = ["autocorr", "integrated_autocorr1"]


def integrated_autocorr1(x, window=None):
    r"""Estimate the integrated autocorrelation time, :math:`\tau_{int}` of a
    time series.

    Parameters
    ----------
    x : ndarray, shape=(n_samples, n_dims)
        The time series, with time along axis 0.
    window : int, optional
        The size of the window to use. If not supplied, the window is chosen
        to be the index of the first time the autocorrelation function crosses
        zero (Chodera 2007).

    Notes
    -----
    This method directly sums the first `k` entries of the ACF, where `k` is
    chosen to be the index of the first instance where the ACF crosses zero.

    References
    ----------
    .. [1] J. D. Chodera, W. C. Swope, J. W. Pitera, C. Seok, and K. A. Dill.
       JCTC 3(1):26-41, 2007.

    Returns
    -------
    tau_int : ndarray, shape=(n_dims,)
        The estimated integrated autocorrelation time of each dimension in
        ``x``, considered independently.
    """
    # Compute the autocorrelation function.
    if x.ndim == 1:
        x = x.reshape(-1, 1)

    f = autocorr(x, axis=0)
    if window is None:
        window = find_first((f < 0).astype(np.uint8))
    elif np.isscalar(window):
        window = window * np.ones(x.shape[1])
    else:
        raise NotImplementedError()

    tau = np.zeros(x.shape[1])
    for j in range(x.shape[1]):
        tau[j] = 1 + 2*np.sum(f[:window[j], j])
    return tau


def autocorr(x, axis=0):
    """Estimate the autocorrelation function of a time series using the FFT.

    Parameters
    ----------
    x : ndarray, shape=(n_samples,) or shape=(n_samples, n_dims)
        The time series. If multidimensional, set the time axis using the
        ``axis`` keyword argument and the function will be computed for every
        other axis.
    axis :  int, optional
        The time axis of ``x``. Assumed to be the first axis if not specified.

    Examples
    --------
    >>> # [ generate samples from ``hmc`` ]
    >>> acf = autocorr(samples)
    >>> import matplotlib.pyplot as plt
    >>> plt.semilogx(acf)

    .. image:: ../_static/autocorr.png

    Returns
    -------
    acf : ndarray, shape=(n_samples,) or shape=(n_samples, n_dims)
        The autocorrelation function of ``x``
    """
    x = np.atleast_1d(x)
    n = x.shape[axis]
    x = x - np.mean(x, axis=axis)

    m = [slice(None), ] * x.ndim
    m[axis] = slice(0, n)

    # Compute the FFT and then (from that) the auto-correlation function.
    f = np.fft.fft(x, n=_next_regular(n+1), axis=axis)
    acf = np.fft.ifft(f * np.conjugate(f), axis=axis)[m].real

    m[axis] = 0
    return acf / acf[m]

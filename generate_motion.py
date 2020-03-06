#!/usr/bin/env python3
import numpy as np


def derivative(f, a, method='central', h=0.0001):
    '''Compute the difference formula for f'(a) with step size h.

    Parameters
    ----------
    f : function
        Vectorized function of one variable
    a : number
        Compute derivative at x = a
    method : string
        Difference formula: 'forward', 'backward' or 'central'
    h : number
        Step size in difference formula

    Returns
    -------
    float
        Difference formula:
            central: f(a+h) - f(a-h))/2h
            forward: f(a+h) - f(a))/h
            backward: f(a) - f(a-h))/h            
    '''
    if method == 'central':
        return (f(a + h) - f(a - h))/(2*h)
    elif method == 'forward':
        return (f(a + h) - f(a))/h
    elif method == 'backward':
        return (f(a) - f(a - h))/h
    else:
        raise ValueError("Method must be 'central', 'forward' or 'backward'.")


def calculate_motion(position: list, Fs: int = 50, duration: float = 0, time_series: list = list()):
    dt = 1/Fs
    if not time_series:
        duration = duration if duration else len(position)*dt
        _time = np.arange(0, duration, dt)
    else:
        _time = np.array(time_series)

    if len(position) != len(_time):
        print("Postition arrays and time_series should have a same lenght.")
        raise ValueError
    _pos = np.round(np.array(position), 10)
    _time = np.round(np.diff(_time), 6)

    velocities = np.round(np.diff(_pos)/_time, 6)  # first derivative
    accelerationes = np.round(
        np.diff(velocities)/_time[:-1], 6)  # second derivative

    return velocities, accelerationes


def main():
    x = np.random.randint(low=1, high=100, size=10)
    v, a = calculate_motion(x)
    print(v, a.astype(int))


if __name__ == "__main__":
    main()

"""The module contains logic related to the SIRD model - the simulate_sird function, as well as the auxiliary function piecewise_beta."""

import numpy as np


def piecewise_beta(d, t1, t2, beta1, beta2):
    if d < t1:
        return beta1
    if d < t2:
        frac = (d - t1) / max((t2 - t1), 1e-8)
        return beta1 + frac * (beta2 - beta1)
    return beta2


def simulate_sird(params, days, S0, I0, R0, D0, dt=0.5, substeps=2, Npop=38e6):
    beta1 = params["beta1"]
    beta2 = params["beta2"]
    t1 = params["t1"]
    t2 = params["t2"]
    gamma_ = params["gamma"]
    mu_ = params["mu"]

    S_arr = np.zeros(days)
    I_arr = np.zeros(days)
    R_arr = np.zeros(days)
    D_arr = np.zeros(days)

    S = S0
    I = I0
    R = R0
    D = D0

    for day_idx in range(days):
        S_arr[day_idx] = S
        I_arr[day_idx] = I
        R_arr[day_idx] = R
        D_arr[day_idx] = D

        for _ in range(substeps):
            if day_idx < t1:
                beta_t = beta1
            elif day_idx < t2:
                frac = (day_idx - t1) / (t2 - t1 + 1e-8)
                beta_t = beta1 + frac * (beta2 - beta1)
            else:
                beta_t = beta2

            dS = -beta_t * (S * I / Npop)
            dI = beta_t * (S * I / Npop) - (gamma_ + mu_) * I
            dR = gamma_ * I
            dD = mu_ * I

            S_new = S + dS * dt
            I_new = I + dI * dt
            R_new = R + dR * dt
            D_new = D + dD * dt

            S_new = max(S_new, 0)
            I_new = max(I_new, 0)
            R_new = max(R_new, 0)
            D_new = max(D_new, 0)

            S_new = min(S_new, 1e15)
            I_new = min(I_new, 1e15)
            R_new = min(R_new, 1e15)
            D_new = min(D_new, 1e15)

            S, I, R, D = S_new, I_new, R_new, D_new

    return S_arr, I_arr, R_arr, D_arr

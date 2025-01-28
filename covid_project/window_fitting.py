import numpy as np


from .pso_fitting import run_pso_sird_gpu
from .sird_simulation import simulate_sird
from covid_project.constants import DT, SUBSTEPS, NUM_PARTICLES, MAX_ITER


def multiple_runs_fit_sird(
    df,
    start_date,
    end_date,
    num_runs=1000,
    cost_type=20,
    use_norm=True,
    n_particles=NUM_PARTICLES,
    max_iter=MAX_ITER,
    forecast_days=0,
    population=38e6,
    DT=DT,
    SUBSTEPS=SUBSTEPS,
):
    """
    Performs num_runs of PSO matches in the selected [start_date..end_date] window.
    Returns a list (S,I,R,D) of length (days_window + forecast_days) for each trial.
    """
    dfw = df[(df["Last_Update"] >= start_date) & (df["Last_Update"] <= end_date)].copy()
    dfw.reset_index(drop=True, inplace=True)
    days_window = len(dfw)
    if days_window < 2:
        print("Za mało danych w oknie:", start_date, end_date)
        return []

    I_emp = dfw["Active"].values.astype(float)
    R_emp = dfw["Recovered"].values.astype(float)
    D_emp = dfw["Deaths"].values.astype(float)

    # Initial conditions
    row0 = dfw.iloc[0]
    S0 = population - (row0["Active"] + row0["Recovered"] + row0["Deaths"])
    I0 = row0["Active"]
    R0 = row0["Recovered"]
    D0 = row0["Deaths"]

    # Normalize
    if use_norm:
        i_min, i_max = I_emp.min(), I_emp.max()
        r_min, r_max = R_emp.min(), R_emp.max()
        d_min, d_max = D_emp.min(), D_emp.max()
        i_rng = max(i_max - i_min, 1e-6)
        r_rng = max(r_max - r_min, 1e-6)
        d_rng = max(d_max - d_min, 1e-6)

        I_emp_norm = (I_emp - i_min) / i_rng
        R_emp_norm = (R_emp - r_min) / r_rng
        D_emp_norm = (D_emp - d_min) / d_rng
    else:
        I_emp_norm = I_emp
        R_emp_norm = R_emp
        D_emp_norm = D_emp
        i_min, i_rng = 0.0, 1.0
        r_min, r_rng = 0.0, 1.0
        d_min, d_rng = 0.0, 1.0

    all_trajectories = []
    for run_idx in range(num_runs):
        gbest_params, hist = run_pso_sird_gpu(
            days=days_window,
            D_emp=D_emp_norm,
            I_emp=I_emp_norm,
            R_emp=R_emp_norm,
            S0=S0,
            I0=I0,
            R0=R0,
            D0=D0,
            dt=DT,
            substeps=SUBSTEPS,
            Npop=population,
            n_particles=n_particles,
            max_iter=max_iter,
            cost_type=cost_type,
            use_norm=use_norm,
            i_min=i_min,
            i_rng=i_rng,
            r_min=r_min,
            r_rng=r_rng,
            d_min=d_min,
            d_rng=d_rng,
        )

        # “Fit in the window” simulation
        S_fit, I_fit, R_fit, D_fit = simulate_sird(
            gbest_params,
            days_window,
            S0,
            I0,
            R0,
            D0,
            dt=DT,
            substeps=SUBSTEPS,
            Npop=population,
        )

        # Forecast
        if forecast_days > 0:
            s_last = S_fit[-1]
            i_last = I_fit[-1]
            r_last = R_fit[-1]
            d_last = D_fit[-1]

            beta2 = gbest_params["beta2"]
            gamma_ = gbest_params["gamma"]
            mu_ = gbest_params["mu"]
            tmp_params = {
                "beta1": beta2,
                "beta2": beta2,
                "t1": 0,
                "t2": 0,
                "gamma": gamma_,
                "mu": mu_,
            }
            S_ext, I_ext, R_ext, D_ext = simulate_sird(
                tmp_params,
                forecast_days,
                s_last,
                i_last,
                r_last,
                d_last,
                dt=DT,
                substeps=SUBSTEPS,
                Npop=population,
            )

            S_full = np.concatenate([S_fit, S_ext])
            I_full = np.concatenate([I_fit, I_ext])
            R_full = np.concatenate([R_fit, R_ext])
            D_full = np.concatenate([D_fit, D_ext])
        else:
            S_full = S_fit
            I_full = I_fit
            R_full = R_fit
            D_full = D_fit

        all_trajectories.append((S_full, I_full, R_full, D_full))

    return all_trajectories


def window_wise_fitting(
    df,
    population=38e6,
    window_size=36,
    step=3,
    cost_type=30,
    n_particles=NUM_PARTICLES,
    max_iter=MAX_ITER,
    use_norm=False,
    i_min=0.0,
    i_rng=1.0,
    r_min=0.0,
    r_rng=1.0,
    d_min=0.0,
    d_rng=1.0,
    DT=DT,
    SUBSTEPS=SUBSTEPS,
):
    """
    We take a window of 36 days, move every 3 days,
    we adjust the SIRD parameters in this window to I,R,D with cost_type=30 (MXSE(IRD)).
    """
    T = len(df)
    results = []

    for start_day in range(0, T - window_size + 1, step):
        df_window = df.iloc[start_day : start_day + window_size]

        D_emp = df_window["Deaths"].values
        I_emp = (
            df_window["Active"].values
            if "Active" in df_window.columns
            else np.zeros_like(D_emp)
        )
        R_emp = (
            df_window["Recovered"].values
            if "Recovered" in df_window.columns
            else np.zeros_like(D_emp)
        )

        # Initial conditions
        row_0 = df_window.iloc[0]
        S0 = population - (row_0["Active"] + row_0["Recovered"] + row_0["Deaths"])
        I0 = row_0["Active"]
        R0 = row_0["Recovered"]
        D0 = row_0["Deaths"]

        gbest_params, hist = run_pso_sird_gpu(
            days=window_size,
            D_emp=D_emp,
            I_emp=I_emp,
            R_emp=R_emp,
            S0=S0,
            I0=I0,
            R0=R0,
            D0=D0,
            dt=DT,
            substeps=SUBSTEPS,
            Npop=population,
            n_particles=n_particles,
            max_iter=max_iter,
            cost_type=cost_type,
            use_norm=use_norm,
            i_min=i_min,
            i_rng=i_rng,
            r_min=r_min,
            r_rng=r_rng,
            d_min=d_min,
            d_rng=d_rng,
        )

        S_fit, I_fit, R_fit, D_fit = simulate_sird(
            gbest_params,
            window_size,
            S0,
            I0,
            R0,
            D0,
            dt=DT,
            substeps=SUBSTEPS,
            Npop=population,
        )

        results.append({
            "start_day": start_day,
            "best_params": gbest_params,
            "cost_history": hist,
            "S_fit": S_fit,
            "I_fit": I_fit,
            "R_fit": R_fit,
            "D_fit": D_fit,
        })

    return results

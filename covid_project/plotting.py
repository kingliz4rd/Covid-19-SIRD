import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
import pandas as pd


def plot_all_trajectories_SIRD(
    all_trajectories,
    df,
    start_date,
    end_date,
    forecast_days=0,
    title="Multiple runs",
    population=38e6,
    tick_step=7,
):
    """
    We draw 4 subplots: S,I,R,D - all (N) runs + empirical points.
    """
    num_runs = len(all_trajectories)
    if num_runs == 0:
        print("No trajectory to draw.")
        return None

    L = len(all_trajectories[0][0])

    end_date_ext = end_date + pd.Timedelta(days=forecast_days)
    df_ext = df[
        (df["Last_Update"] >= start_date) & (df["Last_Update"] <= end_date_ext)
    ].copy()
    df_ext.reset_index(drop=True, inplace=True)

    x_data = np.arange(len(df_ext))
    date_labels = df_ext["Last_Update"].dt.strftime("%Y-%m-%d").values

    df_ext["S_calc"] = population - (
        df_ext["Active"] + df_ext["Recovered"] + df_ext["Deaths"]
    )

    S_emp_ext = df_ext["S_calc"].values
    I_emp_ext = df_ext["Active"].values
    R_emp_ext = df_ext["Recovered"].values
    D_emp_ext = df_ext["Deaths"].values

    fig, axs = plt.subplots(4, 1, figsize=(10, 14), sharex=True)

    fc_start_idx = L - forecast_days if forecast_days > 0 else L

    # S(t)
    for run_idx in range(num_runs):
        S_run = all_trajectories[run_idx][0]
        if forecast_days > 0:
            axs[0].plot(
                np.arange(fc_start_idx), S_run[:fc_start_idx], color="blue", alpha=0.03
            )
            axs[0].plot(
                np.arange(fc_start_idx, L),
                S_run[fc_start_idx:],
                color="magenta",
                alpha=0.03,
                linestyle="--",
            )
        else:
            axs[0].plot(S_run, color="blue", alpha=0.03)
    axs[0].plot(x_data, S_emp_ext, "ko", ms=3, label="Empiryczne S")
    axs[0].set_ylabel("S(t)")
    axs[0].legend()
    axs[0].set_title(f"S(t) – {title}")

    # I(t)
    for run_idx in range(num_runs):
        I_run = all_trajectories[run_idx][1]
        if forecast_days > 0:
            axs[1].plot(
                np.arange(fc_start_idx), I_run[:fc_start_idx], color="red", alpha=0.03
            )
            axs[1].plot(
                np.arange(fc_start_idx, L),
                I_run[fc_start_idx:],
                color="magenta",
                alpha=0.03,
                linestyle="--",
            )
        else:
            axs[1].plot(I_run, color="red", alpha=0.03)
    axs[1].plot(x_data, I_emp_ext, "ko", ms=3, label="Empiryczne I")
    axs[1].set_ylabel("I(t)")
    axs[1].legend()
    axs[1].set_title(f"I(t) – {title}")

    # R(t)
    for run_idx in range(num_runs):
        R_run = all_trajectories[run_idx][2]
        if forecast_days > 0:
            axs[2].plot(
                np.arange(fc_start_idx), R_run[:fc_start_idx], color="green", alpha=0.03
            )
            axs[2].plot(
                np.arange(fc_start_idx, L),
                R_run[fc_start_idx:],
                color="magenta",
                alpha=0.03,
                linestyle="--",
            )
        else:
            axs[2].plot(R_run, color="green", alpha=0.03)
    axs[2].plot(x_data, R_emp_ext, "ko", ms=3, label="Empiryczne R")
    axs[2].set_ylabel("R(t)")
    axs[2].legend()
    axs[2].set_title(f"R(t) – {title}")

    # D(t)
    for run_idx in range(num_runs):
        D_run = all_trajectories[run_idx][3]
        if forecast_days > 0:
            axs[3].plot(
                np.arange(fc_start_idx), D_run[:fc_start_idx], color="black", alpha=0.03
            )
            axs[3].plot(
                np.arange(fc_start_idx, L),
                D_run[fc_start_idx:],
                color="magenta",
                alpha=0.03,
                linestyle="--",
            )
        else:
            axs[3].plot(D_run, color="black", alpha=0.03)
    axs[3].plot(x_data, D_emp_ext, "ro", ms=3, label="Empiryczne D")
    axs[3].set_ylabel("D(t)")
    axs[3].legend()
    axs[3].set_title(f"D(t) – {title}")

    if forecast_days > 0:
        for ax in axs:
            ax.axvline(
                fc_start_idx, color="grey", linestyle="--", label="Start forecast"
            )

    xticks = np.arange(0, len(df_ext), tick_step)
    axs[3].set_xticks(xticks)
    axs[3].set_xticklabels(date_labels[xticks], rotation=90)
    axs[3].set_xlabel("Data")

    plt.tight_layout()
    return fig


def plot_compartments_fits(df, wresults, title_suffix="", save_path=None, ds=0):
    """
    We draw min-max envelopes based on wresults (window list),
    we superimpose the empirical data (I,R,D) on it.
    """
    import numpy as np

    T = len(df)
    x_dates = df["Last_Update"].values

    I_data = df["Active"].values if "Active" in df.columns else np.zeros(T)
    R_data = df["Recovered"].values if "Recovered" in df.columns else np.zeros(T)
    D_data = df["Deaths"].values if "Deaths" in df.columns else np.zeros(T)

    minI = np.full(T, np.inf)
    maxI = np.full(T, -np.inf)
    minR = np.full(T, np.inf)
    maxR = np.full(T, -np.inf)
    minD = np.full(T, np.inf)
    maxD = np.full(T, -np.inf)

    for res in wresults:
        start_day = res["start_day"]
        I_fit = res["I_fit"]
        R_fit = res["R_fit"]
        D_fit = res["D_fit"]

        for d in range(len(I_fit)):
            global_day = start_day + d
            if global_day < T:
                minI[global_day] = min(minI[global_day], I_fit[d])
                maxI[global_day] = max(maxI[global_day], I_fit[d])
                minR[global_day] = min(minR[global_day], R_fit[d])
                maxR[global_day] = max(maxR[global_day], R_fit[d])
                minD[global_day] = min(minD[global_day], D_fit[d])
                maxD[global_day] = max(maxD[global_day], D_fit[d])

    for arr in (minI, maxI, minR, maxR, minD, maxD):
        arr[np.isinf(arr)] = np.nan

    fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)

    # I
    axes[0].fill_between(
        x_dates, minI, maxI, color="blue", alpha=0.3, label="I fit bounds"
    )
    axes[0].plot(x_dates, I_data, "k.", label="I empirical (Active)")
    axes[0].set_title(f"Active (I) {title_suffix}")
    axes[0].legend()

    # R
    axes[1].fill_between(
        x_dates, minR, maxR, color="green", alpha=0.3, label="R fit bounds"
    )
    axes[1].plot(x_dates, R_data, "k.", label="R empirical (Recovered)")
    axes[1].set_title(f"Recovered (R) {title_suffix}")
    axes[1].legend()

    # D
    axes[2].fill_between(
        x_dates, minD, maxD, color="red", alpha=0.3, label="D fit bounds"
    )
    axes[2].plot(x_dates, D_data, "k.", label="D empirical (Deaths)")
    axes[2].set_title(f"Deaths (D) {title_suffix}")
    axes[2].legend()

    if ds == 0:
        axes[0].set_ylim([0, 25000])

    for ax in axes:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=14))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.tick_params(axis="x", rotation=45)

    plt.xlabel("Data")
    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, bbox_inches="tight")

    plt.show()


def plot_params_wresults(df, wresults, title_suffix="", save_path=None):
    """
    Drawing 4 subplots:
      1) Beta(t) envelope
      2) Gamma(t) envelope
      3) Mu(t) envelope
      4) R0(t) envelope
    Based on results from window_wise_fitting (wresults).
    """
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from .sird_simulation import piecewise_beta

    T = len(df)
    x_dates = df["Last_Update"].values

    minBeta = np.full(T, np.inf)
    maxBeta = np.full(T, -np.inf)
    minGamma = np.full(T, np.inf)
    maxGamma = np.full(T, -np.inf)
    minMu = np.full(T, np.inf)
    maxMu = np.full(T, -np.inf)
    minR0 = np.full(T, np.inf)
    maxR0 = np.full(T, -np.inf)

    for res in wresults:
        start_day = res["start_day"]
        best_params = res["best_params"]

        beta1 = best_params["beta1"]
        beta2 = best_params["beta2"]
        t1 = best_params["t1"]
        t2 = best_params["t2"]
        gamma_ = best_params["gamma"]
        mu_ = best_params["mu"]

        window_size = len(res["I_fit"])

        for dlocal in range(window_size):
            dglobal = start_day + dlocal
            if dglobal >= T:
                break

            beta_d = piecewise_beta(dlocal, t1, t2, beta1, beta2)
            gamma_d = gamma_
            mu_d = mu_
            denom = max(gamma_d + mu_d, 1e-12)
            r0_d = beta_d / denom

            minBeta[dglobal] = min(minBeta[dglobal], beta_d)
            maxBeta[dglobal] = max(maxBeta[dglobal], beta_d)

            minGamma[dglobal] = min(minGamma[dglobal], gamma_d)
            maxGamma[dglobal] = max(maxGamma[dglobal], gamma_d)

            minMu[dglobal] = min(minMu[dglobal], mu_d)
            maxMu[dglobal] = max(maxMu[dglobal], mu_d)

            minR0[dglobal] = min(minR0[dglobal], r0_d)
            maxR0[dglobal] = max(maxR0[dglobal], r0_d)

    for arr in (minBeta, maxBeta, minGamma, maxGamma, minMu, maxMu, minR0, maxR0):
        arr[np.isinf(arr)] = np.nan

    fig, axs = plt.subplots(4, 1, figsize=(10, 12), sharex=True)

    axs[0].fill_between(
        x_dates, minBeta, maxBeta, color="blue", alpha=0.3, label="β(t) obwiednia"
    )
    axs[0].plot(x_dates, minBeta, color="blue", alpha=0.6)
    axs[0].plot(x_dates, maxBeta, color="blue", alpha=0.6)
    axs[0].set_ylabel("beta(t)")
    axs[0].set_title(f"β(t) {title_suffix}")
    axs[0].legend()

    axs[1].fill_between(
        x_dates, minGamma, maxGamma, color="green", alpha=0.3, label="γ(t) obwiednia"
    )
    axs[1].plot(x_dates, minGamma, color="green", alpha=0.6)
    axs[1].plot(x_dates, maxGamma, color="green", alpha=0.6)
    axs[1].set_ylabel("gamma")
    axs[1].set_title(f"γ(t) {title_suffix}")
    axs[1].legend()

    axs[2].fill_between(
        x_dates, minMu, maxMu, color="red", alpha=0.3, label="μ(t) obwiednia"
    )
    axs[2].plot(x_dates, minMu, color="red", alpha=0.6)
    axs[2].plot(x_dates, maxMu, color="red", alpha=0.6)
    axs[2].set_ylabel("mu")
    axs[2].set_title(f"μ(t) {title_suffix}")
    axs[2].legend()

    axs[3].fill_between(
        x_dates, minR0, maxR0, color="orange", alpha=0.3, label="R0(t) obwiednia"
    )
    axs[3].plot(x_dates, minR0, color="orange", alpha=0.6)
    axs[3].plot(x_dates, maxR0, color="orange", alpha=0.6)
    axs[3].set_ylabel("R0(t)")
    axs[3].set_title(f"R0(t) = β(t)/(γ+μ) {title_suffix}")
    axs[3].legend()

    for ax in axs:
        ax.xaxis.set_major_locator(mdates.DayLocator(interval=14))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        ax.tick_params(axis="x", rotation=45)

    plt.xlabel("Data")
    plt.tight_layout()

    if save_path is not None:
        plt.savefig(save_path, bbox_inches="tight")

    plt.show()

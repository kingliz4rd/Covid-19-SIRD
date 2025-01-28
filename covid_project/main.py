#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt

from .data_loader import load_covid_data
from .window_fitting import multiple_runs_fit_sird, window_wise_fitting
from .plotting import (
    plot_all_trajectories_SIRD,
    plot_compartments_fits,
    plot_params_wresults,
)
from covid_project.constants import NUM_PARTICLES, MAX_ITER


def main():
    # 1) Load the data
    csv_path = "data/covid-19-preprocessed.csv"
    df = load_covid_data(csv_path)
    print("[INFO] Data loaded. Rows =", len(df))

    start_date_1 = pd.to_datetime("2020-05-10")
    end_date_1 = pd.to_datetime("2020-06-13")
    start_date_2 = pd.to_datetime("2021-04-04")
    end_date_2 = pd.to_datetime("2021-05-08")
    forecast_days = 21

    all_traj_1 = multiple_runs_fit_sird(
        df,
        start_date_1,
        end_date_1,
        num_runs=1000,
        cost_type=30,
        use_norm=True,
        n_particles=NUM_PARTICLES,
        max_iter=MAX_ITER,
        forecast_days=forecast_days,
        population=38e6,
    )
    fig1 = plot_all_trajectories_SIRD(
        all_traj_1,
        df,
        start_date_1,
        end_date_1,
        forecast_days=forecast_days,
        title=f"Okno1: {start_date_1.date()}..{end_date_1.date()} (cost=MXSE(IRD))",
    )
    if fig1 is not None:
        plt.show(fig1)
        fig1.savefig("1000repetitions_2020_05_10.pdf")
        plt.close(fig1)

    all_traj_2 = multiple_runs_fit_sird(
        df,
        start_date_2,
        end_date_2,
        num_runs=1000,
        cost_type=30,
        use_norm=True,
        n_particles=NUM_PARTICLES,
        max_iter=MAX_ITER,
        forecast_days=forecast_days,
        population=38e6,
    )
    fig2 = plot_all_trajectories_SIRD(
        all_traj_2,
        df,
        start_date_2,
        end_date_2,
        forecast_days=forecast_days,
        title=f"Window2: {start_date_2.date()}..{end_date_2.date()} (cost=MXSE(IRD))",
    )
    if fig2 is not None:
        plt.show(fig2)
        fig2.savefig("1000_repetitions_2021_.pdf")
        plt.close(fig2)

    # 3) Przykład: Okienkowe dopasowanie (window_wise_fitting)
    df_before = df[df["Last_Update"] <= "2020-10-20"].copy()
    wresults_before = window_wise_fitting(
        df=df_before,
        population=38e6,
        window_size=36,
        step=7,
        cost_type=30,
        n_particles=NUM_PARTICLES,
        max_iter=MAX_ITER,
        use_norm=False,
    )
    plot_compartments_fits(
        df_before,
        wresults_before,
        title_suffix="(do 20.10.2020)",
        save_path="plot_fitting_20102020.pdf",
    )

    df_after = df[df["Last_Update"] > "2020-10-20"].copy()
    wresults_after = window_wise_fitting(
        df=df_after,
        population=38e6,
        window_size=36,
        step=7,
        cost_type=30,
        n_particles=NUM_PARTICLES,
        max_iter=MAX_ITER,
        use_norm=False,
    )
    plot_compartments_fits(
        df_after,
        wresults_after,
        title_suffix="(od 21.10.2020)",
        save_path="plot_after_20102020.pdf",
        ds=1,
    )

    plot_params_wresults(
        df_before,
        wresults_before,
        title_suffix="(do 20.10.2020)",
        save_path="params1_20102020.pdf",
    )
    plot_params_wresults(
        df_after,
        wresults_after,
        title_suffix="(od 21.10.2020)",
        save_path="params_2_after_20102020.pdf",
    )

    print("\n[DONE] Skrypt zakończył działanie.")


if __name__ == "__main__":
    main()

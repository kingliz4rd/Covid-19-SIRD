"""All computing kernels using Numba/CUDA and related structures are located here."""

from numba import cuda


@cuda.jit
def sird_euler_gpu(  # noqa: PLR0912
    beta1_array,
    beta2_array,
    t1_array,
    t2_array,
    gamma_array,
    mu_array,
    cost_array,
    dt,
    substeps,
    Npop,
    days,
    I_emp,
    R_emp,
    D_emp,
    cost_type,
    S0,
    I0,
    R0,
    D0,
    use_norm,
    i_min,
    i_rng,
    r_min,
    r_rng,
    d_min,
    d_rng,
):
    pid = cuda.grid(1)
    if pid < beta1_array.size:
        beta1 = beta1_array[pid]
        beta2 = beta2_array[pid]
        t1 = t1_array[pid]
        t2 = t2_array[pid]
        gamma_ = gamma_array[pid]
        mu_ = mu_array[pid]

        # Stan początkowy
        S = S0
        I = I0
        R = R0
        D = D0

        # Akumulatory błędów dla MSE:
        err_I = 0.0
        err_R = 0.0
        err_D = 0.0

        # Do obliczania max-square-error:
        max_err_ird_sq = 0.0
        max_err_d_sq = 0.0

        # Symulacja day po day
        for day_idx in range(days):
            # -- Euler substeps (np. 2 subkroki = 1 dzień) --
            for _ in range(substeps):
                # Określenie beta(t)
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

            # -- błąd dobowy --
            if use_norm == 1:
                # Normalizacja
                di = 0.0
                dr = 0.0
                dd = 0.0
                if i_rng > 1e-12:
                    di = (I - i_min) / i_rng - I_emp[day_idx]
                if r_rng > 1e-12:
                    dr = (R - r_min) / r_rng - R_emp[day_idx]
                if d_rng > 1e-12:
                    dd = (D - d_min) / d_rng - D_emp[day_idx]
            else:
                di = I - I_emp[day_idx]
                dr = R - R_emp[day_idx]
                dd = D - D_emp[day_idx]

            if cost_type == 10:
                # sum MSE
                err_I += di * di
                err_R += dr * dr
                err_D += dd * dd

            elif cost_type == 20:
                # max squared error (dla IRD)
                sum_sq = di * di + dr * dr + dd * dd
                max_err_ird_sq = max(sum_sq, max_err_ird_sq)

            elif cost_type == 3:
                # max( (D-D_emp)^2 )
                sq = dd * dd
                max_err_d_sq = max(sq, max_err_d_sq)

            elif cost_type == 30:
                sum_sq = di * di + dr * dr + dd * dd
                max_err_ird_sq = max(sum_sq, max_err_ird_sq)

        # -- Po pętli day_idx --
        if cost_type == 10:
            cost_array[pid] = (err_I + err_R + err_D) / days
        elif cost_type == 20:
            cost_array[pid] = max_err_ird_sq
        elif cost_type == 3:
            cost_array[pid] = max_err_d_sq
        elif cost_type == 30:
            cost_array[pid] = max_err_ird_sq
        else:
            cost_array[pid] = (err_I + err_R + err_D) / days

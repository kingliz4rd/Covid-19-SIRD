import numpy as np
from numba import cuda
from .gpu_kernels import sird_euler_gpu
from covid_project.constants import W, C1, C2, DT, SUBSTEPS


def run_pso_sird_gpu(
    days,
    D_emp,
    I_emp=None,
    R_emp=None,
    S0=0.0,
    I0=0.0,
    R0=0.0,
    D0=0.0,
    dt=DT,
    substeps=SUBSTEPS,
    Npop=38e6,
    n_particles=1000,
    max_iter=50,
    cost_type=10,
    # bounds
    bounds_beta1=(0.0, 1.5),
    bounds_beta2=(0.0, 1.5),
    bounds_t1=(0.0, 10.0),
    bounds_t2=(10.0, 36.0),
    bounds_gamma=(0.0, 0.3),
    bounds_mu=(0.0, 0.05),
    # normalize
    use_norm=False,
    i_min=0.0,
    i_rng=1.0,
    r_min=0.0,
    r_rng=1.0,
    d_min=0.0,
    d_rng=1.0,
    W=W,
    C1=C1,
    C2=C2,
):
    """
    The main PSO function that returns:
    - gbest_params: dict with best parameters
    - history: a list of the best cost values in each iteration
    """

    if I_emp is None:
        I_emp = np.zeros(days, dtype=np.float32)
    if R_emp is None:
        R_emp = np.zeros(days, dtype=np.float32)

    # Initialize
    beta1 = np.random.uniform(bounds_beta1[0], bounds_beta1[1], n_particles)
    beta2 = np.random.uniform(bounds_beta2[0], bounds_beta2[1], n_particles)
    t1_ = np.random.uniform(bounds_t1[0], bounds_t1[1], n_particles)
    t2_ = np.random.uniform(bounds_t2[0], bounds_t2[1], n_particles)
    gamma_ = np.random.uniform(bounds_gamma[0], bounds_gamma[1], n_particles)
    mu_ = np.random.uniform(bounds_mu[0], bounds_mu[1], n_particles)

    v_beta1 = np.zeros(n_particles)
    v_beta2 = np.zeros(n_particles)
    v_t1 = np.zeros(n_particles)
    v_t2 = np.zeros(n_particles)
    v_gamma = np.zeros(n_particles)
    v_mu = np.zeros(n_particles)

    pbest_beta1 = beta1.copy()
    pbest_beta2 = beta2.copy()
    pbest_t1 = t1_.copy()
    pbest_t2 = t2_.copy()
    pbest_gamma = gamma_.copy()
    pbest_mu = mu_.copy()
    pbest_cost = np.ones(n_particles) * 1e30

    gbest_cost = 1e30
    gbest_params = {}

    # Convert to float32 and copy to GPU.
    d_emp_f32 = D_emp.astype(np.float32)
    i_emp_f32 = I_emp.astype(np.float32)
    r_emp_f32 = R_emp.astype(np.float32)

    D_emp_dev = cuda.to_device(d_emp_f32)
    I_emp_dev = cuda.to_device(i_emp_f32)
    R_emp_dev = cuda.to_device(r_emp_f32)

    beta1_dev = cuda.to_device(beta1.astype(np.float32))
    beta2_dev = cuda.to_device(beta2.astype(np.float32))
    t1_dev = cuda.to_device(t1_.astype(np.float32))
    t2_dev = cuda.to_device(t2_.astype(np.float32))
    gamma_dev = cuda.to_device(gamma_.astype(np.float32))
    mu_dev = cuda.to_device(mu_.astype(np.float32))

    cost_dev = cuda.device_array(n_particles, dtype=np.float32)

    use_norm_flag = 1 if use_norm else 0
    norm_data = np.array([i_min, i_rng, r_min, r_rng, d_min, d_rng], dtype=np.float32)
    norm_data_dev = cuda.to_device(norm_data)

    threadsperblock = 128
    blockspergrid = (n_particles + threadsperblock - 1) // threadsperblock

    history = []

    for it in range(max_iter):
        # 1) Kernel on GPU
        sird_euler_gpu[blockspergrid, threadsperblock](
            beta1_dev,
            beta2_dev,
            t1_dev,
            t2_dev,
            gamma_dev,
            mu_dev,
            cost_dev,
            dt,
            substeps,
            Npop,
            days,
            I_emp_dev,
            R_emp_dev,
            D_emp_dev,
            cost_type,
            S0,
            I0,
            R0,
            D0,
            use_norm_flag,
            norm_data_dev[0],
            norm_data_dev[1],
            norm_data_dev[2],
            norm_data_dev[3],
            norm_data_dev[4],
            norm_data_dev[5],
        )
        cuda.synchronize()

        # 2) Matching cost with GPU
        cost_vals = cost_dev.copy_to_host()

        # 3) Update pbest
        better_idx = cost_vals < pbest_cost
        pbest_cost[better_idx] = cost_vals[better_idx]
        pbest_beta1[better_idx] = beta1[better_idx]
        pbest_beta2[better_idx] = beta2[better_idx]
        pbest_t1[better_idx] = t1_[better_idx]
        pbest_t2[better_idx] = t2_[better_idx]
        pbest_gamma[better_idx] = gamma_[better_idx]
        pbest_mu[better_idx] = mu_[better_idx]

        # 4) Update gbest
        min_cost_idx = np.argmin(cost_vals)
        min_cost_val = cost_vals[min_cost_idx]
        if min_cost_val < gbest_cost:
            gbest_cost = min_cost_val
            gbest_params = {
                "beta1": beta1[min_cost_idx],
                "beta2": beta2[min_cost_idx],
                "t1": t1_[min_cost_idx],
                "t2": t2_[min_cost_idx],
                "gamma": gamma_[min_cost_idx],
                "mu": mu_[min_cost_idx],
            }

        history.append(gbest_cost)

        # 5) Speed and position update
        r1 = np.random.rand(n_particles)
        r2 = np.random.rand(n_particles)
        v_beta1 = (
            W * v_beta1
            + C1 * r1 * (pbest_beta1 - beta1)
            + C2 * r2 * (gbest_params["beta1"] - beta1)
        )
        beta1 += v_beta1

        r1 = np.random.rand(n_particles)
        r2 = np.random.rand(n_particles)
        v_beta2 = (
            W * v_beta2
            + C1 * r1 * (pbest_beta2 - beta2)
            + C2 * r2 * (gbest_params["beta2"] - beta2)
        )
        beta2 += v_beta2

        r1 = np.random.rand(n_particles)
        r2 = np.random.rand(n_particles)
        v_t1 = (
            W * v_t1 + C1 * r1 * (pbest_t1 - t1_) + C2 * r2 * (gbest_params["t1"] - t1_)
        )
        t1_ += v_t1

        r1 = np.random.rand(n_particles)
        r2 = np.random.rand(n_particles)
        v_t2 = (
            W * v_t2 + C1 * r1 * (pbest_t2 - t2_) + C2 * r2 * (gbest_params["t2"] - t2_)
        )
        t2_ += v_t2

        r1 = np.random.rand(n_particles)
        r2 = np.random.rand(n_particles)
        v_gamma = (
            W * v_gamma
            + C1 * r1 * (pbest_gamma - gamma_)
            + C2 * r2 * (gbest_params["gamma"] - gamma_)
        )
        gamma_ += v_gamma

        r1 = np.random.rand(n_particles)
        r2 = np.random.rand(n_particles)
        v_mu = (
            W * v_mu + C1 * r1 * (pbest_mu - mu_) + C2 * r2 * (gbest_params["mu"] - mu_)
        )
        mu_ += v_mu

        # 6) clip
        beta1 = np.clip(beta1, bounds_beta1[0], bounds_beta1[1])
        beta2 = np.clip(beta2, bounds_beta2[0], bounds_beta2[1])
        t1_ = np.clip(t1_, bounds_t1[0], bounds_t1[1])
        t2_ = np.clip(t2_, bounds_t2[0], bounds_t2[1])
        gamma_ = np.clip(gamma_, bounds_gamma[0], bounds_gamma[1])
        mu_ = np.clip(mu_, bounds_mu[0], bounds_mu[1])

        # 7) Copying back to the GPU
        beta1_dev.copy_to_device(beta1.astype(np.float32))
        beta2_dev.copy_to_device(beta2.astype(np.float32))
        t1_dev.copy_to_device(t1_.astype(np.float32))
        t2_dev.copy_to_device(t2_.astype(np.float32))
        gamma_dev.copy_to_device(gamma_.astype(np.float32))
        mu_dev.copy_to_device(mu_.astype(np.float32))

    return gbest_params, history

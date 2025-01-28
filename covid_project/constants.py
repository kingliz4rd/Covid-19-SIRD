"""Let's define constants that is used within the implementation."""

# PSO
W = 0.5  # Innertia coefficient
C1 = 0.5  # Cognitive coefficient
C2 = 0.5  # Social coefficient
MAX_ITER = 100  # Maximal number of iterations
NUM_PARTICLES = 10_000  # Number of particles

DT = 0.5  # sub step = 0.5 => 2 Euler sub steps for 1 day
SUBSTEPS = 2  # 2 sub-steps of 0.5 = 1 day

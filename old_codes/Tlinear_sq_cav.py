import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import sys
import time
from matplotlib import cm
from numba import njit

np.set_printoptions(threshold=sys.maxsize)
pd.set_option("display.max_rows", None, "display.max_columns", None)
pd.set_option('display.expand_frame_repr', False)
folder_nr = 'gallium_Tlinear'

# Define constants
# # Physical parameters water
# L = 0.1             # Length of cavity (m)
# H = L               # Height of cavity (m)
# g = 9.81            # Gravitational acceleration (m/s^2)
# Time = 400         # (s)
# nu = 1e-6           # Kinematic viscosity (m^2/s)
# alpha = 1.44e-7     # Thermal diffusivity (m^2/s)
# lbda = 0.6          # Thermal conductivity (W/m K)
# rho0 = 1e3          # Density (kg/m^3)
# beta = 210e-6       # Thermal expansion (1/K)
# Lat = 334e3         # Latent heat (J/kg)
# c_p = 4.2e3         # Specific heat (J/(kgK))
# Tm = 273.15         # Melting point (K)
#
# # Domain parameters
# T0 = 275          # Starting temperature (K)
# T_H = 285         # Hot wall temperature (K)
# T_C = 275         # Hot wall temperature (K)
# epsilon = 0.05 * (T_H - T_C)  # Width mushy zone (K)
# umax = np.sqrt(g * beta * (T_H - T0) * L)           # Maximal velocity

# Physical parameters gallium
Time = 1080         # (s)
L = 0.0889             # Length of cavity (m)
H = 0.714*L      # Height of cavity (m)
g = 9.81            # Gravitational acceleration (m/s^2)
rho0 = 6.093e3      # Density (kg/m^3)
lbda = 33           # Thermal conductivity (W/m K)
mu = 1.81e-3        # Dynamic viscosity (Ns/m^2)
nu = mu / rho0      # Kinematic viscosity (m^2/s)
beta = 1.2e-4       # Thermal expansion (1/K)
Lat = 8.016e5       # Latent heat (J/kg)
c_p = 381           # Specific heat (J/(kgK))
alpha = lbda / (rho0 * c_p)     # Thermal diffusivity (m^2/s)
Tm = 302.8          # Melting point (K)

# Domain parameters
T0 = 301.3          # Starting temperature (K)
T_H = 311           # Hot wall temperature (K)
T_C = 301.3         # Hot wall temperature (K)
epsilon = 0.05 * (T_H - T_C)  # Width mushy zone (K)
umax = np.sqrt(g * beta * (T_H - T0) * H)           # Maximal velocity
print(umax)

# Dimensionless numbers
Re = umax * H / nu                                  # Reynolds number
Ra = beta * (T_H - T0) * g * H**3 / (nu * alpha)    # Rayleigh number
print('Ra', Ra)
Pr = nu / alpha                                     # Prandtl number
Ma = 0.1                                            # Mach number

# Choose simulation parameters
Lambda = 1/4        # Magic parameter
tau_plus = 0.5005     # Even relaxation time
rho0_sim = 1        # Starting simulation density
Nx = 40             # Nodes in y-direction
Ny = np.int(0.714*Nx)

dx_sim = 1          # simulation length
dt_sim = 1          # simulation time
c_s = (1 / np.sqrt(3)) * (dx_sim / dt_sim)              # Simulation speed of sound
nu_sim = c_s**2 * (tau_plus - 1 / 2)                    # Simulation viscosity
print('nu_sim', nu_sim)

# Determine dependent parameters
umax_sim = Re * nu_sim / Ny                             # Maximal simulation density
print('umax_sim', umax_sim)
tau_minus = dt_sim * (Lambda / (tau_plus / dt_sim - 1/2) + 1/2)
alpha_sim = nu_sim / Pr

# if alpha_sim > 1/6:
#     print(f"alpha too large ({alpha_sim}), unstable temperature")

# Calculate conversion parameters
dx = L / Nx                                             # Distance
dt = (c_s ** 2) * (tau_plus - 1 / 2) * ((dx ** 2) / nu)       # Time
print(dx, dt)
Cu = dx / dt                                            # Velocity
Cg = dx / dt**2                                         # Acceleration
Crho = rho0 / rho0_sim                                  # Density
CF = Crho * Cg                                          # Force
Ch = dx**2 / dt**2                                      # Specific enthalpy

# D2Q9 lattice constants
c_i = np.array([[0, 0], [1, 0], [0, 1], [-1, 0], [0, -1], [1, 1], [-1, 1], [-1, -1], [1, -1]], dtype=np.int)
c_opp = np.array([0, 3, 4, 1, 2, 7, 8, 5, 6], dtype=np.int)
w_i = np.array([4/9, 1/9, 1/9, 1/9, 1/9, 1/36, 1/36, 1/36, 1/36])
q = 9                               # number of directions

# Grid and time steps
Ny = np.int(H/dx)                                 # Number of lattice nodes in x-direction
Nt = np.int(Time / dt)                  # Number of time steps
print('Nt', Nt)

# Forces
g_sim = g / Cg * np.array([0, -1])   # Simulation acceleration vector

# Initial conditions
dim = (Nx, Ny)
ux = np.zeros(dim)                 # Simulation velocity in x direction
uy = np.zeros(dim)                 # Simulation velocity in y direction
rho_sim = rho0_sim * np.ones(dim)  # Simulation density
T_dim = np.zeros((Nx+2, Ny+2))     # Dimensionless simulation temperature
f_l = np.zeros(dim)                # Liquid fraction
h = (c_p * T0) * np.ones(dim)        # Enthalpy
c_app = c_p * np.ones(dim)

# Temperature BCS
T_dim_H = np.ones(Ny+2) * beta * (T_H - T0)
T_dim_C = np.ones(Ny+2) * beta * (T_C - T0)

def easy_view(nr, arr):
    idx = ["idx" for i in arr[1, :]]
    col = ["col" for j in arr[:, 1]]

    dataset = pd.DataFrame(arr.T, index=idx, columns=col)
    print(nr, dataset)

@njit
def fluid(Nx, Ny, f_plus, f_minus, f_star):
    for i in range(1, Nx-1):
        f_plus[i, 1:Ny-1, 0] = f_star[i, 1:Ny-1, 0]
        f_plus[i, 1:Ny-1, 1] = (f_star[i-1, 1:Ny-1, 1] + f_star[i+1, 1:Ny-1, 3]) / 2
        f_plus[i, 1:Ny-1, 2] = (f_star[i, 0:Ny-2, 2] + f_star[i, 2:Ny, 4]) / 2
        f_plus[i, 1:Ny-1, 3] = f_plus[i, 1:Ny-1, 1]
        f_plus[i, 1:Ny-1, 4] = f_plus[i, 1:Ny-1, 2]
        f_plus[i, 1:Ny-1, 5] = (f_star[i-1, 0:Ny-2, 5] + f_star[i+1, 2:Ny, 7]) / 2
        f_plus[i, 1:Ny-1, 6] = (f_star[i+1, 0:Ny-2, 6] + f_star[i-1, 2:Ny, 8]) / 2
        f_plus[i, 1:Ny-1, 7] = f_plus[i, 1:Ny-1, 5]
        f_plus[i, 1:Ny-1, 8] = f_plus[i, 1:Ny-1, 6]

        f_minus[i, 1:Ny-1, 0] = 0
        f_minus[i, 1:Ny-1, 1] = (f_star[i-1, 1:Ny-1, 1] - f_star[i+1, 1:Ny-1, 3]) / 2
        f_minus[i, 1:Ny-1, 2] = (f_star[i, 0:Ny-2, 2] - f_star[i, 2:Ny, 4]) / 2
        f_minus[i, 1:Ny-1, 3] = -f_minus[i, 1:Ny-1, 1]
        f_minus[i, 1:Ny-1, 4] = -f_minus[i, 1:Ny-1, 2]
        f_minus[i, 1:Ny-1, 5] = (f_star[i-1, 0:Ny-2, 5] - f_star[i+1, 2:Ny, 7]) / 2
        f_minus[i, 1:Ny-1, 6] = (f_star[i+1, 0:Ny-2, 6] - f_star[i-1, 2:Ny, 8]) / 2
        f_minus[i, 1:Ny-1, 7] = -f_minus[i, 1:Ny-1, 5]
        f_minus[i, 1:Ny-1, 8] = -f_minus[i, 1:Ny-1, 6]

    return f_plus, f_minus

@njit
def left_wall(Ny, f_plus, f_minus, f_star):
    i = 0

    f_plus[i, 1:Ny-1, 0] = f_star[i, 1:Ny-1, 0]
    f_plus[i, 1:Ny-1, 1] = (f_star[i, 1:Ny-1, 3] + f_star[i+1, 1:Ny-1, 3]) / 2      # Bounce
    f_plus[i, 1:Ny-1, 2] = (f_star[i, 0:Ny-2, 2] + f_star[i, 2:Ny, 4]) / 2
    f_plus[i, 1:Ny-1, 3] = f_plus[i, 1:Ny-1, 1]
    f_plus[i, 1:Ny-1, 4] = f_plus[i, 1:Ny-1, 2]
    f_plus[i, 1:Ny-1, 5] = (f_star[i, 1:Ny-1, 7] + f_star[i+1, 2:Ny, 7]) / 2        # Bounce
    f_plus[i, 1:Ny-1, 6] = (f_star[i+1, 0:Ny-2, 6] + f_star[i, 1:Ny-1, 6]) / 2
    f_plus[i, 1:Ny-1, 7] = f_plus[i, 1:Ny-1, 5]
    f_plus[i, 1:Ny-1, 8] = f_plus[i, 1:Ny-1, 6]                                     # Bounce

    f_minus[i, 1:Ny-1, 0] = 0
    f_minus[i, 1:Ny-1, 1] = (f_star[i, 1:Ny-1, 3] - f_star[i+1, 1:Ny-1, 3]) / 2     # Bounce
    f_minus[i, 1:Ny-1, 2] = (f_star[i, 0:Ny-2, 2] - f_star[i, 2:Ny, 4]) / 2
    f_minus[i, 1:Ny-1, 3] = -f_minus[i, 1:Ny-1, 1]
    f_minus[i, 1:Ny-1, 4] = -f_minus[i, 1:Ny-1, 2]
    f_minus[i, 1:Ny-1, 5] = (f_star[i, 1:Ny-1, 7] - f_star[i+1, 2:Ny, 7]) / 2       # Bounce
    f_minus[i, 1:Ny-1, 6] = (f_star[i+1, 0:Ny-2, 6] - f_star[i, 1:Ny-1, 6]) / 2
    f_minus[i, 1:Ny-1, 7] = -f_minus[i, 1:Ny-1, 5]
    f_minus[i, 1:Ny-1, 8] = -f_minus[i, 1:Ny-1, 6]                                  # Bounce

    return f_plus, f_minus

@njit
def right_wall(Nx, Ny, f_plus, f_minus, f_star):
    i = Nx - 1

    f_plus[i, 1:Ny-1, 0] = f_star[i, 1:Ny-1, 0]
    f_plus[i, 1:Ny-1, 1] = (f_star[i-1, 1:Ny-1, 1] + f_star[i, 1:Ny-1, 1]) / 2      # Bounce
    f_plus[i, 1:Ny-1, 2] = (f_star[i, 0:Ny-2, 2] + f_star[i, 2:Ny, 4]) / 2
    f_plus[i, 1:Ny-1, 3] = f_plus[i, 1:Ny-1, 1]
    f_plus[i, 1:Ny-1, 4] = f_plus[i, 1:Ny-1, 2]
    f_plus[i, 1:Ny-1, 5] = (f_star[i-1, 0:Ny-2, 5] + f_star[i, 1:Ny-1, 5]) / 2
    f_plus[i, 1:Ny-1, 6] = (f_star[i, 1:Ny-1, 8] + f_star[i-1, 2:Ny, 8]) / 2        # Bounce
    f_plus[i, 1:Ny-1, 7] = f_plus[i, 1:Ny-1, 5]                                     # Bounce
    f_plus[i, 1:Ny-1, 8] = f_plus[i, 1:Ny-1, 6]

    f_minus[i, 1:Ny-1, 0] = 0
    f_minus[i, 1:Ny-1, 1] = (f_star[i-1, 1:Ny-1, 1] - f_star[i, 1:Ny-1, 1]) / 2     # Bounce
    f_minus[i, 1:Ny-1, 2] = (f_star[i, 0:Ny-2, 2] - f_star[i, 2:Ny, 4]) / 2
    f_minus[i, 1:Ny-1, 3] = -f_minus[i, 1:Ny-1, 1]
    f_minus[i, 1:Ny-1, 4] = -f_minus[i, 1:Ny-1, 2]
    f_minus[i, 1:Ny-1, 5] = (f_star[i-1, 0:Ny-2, 5] - f_star[i, 1:Ny-1, 5]) / 2
    f_minus[i, 1:Ny-1, 6] = (f_star[i, 1:Ny-1, 8] - f_star[i-1, 2:Ny, 8]) / 2       # Bounce
    f_minus[i, 1:Ny-1, 7] = -f_minus[i, 1:Ny-1, 5]                                  # Bounce
    f_minus[i, 1:Ny-1, 8] = -f_minus[i, 1:Ny-1, 6]

    return f_plus, f_minus

@njit
def lower_wall(Nx, f_plus, f_minus, f_star):
    j = 0

    f_plus[1:Nx-1, j, 0] = f_star[1:Nx-1, j, 0]
    f_plus[1:Nx-1, j, 1] = (f_star[0:Nx-2, j, 1] + f_star[2:Nx, j, 3]) / 2
    f_plus[1:Nx-1, j, 2] = (f_star[1:Nx-1, j, 4] + f_star[1:Nx-1, j+1, 4]) / 2      # Bounce
    f_plus[1:Nx-1, j, 3] = f_plus[1:Nx-1, j, 1]
    f_plus[1:Nx-1, j, 4] = f_plus[1:Nx-1, j, 2]
    f_plus[1:Nx-1, j, 5] = (f_star[1:Nx-1, j, 7] + f_star[2:Nx, j+1, 7]) / 2        # Bounce
    f_plus[1:Nx-1, j, 6] = (f_star[1:Nx-1, j, 8] + f_star[0:Nx-2, j+1, 8]) / 2      # Bounce
    f_plus[1:Nx-1, j, 7] = f_plus[1:Nx-1, j, 5]
    f_plus[1:Nx-1, j, 8] = f_plus[1:Nx-1, j, 6]

    f_minus[1:Nx-1, j, 0] = 0
    f_minus[1:Nx-1, j, 1] = (f_star[0:Nx-2, j, 1] - f_star[2:Nx, j, 3]) / 2
    f_minus[1:Nx-1, j, 2] = (f_star[1:Nx-1, j, 4] - f_star[1:Nx-1, j+1, 4]) / 2      # Bounce
    f_minus[1:Nx-1, j, 3] = -f_minus[1:Nx-1, j, 1]
    f_minus[1:Nx-1, j, 4] = -f_minus[1:Nx-1, j, 2]
    f_minus[1:Nx-1, j, 5] = (f_star[1:Nx-1, j, 7] - f_star[2:Nx, j+1, 7]) / 2        # Bounce
    f_minus[1:Nx-1, j, 6] = (f_star[1:Nx-1, j, 8] - f_star[0:Nx-2, j+1, 8]) / 2      # Bounce
    f_minus[1:Nx-1, j, 7] = -f_minus[1:Nx-1, j, 5]
    f_minus[1:Nx-1, j, 8] = -f_minus[1:Nx-1, j, 6]

    return f_plus, f_minus

@njit
def upper_wall(Nx, Ny, f_plus, f_minus, f_star):
    j = Ny - 1

    f_plus[1:Nx-1, j, 0] = f_star[1:Nx-1, j, 0]
    f_plus[1:Nx-1, j, 1] = (f_star[0:Nx-2, j, 1] + f_star[2:Nx, j, 3]) / 2
    f_plus[1:Nx-1, j, 2] = (f_star[1:Nx-1, j-1, 2] + f_star[1:Nx-1, j, 2]) / 2
    f_plus[1:Nx-1, j, 3] = f_plus[1:Nx-1, j, 1]
    f_plus[1:Nx-1, j, 4] = f_plus[1:Nx-1, j, 2]
    f_plus[1:Nx-1, j, 5] = (f_star[0:Nx-2, j-1, 5] + f_star[1:Nx-1, j, 5]) / 2
    f_plus[1:Nx-1, j, 6] = (f_star[2:Nx, j-1, 6] + f_star[1:Nx-1, j, 6]) / 2
    f_plus[1:Nx-1, j, 7] = f_plus[1:Nx-1, j, 5]
    f_plus[1:Nx-1, j, 8] = f_plus[1:Nx-1, j, 6]

    f_minus[1:Nx-1, j, 0] = 0
    f_minus[1:Nx-1, j, 1] = (f_star[0:Nx-2, j, 1] - f_star[2:Nx, j, 3]) / 2
    f_minus[1:Nx-1, j, 2] = (f_star[1:Nx-1, j-1, 2] - f_star[1:Nx-1, j, 2]) / 2
    f_minus[1:Nx-1, j, 3] = -f_minus[1:Nx-1, j, 1]
    f_minus[1:Nx-1, j, 4] = -f_minus[1:Nx-1, j, 2]
    f_minus[1:Nx-1, j, 5] = (f_star[0:Nx-2, j-1, 5] - f_star[1:Nx-1, j, 5]) / 2
    f_minus[1:Nx-1, j, 6] = (f_star[2:Nx, j-1, 6] - f_star[1:Nx-1, j, 6]) / 2
    f_minus[1:Nx-1, j, 7] = -f_minus[1:Nx-1, j, 5]
    f_minus[1:Nx-1, j, 8] = -f_minus[1:Nx-1, j, 6]

    return f_plus, f_minus

@njit
def lower_left_corner(f_plus, f_minus, f_star):
    i = 0
    j = 0

    f_plus[i, j, 0] = f_star[i, j, 0]
    f_plus[i, j, 1] = (f_star[i, j, 3] + f_star[i+1, j, 3]) / 2
    f_plus[i, j, 2] = (f_star[i, j, 4] + f_star[i, j+1, 4]) / 2
    f_plus[i, j, 3] = f_plus[i, j, 1]
    f_plus[i, j, 4] = f_plus[i, j, 2]
    f_plus[i, j, 5] = (f_star[i, j, 7] + f_star[i+1, j+1, 7]) / 2
    f_plus[i, j, 6] = (f_star[i, j, 8] + f_star[i, j, 6]) / 2
    f_plus[i, j, 7] = f_plus[i, j, 5]
    f_plus[i, j, 8] = f_plus[i, j, 6]

    f_minus[i, j, 0] = 0
    f_minus[i, j, 1] = (f_star[i, j, 3] - f_star[i+1, j, 3]) / 2
    f_minus[i, j, 2] = (f_star[i, j, 4] - f_star[i, j+1, 4]) / 2
    f_minus[i, j, 3] = -f_minus[i, j, 1]
    f_minus[i, j, 4] = -f_minus[i, j, 2]
    f_minus[i, j, 5] = (f_star[i, j, 7] - f_star[i+1, j+1, 7]) / 2
    f_minus[i, j, 6] = (f_star[i, j, 8] - f_star[i, j, 6]) / 2
    f_minus[i, j, 7] = -f_minus[i, j, 5]
    f_minus[i, j, 8] = -f_minus[i, j, 6]

    return f_plus, f_minus

@njit
def lower_right_corner(Nx, f_plus, f_minus, f_star):
    i = Nx - 1
    j = 0

    f_plus[i, j, 0] = f_star[i, j, 0]
    f_plus[i, j, 1] = (f_star[i-1, j, 1] + f_star[i, j, 1]) / 2
    f_plus[i, j, 2] = (f_star[i, j, 4] + f_star[i, j+1, 4]) / 2
    f_plus[i, j, 3] = f_plus[i, j, 1]
    f_plus[i, j, 4] = f_plus[i, j, 2]
    f_plus[i, j, 5] = (f_star[i, j, 7] + f_star[i, j, 5]) / 2
    f_plus[i, j, 6] = (f_star[i, j, 8] + f_star[i-1, j+1, 8]) / 2
    f_plus[i, j, 7] = f_plus[i, j, 5]
    f_plus[i, j, 8] = f_plus[i, j, 6]

    f_minus[i, j, 0] = 0
    f_minus[i, j, 1] = (f_star[i-1, j, 1] - f_star[i, j, 1]) / 2
    f_minus[i, j, 2] = (f_star[i, j, 4] - f_star[i, j+1, 4]) / 2
    f_minus[i, j, 3] = -f_minus[i, j, 1]
    f_minus[i, j, 4] = -f_minus[i, j, 2]
    f_minus[i, j, 5] = (f_star[i, j, 7] - f_star[i, j, 5]) / 2
    f_minus[i, j, 6] = (f_star[i, j, 8] - f_star[i-1, j+1, 8]) / 2
    f_minus[i, j, 7] = -f_minus[i, j, 5]
    f_minus[i, j, 8] = -f_minus[i, j, 6]

    return f_plus, f_minus

@njit
def upper_left_corner(f_plus, f_minus, f_star):
    i = 0
    j = Ny - 1

    f_plus[i, j, 0] = f_star[i, j, 0]
    f_plus[i, j, 1] = (f_star[i, j, 3] + f_star[i+1, j, 3]) / 2
    f_plus[i, j, 2] = (f_star[i, j-1, 2] + f_star[i, j, 2]) / 2
    f_plus[i, j, 3] = f_plus[i, j, 1]
    f_plus[i, j, 4] = f_plus[i, j, 2]
    f_plus[i, j, 5] = (f_star[i, j, 7] + f_star[i, j, 5]) / 2
    f_plus[i, j, 6] = (f_star[i+1, j-1, 6] + f_star[i, j, 6]) / 2
    f_plus[i, j, 7] = f_plus[i, j, 5]
    f_plus[i, j, 8] = f_plus[i, j, 6]

    f_minus[i, j, 0] = 0
    f_minus[i, j, 1] = (f_star[i, j, 3] - f_star[i+1, j, 3]) / 2
    f_minus[i, j, 2] = (f_star[i, j-1, 2] - f_star[i, j, 2]) / 2
    f_minus[i, j, 3] = -f_minus[i, j, 1]
    f_minus[i, j, 4] = -f_minus[i, j, 2]
    f_minus[i, j, 5] = (f_star[i, j, 7] - f_star[i, j, 5]) / 2
    f_minus[i, j, 6] = (f_star[i+1, j-1, 6] - f_star[i, j, 6]) / 2
    f_minus[i, j, 7] = -f_minus[i, j, 5]
    f_minus[i, j, 8] = -f_minus[i, j, 6]

    return f_plus, f_minus

@njit
def upper_right_corner(f_plus, f_minus, f_star):
    i = Nx - 1
    j = Ny - 1

    f_plus[i, j, 0] = f_star[i, j, 0]
    f_plus[i, j, 1] = (f_star[i-1, j, 1] + f_star[i-1, j, 1]) / 2
    f_plus[i, j, 2] = (f_star[i, j-1, 2] + f_star[i, j, 2]) / 2
    f_plus[i, j, 3] = f_plus[i, j, 1]
    f_plus[i, j, 4] = f_plus[i, j, 2]
    f_plus[i, j, 5] = (f_star[i-1, j-1, 5] + f_star[i, j, 5]) / 2
    f_plus[i, j, 6] = (f_star[i, j, 8] + f_star[i, j, 6]) / 2
    f_plus[i, j, 7] = f_plus[i, j, 5]
    f_plus[i, j, 8] = f_plus[i, j, 6]

    f_minus[i, j, 0] = 0
    f_minus[i, j, 1] = (f_star[i-1, j, 1] - f_star[i-1, j, 1]) / 2
    f_minus[i, j, 2] = (f_star[i, j-1, 2] - f_star[i, j, 2]) / 2
    f_minus[i, j, 3] = -f_minus[i, j, 1]
    f_minus[i, j, 4] = -f_minus[i, j, 2]
    f_minus[i, j, 5] = (f_star[i-1, j-1, 5] - f_star[i, j, 5]) / 2
    f_minus[i, j, 6] = (f_star[i, j, 8] - f_star[i, j, 6]) / 2
    f_minus[i, j, 7] = -f_minus[i, j, 5]
    f_minus[i, j, 8] = -f_minus[i, j, 6]

    return f_plus, f_minus

def streaming(Nx, Ny, f_plus, f_minus, f_star):
    f_plus, f_minus = fluid(Nx, Ny, f_plus, f_minus, f_star)
    f_plus, f_minus = left_wall(Ny, f_plus, f_minus, f_star)
    f_plus, f_minus = right_wall(Nx, Ny, f_plus, f_minus, f_star)
    f_plus, f_minus = lower_wall(Nx, f_plus, f_minus, f_star)
    f_plus, f_minus = upper_wall(Nx, Ny, f_plus, f_minus, f_star)
    f_plus, f_minus = lower_left_corner(f_plus, f_minus, f_star)
    f_plus, f_minus = lower_right_corner(Nx, f_plus, f_minus, f_star)
    f_plus, f_minus = upper_left_corner(f_plus, f_minus, f_star)
    f_plus, f_minus = upper_right_corner(f_plus, f_minus, f_star)

    return f_plus, f_minus

@njit
def f_equilibrium(w_i, rho, ux, uy, c_i, q, c_s):
    f_eq_plus = np.zeros((Nx, Ny, q))                                   # Initialize even and odd parts of f_eq
    f_eq_minus = np.zeros((Nx, Ny, q))

    u_dot_u = ux**2 + uy**2                                             # Inner product of u with itself

    for i in range(q):                                                  # Loop over all directions of Q
        if i == 0:                                                      # If-statement for symmetry arguments
            u_dot_c = ux * c_i[i, 0] + uy * c_i[i, 1]                   # Inner product of u with c_i
            f_eq_plus[:, :, i] = w_i[i] * rho * (1 + (u_dot_c[:, :] / c_s**2) + (u_dot_c[:, :]**2 / (2 * c_s**4)) - (u_dot_u / (2 * c_s**2)))
        elif i in [1, 2, 5, 6]:
            u_dot_c = ux * c_i[i, 0] + uy * c_i[i, 1]
            f_eq_plus[:, :, i] = w_i[i] * rho * (1 + (u_dot_c[:, :]**2 / (2 * c_s**4)) - (u_dot_u / (2 * c_s**2)))      # Even part of f_eq
            f_eq_minus[:, :, i] = w_i[i] * rho * (u_dot_c[:, :] / c_s**2)                                               # Odd part of f_eq
        else:
            f_eq_plus[:, :, i] = f_eq_plus[:, :, c_opp[i]]
            f_eq_minus[:, :, i] = -f_eq_minus[:, :, c_opp[i]]

    return f_eq_plus, f_eq_minus

@njit
def force_source(ux, uy, F):
    Fi = np.zeros((Nx, Ny, q))                                              # Initialize forcing and source terms
    Si = np.zeros((Nx, Ny, q))
    # easy_view("uy", uy)
    # easy_view("F", F[:, :, 1])

    u_dot_F = ux * F[:, :, 0] + uy * F[:, :, 1]                             # Inner product of u with F

    for i in range(q):
        u_dot_c = ux * c_i[i, 0] + uy * c_i[i, 1]                           # Inner product of u with c_i

        Fi[:, :, i] = F[:, :, 0] * c_i[i, 0] + F[:, :, 1] * c_i[i, 1]       # Inner product of F with c_i
        Si[:, :, i] = (1 - 1/(2*tau_plus)) * w_i[i] * (u_dot_c[:, :] * Fi[:, :, i] / c_s**4 - u_dot_F / c_s**2) + (1 - 1/(2*tau_minus)) * w_i[i] * Fi[:, :, i] / c_s**2   # Source term

    return Si

# @njit
def temperature(T_old_dim, h_old, c_app_old, f_l_old, ux_sim, uy_sim, t, T_dim_C, T_dim_H):
    T_new = np.zeros((Nx+2, Ny+2))
    l_relax = 1

    c_s = c_p
    c_l = c_p
    Ts = Tm - epsilon
    Tl = Tm + epsilon

    h_s = c_s * Ts
    h_l = h_s + Lat + (c_s + c_l) / 2 * (Tl - Ts)

    T_H = T_dim_H / beta + T0
    T_C = T_dim_C / beta + T0

    ux = ux_sim * dx / dt
    uy = uy_sim * dx / dt

    # easy_view(t, T_old_dim)

    def energy_eq(i, j, T, ux, uy, c_app, h, h_old):
        T_new = T[i, j] - (h[i-1, j-1] - h_old[i-1, j-1]) / c_app[i-1, j-1] \
                + (lbda * dt / (c_app[i-1, j-1] * rho0 * dx**2)) * (2 * (T[i+1, j] + T[i-1, j] + T[i, j+1] + T[i, j-1]) - 1/2 * (T[i+1, j+1] + T[i-1, j+1] + T[i-1, j-1] + T[i+1, j-1]) - 6 * T[i, j]) \
                - (c_p * dt / (c_app[i-1, j-1] * dx) * (ux[i-1, j-1] * (T[i+1, j] - T[i-1, j] - 1/4 * (T[i+1, j+1] - T[i-1, j+1] + T[i+1, j-1] - T[i-1, j-1])) \
                + uy[i-1, j-1] * (T[i, j+1] - T[i, j-1] - 1/4 * (T[i+1, j+1] - T[i+1, j-1] + T[i-1, j+1] - T[i-1, j-1]))))

        return T_new

    while True:
        f_l_iter = -2
        mask = (f_l_old - f_l_iter) < 0

        T_iter = T_old_dim / beta + T0
        h_iter = h_old.copy()
        c_app_iter = c_app_old.copy()
        f_l = f_l_old.copy()

        n_iter = 1
        while True:
            for j in range(1, Ny+1):
                for i in range(1, Nx+1):
                    if mask[i-1, j-1]:
                        T_new[i, j] = T_iter[i, j]
                    else:
                        T_new[i, j] = energy_eq(i, j, T_iter, ux, uy, c_app_iter, h_iter, h_old)

            h_new = h_iter + l_relax * c_app_iter * (T_new[1:-1, 1:-1] - T_iter[1:-1, 1:-1])

            for j in range(1, Ny+1):
                for i in range(1, Nx+1):
                    if mask[i-1, j-1]:
                        c_app[i-1, j-1] = c_app_iter[i-1, j-1]
                        f_l[i-1, j-1] = f_l_iter[i-1, j-1]
                    else:
                        if h_new[i-1, j-1] < h_s:
                            T_new[i, j] = h_new[i-1, j-1] / c_s
                        elif h_new[i-1, j-1] > h_l:
                            T_new[i, j] = Tl + (h_new[i-1, j-1] - h_l) / c_l
                        else:
                            T_new[i, j] = Ts + ((h_new[i-1, j-1] - h_s) / (h_l - h_s)) * (Tl - Ts)

                        if T_new[i, j] < Ts:
                            c_app[i-1, j-1] = c_s
                            f_l[i-1, j-1] = 0
                        elif T_new[i, j] > Tl:
                            c_app[i-1, j-1] = c_l
                            f_l[i-1, j-1] = 1
                        else:
                            c_app[i-1, j-1] = c_s + (Lat / (Tl - Ts)) + (c_l - c_s) * (T_new[i, j] - Ts) / (Tl - Ts)
                            f_l[i-1, j-1] = (T_new[i, j] - Ts) / (Tl - Ts)

            # Ghost nodes
            T_new[1:-1, 0] = 21/23 * T_new[1:-1, 1] + 3/23 * T_new[1:-1, 2] - 1/23 * T_new[1:-1, 3]         # Neumann extrapolation on lower boundary
            T_new[1:-1, -1] = 21/23 * T_new[1:-1, -2] + 3/23 * T_new[1:-1, -3] - 1/23 * T_new[1:-1, -4]     # Neumann extrapolation on upper boundary
            # T_new[-1, :] = 21/23 * T_new[-2, :] + 3/23 * T_new[-3, :] - 1/23 * T_new[-4, :]               # Neumann extrapolation on right boundary
            T_new[0, :] = 16/5 * T_H - 3 * T_new[1, :] + T_new[2, :] - 1/5 * T_new[3, :]               # Dirichlet extrapolation on left boundary
            T_new[-1, :] = 16/5 * T_C - 3 * T_new[-2, :] + T_new[-3, :] - 1/5 * T_new[-4, :]           # Dirichlet extrapolation on right boundary

            if np.any(abs(f_l - f_l_iter)) < 1e-5:
                break
            elif (n_iter > 10) and (l_relax == 1):
                l_relax = 0.1
                break
            else:
                mask = (abs(f_l - f_l_iter) < 1e-5)
                T_iter = T_new.copy()
                h_iter = h_new.copy()
                c_app_iter = c_app.copy()
                f_l_iter = f_l.copy()

            n_iter += 1

        if np.any(abs(f_l - f_l_iter)) < 1e-5:
            # print(n_iter)
            break
        else:
            continue

    if t % 100 == 0:
        print(t, np.amax(uy_sim))
    #     # easy_view(t, uy_sim)
    #     # easy_view(t, ux_sim)
    #     # easy_view(t, T_new)
    #
    if t % 100 == 0:
        print('t', t)

    T_dim = beta * (T_new - T0)
    # easy_view(t, T_dim)

    return T_dim, h_new, c_app, f_l


f_plus, f_minus = f_equilibrium(w_i, rho_sim, ux, uy, c_i, q, c_s)          # Initialize distributions

start = time.time()

# Time stamps for plots
T_plot = np.array([120, 360, 600, 1020])
t_plot_float = T_plot / Time * Nt
t_plot_int = t_plot_float.astype(int).tolist()

for t in range(Nt):
    ### Forcing
    T_dim_phys = T_dim[1:-1, 1:-1]                                          # Select only physical domain w/out ghost nodes

    F_buoy = - (T_dim[1:-1, 1:-1, None] - np.mean(T_dim_phys)) * g_sim          # Calculate buoyancy force

    ### Moment update
    rho_sim = np.sum(f_plus, axis=2)                                        # Calculate density (even parts due to symmetry)

    B = (1 - f_l) * (tau_plus - 1/2) / (f_l + tau_plus - 1/2)               # Viscosity-dependent solid fraction
    ux = 1 * (np.sum(f_minus[:, :] * c_i[:, 0], axis=2) / rho_sim + (1 - B[:, :]) / 2 * F_buoy[:, :, 0])    # Calculate x velocity (odd parts due to symmetry)
    uy = 1 * (np.sum(f_minus[:, :] * c_i[:, 1], axis=2) / rho_sim + (1 - B[:, :]) / 2 * F_buoy[:, :, 1])    # Calculate y velocity (odd parts due to symmetry)

    # ux[np.round(B) == 1] = 0                                                # Force velocity in solid to zero
    # uy[B == 1] = 0

    ### Temperature
    ux_T = 1 * (np.sum(f_minus[:, :] * c_i[:, 0], axis=2) / rho_sim)    # Calculate x velocity (odd parts due to symmetry)
    uy_T = 1 * (np.sum(f_minus[:, :] * c_i[:, 1], axis=2) / rho_sim)    # Calculate y velocity (odd parts due to symmetry)
    T_dim, h, c_app, f_l = temperature(T_dim, h, c_app, f_l, ux_T, uy_T, t, T_dim_C, T_dim_H)                   # Calculate temperature and liquid fraction

    ### Equilibrium
    f_eq_plus, f_eq_minus = f_equilibrium(w_i, rho_sim, ux, uy, c_i, q, c_s)                                # Calculate new equilibrium distribution

    ### Source
    Si = force_source(ux, uy, F_buoy)                      # Calculate source term
    Bi = np.repeat(B[:, :, np.newaxis], q, axis=2)                          # Repeat B in all directions to make next calc possible

    ### Collision
    f_star = f_plus * (1 - (1-Bi) / tau_plus) + f_minus * (1 - 2*Bi - (1-Bi) / tau_minus) + f_eq_plus * (1-Bi) / tau_plus + f_eq_minus * (1-Bi) / tau_minus + Si * (1-Bi)

    ### Streaming
    f_plus, f_minus = streaming(Nx, Ny, f_plus, f_minus, f_star)

    ### Plots
    # if t > 12600 and (t % 100 == 0):
    # # if t in t_plot_int:
    #     ### Moment update
    #     rho_sim = np.sum(f_plus, axis=2)                                        # Calculate density (even parts due to symmetry)
    #
    #     B = (1 - f_l) * (tau_plus - 1/2) / (f_l + tau_plus - 1/2)               # Viscosity-dependent solid fraction
    #     ux = 1 * (np.sum(f_minus[:, :] * c_i[:, 0], axis=2) / rho_sim + (1 - B[:, :]) / 2 * F_buoy[:, :, 0])    # Calculate x velocity (odd parts due to symmetry)
    #     uy = 1 * (np.sum(f_minus[:, :] * c_i[:, 1], axis=2) / rho_sim + (1 - B[:, :]) / 2 * F_buoy[:, :, 1])    # Calculate y velocity (odd parts due to symmetry)
    #
    #     ux[np.round(B) == 1] = 0                                                # Force velocity in solid to zero
    #     uy[B == 1] = 0
    #
    #     T = T_dim / beta + T0
    #
    #     # Liquid fraction
    #     plt.figure()
    #     plt.imshow(f_l.T, cmap=cm.autumn, origin='lower', aspect=1.0)
    #     plt.xlabel('$x$ (# lattice nodes)')
    #     plt.ylabel('$y$ (# lattice nodes)')
    #     plt.title(f'Gallium \n $f_l$, left wall at $T={T_H}K$, $t={np.round(t/Nt*Time, decimals=2)}s$')
    #     plt.colorbar()
    #     plt.savefig(f"Figures/hsource_trt-fsm_sq_cav/{folder_nr}/heatmap_fl_t={np.round(t/Nt*Time, decimals=2)}_N{Ny}.png")
    #
    #     # Velocities
    #     plt.figure()
    #     plt.clf()
    #     plt.imshow(np.flip(uy, axis=1).T, cmap=cm.Blues)
    #     plt.xlabel('$x$ (# lattice nodes)')
    #     plt.ylabel('$y$ (# lattice nodes)')
    #     plt.title(f'Gallium \n $u_y$, left wall at $T={T_H}K$, $t={np.round(t/Nt*Time, decimals=2)}s$')
    #     plt.colorbar()
    #     plt.savefig(f"Figures/hsource_trt-fsm_sq_cav/{folder_nr}/heatmap_uy_t={np.round(t/Nt*Time, decimals=2)}_N{Ny}.png")
    #
    #     plt.figure()
    #     plt.clf()
    #     plt.imshow(ux.T, cmap=cm.Blues, origin='lower')
    #     plt.xlabel('$x$ (# lattice nodes)')
    #     plt.ylabel('$y$ (# lattice nodes)')
    #     plt.title(f'Gallium \n $u_x$, left wall at $T={T_H}K$, $t={np.round(t/Nt*Time, decimals=2)}s$')
    #     plt.colorbar()
    #     plt.savefig(f"Figures/hsource_trt-fsm_sq_cav/{folder_nr}/heatmap_ux_t={np.round(t/Nt*Time, decimals=3)}_N{Ny}.png")
    #
    #     ## Temperature heatmap
    #     plt.figure()
    #     plt.clf()
    #     plt.imshow(np.flip(T[1:-1, 1:-1].T, axis=0), cmap=cm.Blues)
    #     plt.xlabel('$x$ (# lattice nodes)')
    #     plt.ylabel('$y$ (# lattice nodes)')
    #     plt.title(f'Gallium \n $T$, left wall at $T={T_H}K$, $t={np.round(t/Nt*Time, decimals=2)}s$')
    #     plt.colorbar()
    #     plt.savefig(f"Figures/hsource_trt-fsm_sq_cav/{folder_nr}/heatmap_T_t={np.round(t/Nt*Time, decimals=3)}_N{Ny}.png")
    #
    #     # plt.figure()
    #     # plt.clf()
    #     # plt.imshow(np.flip(rho_sim, axis=1).T, cmap=cm.Blues)
    #     # plt.xlabel('$x$ (# lattice nodes)')
    #     # plt.ylabel('$y$ (# lattice nodes)')
    #     # plt.title(f'$\\rho$ in cavity with left wall at $T={T_H}K$')
    #     # plt.colorbar()
    #     # plt.savefig(f"Figures/hsource_trt-fsm_sq_cav/{folder_nr}/heatmap_rho_time{Time}_t={np.round(t/Nt*Time, decimals=3)}.png")
    #
    #     # Vector plot
    #     plt.figure()
    #     plt.quiver(Cu*ux.T, Cu*uy.T)
    #     plt.xlabel('$x$ (# lattice nodes)')
    #     plt.ylabel('$y$ (# lattice nodes)')
    #     plt.title(f'Gallium \n $u$ in pipe with left wall at $T={T_H}K$, $t={np.round(t/Nt*Time, decimals=2)}s$')
    #     # plt.legend('Velocity vector')
    #     plt.savefig(f"Figures/hsource_trt-fsm_sq_cav/{folder_nr}/arrowplot_t={np.round(t/Nt*Time, decimals=3)}_N{Ny}.png")
    #
    #     plt.close('all')

    # if t in t_plot_int:
    if t % 3000 == 0:
        ### Moment update
        rho_sim = np.sum(f_plus, axis=2)                                        # Calculate density (even parts due to symmetry)

        B = (1 - f_l) * (tau_plus - 1/2) / (f_l + tau_plus - 1/2)               # Viscosity-dependent solid fraction
        ux = 1 * (np.sum(f_minus[:, :] * c_i[:, 0], axis=2) / rho_sim)    # Calculate x velocity (odd parts due to symmetry)
        uy = 1 * (np.sum(f_minus[:, :] * c_i[:, 1], axis=2) / rho_sim)    # Calculate y velocity (odd parts due to symmetry)

        ux[np.round(B) == 1] = 0                                                # Force velocity in solid to zero
        uy[B == 1] = 0

        T = T_dim / beta + T0

        # Liquid fraction
        plt.figure()
        plt.imshow(f_l.T, cmap=cm.autumn, origin='lower', aspect=1.0)
        plt.xlabel('$x$ (# lattice nodes)')
        plt.ylabel('$y$ (# lattice nodes)')
        plt.title(f'Gallium \n $f_l$, left wall at $T={T_H}K$, $t={np.round(t/Nt*Time, decimals=2)}s$')
        plt.colorbar()
        plt.savefig(f"Figures/hsource_trt-fsm_sq_cav/{folder_nr}/heatmap_fl_t={np.round(t/Nt*Time, decimals=2)}_N{Ny}.png")

        # Velocities
        plt.figure()
        plt.clf()
        plt.imshow(np.flip(uy, axis=1).T, cmap=cm.Blues)
        plt.xlabel('$x$ (# lattice nodes)')
        plt.ylabel('$y$ (# lattice nodes)')
        plt.title(f'Gallium \n $u_y$, left wall at $T={T_H}K$, $t={np.round(t/Nt*Time, decimals=2)}s$')
        plt.colorbar()
        plt.savefig(f"Figures/hsource_trt-fsm_sq_cav/{folder_nr}/heatmap_uy_t={np.round(t/Nt*Time, decimals=2)}_N{Ny}.png")

        plt.figure()
        plt.clf()
        plt.imshow(ux.T, cmap=cm.Blues, origin='lower')
        plt.xlabel('$x$ (# lattice nodes)')
        plt.ylabel('$y$ (# lattice nodes)')
        plt.title(f'Gallium \n $u_x$, left wall at $T={T_H}K$, $t={np.round(t/Nt*Time, decimals=2)}s$')
        plt.colorbar()
        plt.savefig(f"Figures/hsource_trt-fsm_sq_cav/{folder_nr}/heatmap_ux_t={np.round(t/Nt*Time, decimals=3)}_N{Ny}.png")

        ## Temperature heatmap
        plt.figure()
        plt.clf()
        plt.imshow(np.flip(T[1:-1, 1:-1].T, axis=0), cmap=cm.Blues)
        plt.xlabel('$x$ (# lattice nodes)')
        plt.ylabel('$y$ (# lattice nodes)')
        plt.title(f'Gallium \n $T$, left wall at $T={T_H}K$, $t={np.round(t/Nt*Time, decimals=2)}s$')
        plt.colorbar()
        plt.savefig(f"Figures/hsource_trt-fsm_sq_cav/{folder_nr}/heatmap_T_t={np.round(t/Nt*Time, decimals=3)}_N{Ny}.png")

        # plt.figure()
        # plt.clf()
        # plt.imshow(np.flip(rho_sim, axis=1).T, cmap=cm.Blues)
        # plt.xlabel('$x$ (# lattice nodes)')
        # plt.ylabel('$y$ (# lattice nodes)')
        # plt.title(f'$\\rho$ in cavity with left wall at $T={T_H}K$')
        # plt.colorbar()
        # plt.savefig(f"Figures/hsource_trt-fsm_sq_cav/{folder_nr}/heatmap_rho_time{Time}_t={np.round(t/Nt*Time, decimals=3)}.png")

        # Vector plot
        plt.figure()
        plt.quiver(Cu*ux.T, Cu*uy.T)
        plt.xlabel('$x$ (# lattice nodes)')
        plt.ylabel('$y$ (# lattice nodes)')
        plt.title(f'Gallium \n $u$ in pipe with left wall at $T={T_H}K$, $t={np.round(t/Nt*Time, decimals=2)}s$')
        # plt.legend('Velocity vector')
        plt.savefig(f"Figures/hsource_trt-fsm_sq_cav/{folder_nr}/arrowplot_t={np.round(t/Nt*Time, decimals=3)}_N{Ny}.png")

        plt.close('all')


stop = time.time()
print(stop-start)

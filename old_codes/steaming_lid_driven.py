from numba import njit
import numpy as np

q = 9

@njit
def fluid(Nx, Ny, f_plus, f_minus, f_star):
    for i in range(1, Nx-1):

        f = f_plus.copy()

        f[i, 1:Ny-1, 0] = f_star[i, 1:Ny-1, 0]
        f[i, 1:Ny-1, 1] = f_star[i-1, 1:Ny-1, 1]
        f[i, 1:Ny-1, 2] = f_star[i, 0:Ny-2, 2]
        f[i, 1:Ny-1, 3] = f_star[i+1, 1:Ny-1, 3]
        f[i, 1:Ny-1, 4] = f_star[i, 2:Ny, 4]
        f[i, 1:Ny-1, 5] = f_star[i-1, 0:Ny-2, 5]
        f[i, 1:Ny-1, 6] = f_star[i+1, 0:Ny-2, 6]
        f[i, 1:Ny-1, 7] = f_star[i+1, 2:Ny, 7]
        f[i, 1:Ny-1, 8] = f_star[i-1, 2:Ny, 8]

        # f_plus[i, 1:Ny-1, 0] = f_star[i, 1:Ny-1, 0]
        # f_plus[i, 1:Ny-1, 1] = (f_star[i-1, 1:Ny-1, 1] + f_star[i+1, 1:Ny-1, 3]) / 2
        # f_plus[i, 1:Ny-1, 2] = (f_star[i, 0:Ny-2, 2] + f_star[i, 2:Ny, 4]) / 2
        # f_plus[i, 1:Ny-1, 3] = f_plus[i, 1:Ny-1, 1]
        # f_plus[i, 1:Ny-1, 4] = f_plus[i, 1:Ny-1, 2]
        # f_plus[i, 1:Ny-1, 5] = (f_star[i-1, 0:Ny-2, 5] + f_star[i+1, 2:Ny, 7]) / 2
        # f_plus[i, 1:Ny-1, 6] = (f_star[i+1, 0:Ny-2, 6] + f_star[i-1, 2:Ny, 8]) / 2
        # f_plus[i, 1:Ny-1, 7] = f_plus[i, 1:Ny-1, 5]
        # f_plus[i, 1:Ny-1, 8] = f_plus[i, 1:Ny-1, 6]
        #
        # f_minus[i, 1:Ny-1, 0] = 0
        # f_minus[i, 1:Ny-1, 1] = (f_star[i-1, 1:Ny-1, 1] - f_star[i+1, 1:Ny-1, 3]) / 2
        # f_minus[i, 1:Ny-1, 2] = (f_star[i, 0:Ny-2, 2] - f_star[i, 2:Ny, 4]) / 2
        # f_minus[i, 1:Ny-1, 3] = -f_minus[i, 1:Ny-1, 1]
        # f_minus[i, 1:Ny-1, 4] = -f_minus[i, 1:Ny-1, 2]
        # f_minus[i, 1:Ny-1, 5] = (f_star[i-1, 0:Ny-2, 5] - f_star[i+1, 2:Ny, 7]) / 2
        # f_minus[i, 1:Ny-1, 6] = (f_star[i+1, 0:Ny-2, 6] - f_star[i-1, 2:Ny, 8]) / 2
        # f_minus[i, 1:Ny-1, 7] = -f_minus[i, 1:Ny-1, 5]
        # f_minus[i, 1:Ny-1, 8] = -f_minus[i, 1:Ny-1, 6]

        f_plus[i, 1:Ny-1, 0] = f[i, 1:Ny-1, 0]
        f_plus[i, 1:Ny-1, 1] = (f[i, 1:Ny-1, 1] + f[i, 1:Ny-1, 3]) / 2
        f_plus[i, 1:Ny-1, 2] = (f[i, 1:Ny-1, 2] + f[i, 1:Ny-1, 4]) / 2
        f_plus[i, 1:Ny-1, 3] = (f[i, 1:Ny-1, 3] + f[i, 1:Ny-1, 1]) / 2
        f_plus[i, 1:Ny-1, 4] = (f[i, 1:Ny-1, 4] + f[i, 1:Ny-1, 2]) / 2
        f_plus[i, 1:Ny-1, 5] = (f[i, 1:Ny-1, 5] + f[i, 1:Ny-1, 7]) / 2
        f_plus[i, 1:Ny-1, 6] = (f[i, 1:Ny-1, 6] + f[i, 1:Ny-1, 8]) / 2
        f_plus[i, 1:Ny-1, 7] = (f[i, 1:Ny-1, 7] + f[i, 1:Ny-1, 5]) / 2
        f_plus[i, 1:Ny-1, 8] = (f[i, 1:Ny-1, 8] + f[i, 1:Ny-1, 6]) / 2

        f_minus[i, 1:Ny-1, 0] = 0
        f_minus[i, 1:Ny-1, 1] = (f[i, 1:Ny-1, 1] - f[i, 1:Ny-1, 3]) / 2
        f_minus[i, 1:Ny-1, 2] = (f[i, 1:Ny-1, 2] - f[i, 1:Ny-1, 4]) / 2
        f_minus[i, 1:Ny-1, 3] = (f[i, 1:Ny-1, 3] - f[i, 1:Ny-1, 1]) / 2
        f_minus[i, 1:Ny-1, 4] = (f[i, 1:Ny-1, 4] - f[i, 1:Ny-1, 2]) / 2
        f_minus[i, 1:Ny-1, 5] = (f[i, 1:Ny-1, 5] - f[i, 1:Ny-1, 7]) / 2
        f_minus[i, 1:Ny-1, 6] = (f[i, 1:Ny-1, 6] - f[i, 1:Ny-1, 8]) / 2
        f_minus[i, 1:Ny-1, 7] = (f[i, 1:Ny-1, 7] - f[i, 1:Ny-1, 5]) / 2
        f_minus[i, 1:Ny-1, 8] = (f[i, 1:Ny-1, 8] - f[i, 1:Ny-1, 6]) / 2

    return f_plus, f_minus

@njit
def left_wall(Ny, f_plus, f_minus, f_star):
    i = 0

    f = f_plus.copy()

    f[i, 1:Ny-1, 0] = f_star[i, 1:Ny-1, 0]
    f[i, 1:Ny-1, 1] = f_star[i, 1:Ny-1, 3]
    f[i, 1:Ny-1, 2] = f_star[i, 0:Ny-2, 2]
    f[i, 1:Ny-1, 3] = f_star[i+1, 1:Ny-1, 3]
    f[i, 1:Ny-1, 4] = f_star[i, 2:Ny, 4]
    f[i, 1:Ny-1, 5] = f_star[i, 1:Ny-1, 7]
    f[i, 1:Ny-1, 6] = f_star[i+1, 0:Ny-2, 6]
    f[i, 1:Ny-1, 7] = f_star[i+1, 2:Ny, 7]
    f[i, 1:Ny-1, 8] = f_star[i, 1:Ny-1, 6]

    # f_plus[i, 1:Ny-1, 0] = f_star[i, 1:Ny-1, 0]
    # f_plus[i, 1:Ny-1, 1] = (f_star[i, 1:Ny-1, 3] + f_star[i+1, 1:Ny-1, 3]) / 2      # Bounce
    # f_plus[i, 1:Ny-1, 2] = (f_star[i, 0:Ny-2, 2] + f_star[i, 2:Ny, 4]) / 2
    # f_plus[i, 1:Ny-1, 3] = f_plus[i, 1:Ny-1, 1]
    # f_plus[i, 1:Ny-1, 4] = f_plus[i, 1:Ny-1, 2]
    # f_plus[i, 1:Ny-1, 5] = (f_star[i, 1:Ny-1, 7] + f_star[i+1, 2:Ny, 7]) / 2        # Bounce
    # f_plus[i, 1:Ny-1, 6] = (f_star[i+1, 0:Ny-2, 6] + f_star[i, 1:Ny-1, 6]) / 2
    # f_plus[i, 1:Ny-1, 7] = f_plus[i, 1:Ny-1, 5]
    # f_plus[i, 1:Ny-1, 8] = f_plus[i, 1:Ny-1, 6]                                     # Bounce
    #
    # f_minus[i, 1:Ny-1, 0] = 0
    # f_minus[i, 1:Ny-1, 1] = (f_star[i, 1:Ny-1, 3] - f_star[i+1, 1:Ny-1, 3]) / 2     # Bounce
    # f_minus[i, 1:Ny-1, 2] = (f_star[i, 0:Ny-2, 2] - f_star[i, 2:Ny, 4]) / 2
    # f_minus[i, 1:Ny-1, 3] = -f_minus[i, 1:Ny-1, 1]
    # f_minus[i, 1:Ny-1, 4] = -f_minus[i, 1:Ny-1, 2]
    # f_minus[i, 1:Ny-1, 5] = (f_star[i, 1:Ny-1, 7] - f_star[i+1, 2:Ny, 7]) / 2       # Bounce
    # f_minus[i, 1:Ny-1, 6] = (f_star[i+1, 0:Ny-2, 6] - f_star[i, 1:Ny-1, 6]) / 2
    # f_minus[i, 1:Ny-1, 7] = -f_minus[i, 1:Ny-1, 5]
    # f_minus[i, 1:Ny-1, 8] = -f_minus[i, 1:Ny-1, 6]                                  # Bounce

    f_plus[i, 1:Ny-1, 0] = f[i, 1:Ny-1, 0]
    f_plus[i, 1:Ny-1, 1] = (f[i, 1:Ny-1, 1] + f[i, 1:Ny-1, 3]) / 2
    f_plus[i, 1:Ny-1, 2] = (f[i, 1:Ny-1, 2] + f[i, 1:Ny-1, 4]) / 2
    f_plus[i, 1:Ny-1, 3] = (f[i, 1:Ny-1, 3] + f[i, 1:Ny-1, 1]) / 2
    f_plus[i, 1:Ny-1, 4] = (f[i, 1:Ny-1, 4] + f[i, 1:Ny-1, 2]) / 2
    f_plus[i, 1:Ny-1, 5] = (f[i, 1:Ny-1, 5] + f[i, 1:Ny-1, 7]) / 2
    f_plus[i, 1:Ny-1, 6] = (f[i, 1:Ny-1, 6] + f[i, 1:Ny-1, 8]) / 2
    f_plus[i, 1:Ny-1, 7] = (f[i, 1:Ny-1, 7] + f[i, 1:Ny-1, 5]) / 2
    f_plus[i, 1:Ny-1, 8] = (f[i, 1:Ny-1, 8] + f[i, 1:Ny-1, 6]) / 2

    f_minus[i, 1:Ny-1, 0] = 0
    f_minus[i, 1:Ny-1, 1] = (f[i, 1:Ny-1, 1] - f[i, 1:Ny-1, 3]) / 2
    f_minus[i, 1:Ny-1, 2] = (f[i, 1:Ny-1, 2] - f[i, 1:Ny-1, 4]) / 2
    f_minus[i, 1:Ny-1, 3] = (f[i, 1:Ny-1, 3] - f[i, 1:Ny-1, 1]) / 2
    f_minus[i, 1:Ny-1, 4] = (f[i, 1:Ny-1, 4] - f[i, 1:Ny-1, 2]) / 2
    f_minus[i, 1:Ny-1, 5] = (f[i, 1:Ny-1, 5] - f[i, 1:Ny-1, 7]) / 2
    f_minus[i, 1:Ny-1, 6] = (f[i, 1:Ny-1, 6] - f[i, 1:Ny-1, 8]) / 2
    f_minus[i, 1:Ny-1, 7] = (f[i, 1:Ny-1, 7] - f[i, 1:Ny-1, 5]) / 2
    f_minus[i, 1:Ny-1, 8] = (f[i, 1:Ny-1, 8] - f[i, 1:Ny-1, 6]) / 2

    return f_plus, f_minus

@njit
def right_wall(Nx, Ny, f_plus, f_minus, f_star):
    i = Nx - 1

    f = f_plus.copy()

    f[i, 1:Ny-1, 0] = f_star[i, 1:Ny-1, 0]
    f[i, 1:Ny-1, 1] = f_star[i-1, 1:Ny-1, 1]
    f[i, 1:Ny-1, 2] = f_star[i, 0:Ny-2, 2]
    f[i, 1:Ny-1, 3] = f_star[i, 1:Ny-1, 1]
    f[i, 1:Ny-1, 4] = f_star[i, 2:Ny, 4]
    f[i, 1:Ny-1, 5] = f_star[i-1, 0:Ny-2, 7]
    f[i, 1:Ny-1, 6] = f_star[i, 1:Ny-1, 8]
    f[i, 1:Ny-1, 7] = f_star[i, 1:Ny-1, 5]
    f[i, 1:Ny-1, 8] = f_star[i-1, 2:Ny, 8]

    # f_plus[i, 1:Ny-1, 0] = f_star[i, 1:Ny-1, 0]
    # f_plus[i, 1:Ny-1, 1] = (f_star[i-1, 1:Ny-1, 1] + f_star[i, 1:Ny-1, 1]) / 2      # Bounce
    # f_plus[i, 1:Ny-1, 2] = (f_star[i, 0:Ny-2, 2] + f_star[i, 2:Ny, 4]) / 2
    # f_plus[i, 1:Ny-1, 3] = f_plus[i, 1:Ny-1, 1]
    # f_plus[i, 1:Ny-1, 4] = f_plus[i, 1:Ny-1, 2]
    # f_plus[i, 1:Ny-1, 5] = (f_star[i-1, 0:Ny-2, 5] + f_star[i, 1:Ny-1, 5]) / 2
    # f_plus[i, 1:Ny-1, 6] = (f_star[i, 1:Ny-1, 8] + f_star[i-1, 2:Ny, 8]) / 2        # Bounce
    # f_plus[i, 1:Ny-1, 7] = f_plus[i, 1:Ny-1, 5]                                     # Bounce
    # f_plus[i, 1:Ny-1, 8] = f_plus[i, 1:Ny-1, 6]
    #
    # f_minus[i, 1:Ny-1, 0] = 0
    # f_minus[i, 1:Ny-1, 1] = (f_star[i-1, 1:Ny-1, 1] - f_star[i, 1:Ny-1, 1]) / 2     # Bounce
    # f_minus[i, 1:Ny-1, 2] = (f_star[i, 0:Ny-2, 2] - f_star[i, 2:Ny, 4]) / 2
    # f_minus[i, 1:Ny-1, 3] = -f_minus[i, 1:Ny-1, 1]
    # f_minus[i, 1:Ny-1, 4] = -f_minus[i, 1:Ny-1, 2]
    # f_minus[i, 1:Ny-1, 5] = (f_star[i-1, 0:Ny-2, 5] - f_star[i, 1:Ny-1, 5]) / 2
    # f_minus[i, 1:Ny-1, 6] = (f_star[i, 1:Ny-1, 8] - f_star[i-1, 2:Ny, 8]) / 2       # Bounce
    # f_minus[i, 1:Ny-1, 7] = -f_minus[i, 1:Ny-1, 5]                                  # Bounce
    # f_minus[i, 1:Ny-1, 8] = -f_minus[i, 1:Ny-1, 6]

    f_plus[i, 1:Ny-1, 0] = f[i, 1:Ny-1, 0]
    f_plus[i, 1:Ny-1, 1] = (f[i, 1:Ny-1, 1] + f[i, 1:Ny-1, 3]) / 2
    f_plus[i, 1:Ny-1, 2] = (f[i, 1:Ny-1, 2] + f[i, 1:Ny-1, 4]) / 2
    f_plus[i, 1:Ny-1, 3] = (f[i, 1:Ny-1, 3] + f[i, 1:Ny-1, 1]) / 2
    f_plus[i, 1:Ny-1, 4] = (f[i, 1:Ny-1, 4] + f[i, 1:Ny-1, 2]) / 2
    f_plus[i, 1:Ny-1, 5] = (f[i, 1:Ny-1, 5] + f[i, 1:Ny-1, 7]) / 2
    f_plus[i, 1:Ny-1, 6] = (f[i, 1:Ny-1, 6] + f[i, 1:Ny-1, 8]) / 2
    f_plus[i, 1:Ny-1, 7] = (f[i, 1:Ny-1, 7] + f[i, 1:Ny-1, 5]) / 2
    f_plus[i, 1:Ny-1, 8] = (f[i, 1:Ny-1, 8] + f[i, 1:Ny-1, 6]) / 2

    f_minus[i, 1:Ny-1, 0] = 0
    f_minus[i, 1:Ny-1, 1] = (f[i, 1:Ny-1, 1] - f[i, 1:Ny-1, 3]) / 2
    f_minus[i, 1:Ny-1, 2] = (f[i, 1:Ny-1, 2] - f[i, 1:Ny-1, 4]) / 2
    f_minus[i, 1:Ny-1, 3] = (f[i, 1:Ny-1, 3] - f[i, 1:Ny-1, 1]) / 2
    f_minus[i, 1:Ny-1, 4] = (f[i, 1:Ny-1, 4] - f[i, 1:Ny-1, 2]) / 2
    f_minus[i, 1:Ny-1, 5] = (f[i, 1:Ny-1, 5] - f[i, 1:Ny-1, 7]) / 2
    f_minus[i, 1:Ny-1, 6] = (f[i, 1:Ny-1, 6] - f[i, 1:Ny-1, 8]) / 2
    f_minus[i, 1:Ny-1, 7] = (f[i, 1:Ny-1, 7] - f[i, 1:Ny-1, 5]) / 2
    f_minus[i, 1:Ny-1, 8] = (f[i, 1:Ny-1, 8] - f[i, 1:Ny-1, 6]) / 2

    return f_plus, f_minus

@njit
def lower_wall(Nx, f_plus, f_minus, f_star):
    j = 0

    f = f_plus.copy()

    f[1:Nx-1, j, 0] = f_star[1:Nx-1, j, 0]
    f[1:Nx-1, j, 1] = f_star[0:Nx-2, j, 1]
    f[1:Nx-1, j, 2] = f_star[1:Nx-1, j, 4]
    f[1:Nx-1, j, 3] = f_star[2:Nx, j, 3]
    f[1:Nx-1, j, 4] = f_star[1:Nx-1, j+1, 4]
    f[1:Nx-1, j, 5] = f_star[1:Nx-1, j, 7]
    f[1:Nx-1, j, 6] = f_star[1:Nx-1, j, 8]
    f[1:Nx-1, j, 7] = f_star[2:Nx, j+1, 7]
    f[1:Nx-1, j, 8] = f_star[0:Nx-2, j+1, 8]

    # f_plus[1:Nx-1, j, 0] = f_star[1:Nx-1, j, 0]
    # f_plus[1:Nx-1, j, 1] = (f_star[0:Nx-2, j, 1] + f_star[2:Nx, j, 3]) / 2
    # f_plus[1:Nx-1, j, 2] = (f_star[1:Nx-1, j, 4] + f_star[1:Nx-1, j+1, 4]) / 2      # Bounce
    # f_plus[1:Nx-1, j, 3] = f_plus[1:Nx-1, j, 1]
    # f_plus[1:Nx-1, j, 4] = f_plus[1:Nx-1, j, 2]
    # f_plus[1:Nx-1, j, 5] = (f_star[1:Nx-1, j, 7] + f_star[2:Nx, j+1, 7]) / 2        # Bounce
    # f_plus[1:Nx-1, j, 6] = (f_star[1:Nx-1, j, 8] + f_star[0:Nx-2, j+1, 8]) / 2      # Bounce
    # f_plus[1:Nx-1, j, 7] = f_plus[1:Nx-1, j, 5]
    # f_plus[1:Nx-1, j, 8] = f_plus[1:Nx-1, j, 6]
    #
    # f_minus[1:Nx-1, j, 0] = 0
    # f_minus[1:Nx-1, j, 1] = (f_star[0:Nx-2, j, 1] - f_star[2:Nx, j, 3]) / 2
    # f_minus[1:Nx-1, j, 2] = (f_star[1:Nx-1, j, 4] - f_star[1:Nx-1, j+1, 4]) / 2      # Bounce
    # f_minus[1:Nx-1, j, 3] = -f_minus[1:Nx-1, j, 1]
    # f_minus[1:Nx-1, j, 4] = -f_minus[1:Nx-1, j, 2]
    # f_minus[1:Nx-1, j, 5] = (f_star[1:Nx-1, j, 7] - f_star[2:Nx, j+1, 7]) / 2        # Bounce
    # f_minus[1:Nx-1, j, 6] = (f_star[1:Nx-1, j, 8] - f_star[0:Nx-2, j+1, 8]) / 2      # Bounce
    # f_minus[1:Nx-1, j, 7] = -f_minus[1:Nx-1, j, 5]
    # f_minus[1:Nx-1, j, 8] = -f_minus[1:Nx-1, j, 6]

    f_plus[1:Nx-1, j, 0] = f[1:Nx-1, j, 0]
    f_plus[1:Nx-1, j, 1] = (f[1:Nx-1, j, 1] + f[1:Nx-1, j, 1]) / 2
    f_plus[1:Nx-1, j, 2] = (f[1:Nx-1, j, 2] + f[1:Nx-1, j, 2]) / 2
    f_plus[1:Nx-1, j, 3] = (f[1:Nx-1, j, 3] + f[1:Nx-1, j, 3]) / 2
    f_plus[1:Nx-1, j, 4] = (f[1:Nx-1, j, 4] + f[1:Nx-1, j, 4]) / 2
    f_plus[1:Nx-1, j, 5] = (f[1:Nx-1, j, 5] + f[1:Nx-1, j, 5]) / 2
    f_plus[1:Nx-1, j, 6] = (f[1:Nx-1, j, 6] + f[1:Nx-1, j, 6]) / 2
    f_plus[1:Nx-1, j, 7] = (f[1:Nx-1, j, 7] + f[1:Nx-1, j, 7]) / 2
    f_plus[1:Nx-1, j, 8] = (f[1:Nx-1, j, 8] + f[1:Nx-1, j, 8]) / 2

    f_minus[1:Nx-1, j, 0] = 0
    f_minus[1:Nx-1, j, 1] = (f[1:Nx-1, j, 1] - f[1:Nx-1, j, 1]) / 2
    f_minus[1:Nx-1, j, 2] = (f[1:Nx-1, j, 2] - f[1:Nx-1, j, 2]) / 2
    f_minus[1:Nx-1, j, 3] = (f[1:Nx-1, j, 3] - f[1:Nx-1, j, 3]) / 2
    f_minus[1:Nx-1, j, 4] = (f[1:Nx-1, j, 4] - f[1:Nx-1, j, 4]) / 2
    f_minus[1:Nx-1, j, 5] = (f[1:Nx-1, j, 5] - f[1:Nx-1, j, 5]) / 2
    f_minus[1:Nx-1, j, 6] = (f[1:Nx-1, j, 6] - f[1:Nx-1, j, 6]) / 2
    f_minus[1:Nx-1, j, 7] = (f[1:Nx-1, j, 7] - f[1:Nx-1, j, 7]) / 2
    f_minus[1:Nx-1, j, 8] = (f[1:Nx-1, j, 8] - f[1:Nx-1, j, 8]) / 2

    return f_plus, f_minus

@njit
def upper_wall(Nx, Ny, f_plus, f_minus, f_star, rho, w, c_s, c, uxw, uyw):
    j = Ny - 1

    f = f_plus.copy()

    f[1:Nx-1, j, 0] = f_star[1:Nx-1, j, 0]
    f[1:Nx-1, j, 1] = f_star[0:Nx-2, j, 1]
    f[1:Nx-1, j, 2] = f_star[1:Nx-1, j-1, 2]
    f[1:Nx-1, j, 3] = f_star[2:Nx, j, 3]
    f[1:Nx-1, j, 4] = f_star[1:Nx-1, j, 2] - 2 * w[2] * rho[1:Nx-1, j] / c_s**2 * (uxw * c[2, 0] + uyw * c[2, 1])
    f[1:Nx-1, j, 5] = f_star[0:Nx-2, j-1, 5]
    f[1:Nx-1, j, 6] = f_star[2:Nx, j-1, 6]
    f[1:Nx-1, j, 7] = f_star[1:Nx-1, j, 5] - 2 * w[5] * rho[1:Nx-1, j] / c_s**2 * (uxw * c[5, 0] + uyw * c[5, 1])
    f[1:Nx-1, j, 8] = f_star[1:Nx-1, j, 6] - 2 * w[6] * rho[1:Nx-1, j] / c_s**2 * (uxw * c[6, 0] + uyw * c[6, 1])

    # f_plus[1:Nx-1, j, 0] = f_star[1:Nx-1, j, 0]
    # f_plus[1:Nx-1, j, 1] = (f_star[0:Nx-2, j, 1] + f_star[2:Nx, j, 3]) / 2
    # f_plus[1:Nx-1, j, 2] = (f_star[1:Nx-1, j-1, 2] + f_star[1:Nx-1, j, 2]) / 2
    # f_plus[1:Nx-1, j, 3] = f_plus[1:Nx-1, j, 1]
    # f_plus[1:Nx-1, j, 4] = f_plus[1:Nx-1, j, 2]
    # f_plus[1:Nx-1, j, 5] = (f_star[0:Nx-2, j-1, 5] + f_star[1:Nx-1, j, 5]) / 2
    # f_plus[1:Nx-1, j, 6] = (f_star[2:Nx, j-1, 6] + f_star[1:Nx-1, j, 6]) / 2
    # f_plus[1:Nx-1, j, 7] = f_plus[1:Nx-1, j, 5]
    # f_plus[1:Nx-1, j, 8] = f_plus[1:Nx-1, j, 6]
    #
    # f_minus[1:Nx-1, j, 0] = 0
    # f_minus[1:Nx-1, j, 1] = (f_star[0:Nx-2, j, 1] - f_star[2:Nx, j, 3]) / 2
    # f_minus[1:Nx-1, j, 2] = (f_star[1:Nx-1, j-1, 2] - f_star[1:Nx-1, j, 2]) / 2
    # f_minus[1:Nx-1, j, 3] = -f_minus[1:Nx-1, j, 1]
    # f_minus[1:Nx-1, j, 4] = -f_minus[1:Nx-1, j, 2]
    # f_minus[1:Nx-1, j, 5] = (f_star[0:Nx-2, j-1, 5] - f_star[1:Nx-1, j, 5]) / 2
    # f_minus[1:Nx-1, j, 6] = (f_star[2:Nx, j-1, 6] - f_star[1:Nx-1, j, 6]) / 2
    # f_minus[1:Nx-1, j, 7] = -f_minus[1:Nx-1, j, 5]
    # f_minus[1:Nx-1, j, 8] = -f_minus[1:Nx-1, j, 6]

    f_plus[1:Nx-1, j, 0] = f[1:Nx-1, j, 0]
    f_plus[1:Nx-1, j, 1] = (f[1:Nx-1, j, 1] + f[1:Nx-1, j, 1]) / 2
    f_plus[1:Nx-1, j, 2] = (f[1:Nx-1, j, 2] + f[1:Nx-1, j, 2]) / 2
    f_plus[1:Nx-1, j, 3] = (f[1:Nx-1, j, 3] + f[1:Nx-1, j, 3]) / 2
    f_plus[1:Nx-1, j, 4] = (f[1:Nx-1, j, 4] + f[1:Nx-1, j, 4]) / 2
    f_plus[1:Nx-1, j, 5] = (f[1:Nx-1, j, 5] + f[1:Nx-1, j, 5]) / 2
    f_plus[1:Nx-1, j, 6] = (f[1:Nx-1, j, 6] + f[1:Nx-1, j, 6]) / 2
    f_plus[1:Nx-1, j, 7] = (f[1:Nx-1, j, 7] + f[1:Nx-1, j, 7]) / 2
    f_plus[1:Nx-1, j, 8] = (f[1:Nx-1, j, 8] + f[1:Nx-1, j, 8]) / 2

    f_minus[1:Nx-1, j, 0] = 0
    f_minus[1:Nx-1, j, 1] = (f[1:Nx-1, j, 1] - f[1:Nx-1, j, 1]) / 2
    f_minus[1:Nx-1, j, 2] = (f[1:Nx-1, j, 2] - f[1:Nx-1, j, 2]) / 2
    f_minus[1:Nx-1, j, 3] = (f[1:Nx-1, j, 3] - f[1:Nx-1, j, 3]) / 2
    f_minus[1:Nx-1, j, 4] = (f[1:Nx-1, j, 4] - f[1:Nx-1, j, 4]) / 2
    f_minus[1:Nx-1, j, 5] = (f[1:Nx-1, j, 5] - f[1:Nx-1, j, 5]) / 2
    f_minus[1:Nx-1, j, 6] = (f[1:Nx-1, j, 6] - f[1:Nx-1, j, 6]) / 2
    f_minus[1:Nx-1, j, 7] = (f[1:Nx-1, j, 7] - f[1:Nx-1, j, 7]) / 2
    f_minus[1:Nx-1, j, 8] = (f[1:Nx-1, j, 8] - f[1:Nx-1, j, 8]) / 2

    return f_plus, f_minus

@njit
def lower_left_corner(f_plus, f_minus, f_star, w):
    i = 0
    j = 0

    f = f_plus.copy()

    f[i, j, 0] = f_star[i, j, 0]
    f[i, j, 1] = f_star[i, j, 3]
    f[i, j, 2] = f_star[i, j, 4]
    f[i, j, 3] = f_star[i+1, j, 3]
    f[i, j, 4] = f_star[i, j+1, 4]
    f[i, j, 5] = f_star[i, j, 7]
    f[i, j, 6] = f_star[i, j, 8]
    f[i, j, 7] = f_star[i+1, j+1, 7]
    f[i, j, 8] = f_star[i, j, 6]

    # f_plus[i, j, 0] = f_star[i, j, 0]
    # f_plus[i, j, 1] = (f_star[i, j, 3] + f_star[i+1, j, 3]) / 2
    # f_plus[i, j, 2] = (f_star[i, j, 4] + f_star[i, j+1, 4]) / 2
    # f_plus[i, j, 3] = f_plus[i, j, 1]
    # f_plus[i, j, 4] = f_plus[i, j, 2]
    # f_plus[i, j, 5] = (f_star[i, j, 7] + f_star[i+1, j+1, 7]) / 2
    # f_plus[i, j, 6] = (f_star[i, j, 8] + f_star[i, j, 6]) / 2
    # f_plus[i, j, 7] = f_plus[i, j, 5]
    # f_plus[i, j, 8] = f_plus[i, j, 6]
    #
    # f_minus[i, j, 0] = 0
    # f_minus[i, j, 1] = (f_star[i, j, 3] - f_star[i+1, j, 3]) / 2
    # f_minus[i, j, 2] = (f_star[i, j, 4] - f_star[i, j+1, 4]) / 2
    # f_minus[i, j, 3] = -f_minus[i, j, 1]
    # f_minus[i, j, 4] = -f_minus[i, j, 2]
    # f_minus[i, j, 5] = (f_star[i, j, 7] - f_star[i+1, j+1, 7]) / 2
    # f_minus[i, j, 6] = (f_star[i, j, 8] - f_star[i, j, 6]) / 2
    # f_minus[i, j, 7] = -f_minus[i, j, 5]
    # f_minus[i, j, 8] = -f_minus[i, j, 6]

    f_plus[i, j, 0] = f[i, j, 0]
    f_plus[i, j, 1] = (f[i, j, 1] + f[i, j, 1]) / 2
    f_plus[i, j, 2] = (f[i, j, 2] + f[i, j, 2]) / 2
    f_plus[i, j, 3] = (f[i, j, 3] + f[i, j, 3]) / 2
    f_plus[i, j, 4] = (f[i, j, 4] + f[i, j, 4]) / 2
    f_plus[i, j, 5] = (f[i, j, 5] + f[i, j, 5]) / 2
    f_plus[i, j, 6] = (f[i, j, 6] + f[i, j, 6]) / 2
    f_plus[i, j, 7] = (f[i, j, 7] + f[i, j, 7]) / 2
    f_plus[i, j, 8] = (f[i, j, 8] + f[i, j, 8]) / 2

    f_minus[i, j, 0] = 0
    f_minus[i, j, 1] = (f[i, j, 1] - f[i, j, 1]) / 2
    f_minus[i, j, 2] = (f[i, j, 2] - f[i, j, 2]) / 2
    f_minus[i, j, 3] = (f[i, j, 3] - f[i, j, 3]) / 2
    f_minus[i, j, 4] = (f[i, j, 4] - f[i, j, 4]) / 2
    f_minus[i, j, 5] = (f[i, j, 5] - f[i, j, 5]) / 2
    f_minus[i, j, 6] = (f[i, j, 6] - f[i, j, 6]) / 2
    f_minus[i, j, 7] = (f[i, j, 7] - f[i, j, 7]) / 2
    f_minus[i, j, 8] = (f[i, j, 8] - f[i, j, 8]) / 2

    return f_plus, f_minus

@njit
def lower_right_corner(Nx, f_plus, f_minus, f_star, w):
    i = Nx - 1
    j = 0

    f = f_plus.copy()

    f[i, j, 0] = f_star[i, j, 0]
    f[i, j, 1] = f_star[i-1, j, 1]
    f[i, j, 2] = f_star[i, j, 4]
    f[i, j, 3] = f_star[i, j, 1]
    f[i, j, 4] = f_star[i, j+1, 4]
    f[i, j, 5] = f_star[i, j, 7]
    f[i, j, 6] = f_star[i, j, 8]
    f[i, j, 7] = f_star[i, j, 5]
    f[i, j, 8] = f_star[i-1, j+1, 8]

    # f_plus[i, j, 0] = f_star[i, j, 0]
    # f_plus[i, j, 1] = (f_star[i-1, j, 1] + f_star[i, j, 1]) / 2
    # f_plus[i, j, 2] = (f_star[i, j, 4] + f_star[i, j+1, 4]) / 2
    # f_plus[i, j, 3] = f_plus[i, j, 1]
    # f_plus[i, j, 4] = f_plus[i, j, 2]
    # f_plus[i, j, 5] = (f_star[i, j, 7] + f_star[i, j, 5]) / 2
    # f_plus[i, j, 6] = (f_star[i, j, 8] + f_star[i-1, j+1, 8]) / 2
    # f_plus[i, j, 7] = f_plus[i, j, 5]
    # f_plus[i, j, 8] = f_plus[i, j, 6]
    #
    # f_minus[i, j, 0] = 0
    # f_minus[i, j, 1] = (f_star[i-1, j, 1] - f_star[i, j, 1]) / 2
    # f_minus[i, j, 2] = (f_star[i, j, 4] - f_star[i, j+1, 4]) / 2
    # f_minus[i, j, 3] = -f_minus[i, j, 1]
    # f_minus[i, j, 4] = -f_minus[i, j, 2]
    # f_minus[i, j, 5] = (f_star[i, j, 7] - f_star[i, j, 5]) / 2
    # f_minus[i, j, 6] = (f_star[i, j, 8] - f_star[i-1, j+1, 8]) / 2
    # f_minus[i, j, 7] = -f_minus[i, j, 5]
    # f_minus[i, j, 8] = -f_minus[i, j, 6]

    f_plus[i, j, 0] = f[i, j, 0]
    f_plus[i, j, 1] = (f[i, j, 1] + f[i, j, 1]) / 2
    f_plus[i, j, 2] = (f[i, j, 2] + f[i, j, 2]) / 2
    f_plus[i, j, 3] = (f[i, j, 3] + f[i, j, 3]) / 2
    f_plus[i, j, 4] = (f[i, j, 4] + f[i, j, 4]) / 2
    f_plus[i, j, 5] = (f[i, j, 5] + f[i, j, 5]) / 2
    f_plus[i, j, 6] = (f[i, j, 6] + f[i, j, 6]) / 2
    f_plus[i, j, 7] = (f[i, j, 7] + f[i, j, 7]) / 2
    f_plus[i, j, 8] = (f[i, j, 8] + f[i, j, 8]) / 2

    f_minus[i, j, 0] = 0
    f_minus[i, j, 1] = (f[i, j, 1] - f[i, j, 1]) / 2
    f_minus[i, j, 2] = (f[i, j, 2] - f[i, j, 2]) / 2
    f_minus[i, j, 3] = (f[i, j, 3] - f[i, j, 3]) / 2
    f_minus[i, j, 4] = (f[i, j, 4] - f[i, j, 4]) / 2
    f_minus[i, j, 5] = (f[i, j, 5] - f[i, j, 5]) / 2
    f_minus[i, j, 6] = (f[i, j, 6] - f[i, j, 6]) / 2
    f_minus[i, j, 7] = (f[i, j, 7] - f[i, j, 7]) / 2
    f_minus[i, j, 8] = (f[i, j, 8] - f[i, j, 8]) / 2

    return f_plus, f_minus

@njit
def upper_left_corner(Ny, f_plus, f_minus, f_star, rho, w, c_s, c, uxw, uyw):
    i = 0
    j = Ny - 1

    f = f_plus.copy()

    f[i, j, 0] = f_star[i, j, 0]
    f[i, j, 1] = f_star[i, j, 3]
    f[i, j, 2] = f_star[i, j-1, 2]
    f[i, j, 3] = f_star[i+1, j, 3]
    f[i, j, 4] = f_star[i, j, 2] - 2 * w[2] * rho[i, j] / c_s**2 * (uxw * c[2, 0] + uyw * c[2, 1])
    f[i, j, 5] = f_star[i, j, 7]
    f[i, j, 6] = f_star[i+1, j-1, 6]
    f[i, j, 7] = f_star[i, j, 5] - 2 * w[5] * rho[i, j] / c_s**2 * (uxw * c[5, 0] + uyw * c[5, 1])
    f[i, j, 8] = f_star[i, j, 6] - 2 * w[6] * rho[i, j] / c_s**2 * (uxw * c[6, 0] + uyw * c[6, 1])

    # f_plus[i, j, 0] = f_star[i, j, 0]
    # f_plus[i, j, 1] = (f_star[i, j, 3] + f_star[i+1, j, 3]) / 2
    # f_plus[i, j, 2] = (f_star[i, j-1, 2] + f_star[i, j, 2]) / 2
    # f_plus[i, j, 3] = f_plus[i, j, 1]
    # f_plus[i, j, 4] = f_plus[i, j, 2]
    # f_plus[i, j, 5] = (f_star[i, j, 7] + f_star[i, j, 5]) / 2
    # f_plus[i, j, 6] = (f_star[i+1, j-1, 6] + f_star[i, j, 6]) / 2
    # f_plus[i, j, 7] = f_plus[i, j, 5]
    # f_plus[i, j, 8] = f_plus[i, j, 6]
    #
    # f_minus[i, j, 0] = 0
    # f_minus[i, j, 1] = (f_star[i, j, 3] - f_star[i+1, j, 3]) / 2
    # f_minus[i, j, 2] = (f_star[i, j-1, 2] - f_star[i, j, 2]) / 2
    # f_minus[i, j, 3] = -f_minus[i, j, 1]
    # f_minus[i, j, 4] = -f_minus[i, j, 2]
    # f_minus[i, j, 5] = (f_star[i, j, 7] - f_star[i, j, 5]) / 2
    # f_minus[i, j, 6] = (f_star[i+1, j-1, 6] - f_star[i, j, 6]) / 2
    # f_minus[i, j, 7] = -f_minus[i, j, 5]
    # f_minus[i, j, 8] = -f_minus[i, j, 6]

    f_plus[i, j, 0] = f[i, j, 0]
    f_plus[i, j, 1] = (f[i, j, 1] + f[i, j, 1]) / 2
    f_plus[i, j, 2] = (f[i, j, 2] + f[i, j, 2]) / 2
    f_plus[i, j, 3] = (f[i, j, 3] + f[i, j, 3]) / 2
    f_plus[i, j, 4] = (f[i, j, 4] + f[i, j, 4]) / 2
    f_plus[i, j, 5] = (f[i, j, 5] + f[i, j, 5]) / 2
    f_plus[i, j, 6] = (f[i, j, 6] + f[i, j, 6]) / 2
    f_plus[i, j, 7] = (f[i, j, 7] + f[i, j, 7]) / 2
    f_plus[i, j, 8] = (f[i, j, 8] + f[i, j, 8]) / 2

    f_minus[i, j, 0] = 0
    f_minus[i, j, 1] = (f[i, j, 1] - f[i, j, 1]) / 2
    f_minus[i, j, 2] = (f[i, j, 2] - f[i, j, 2]) / 2
    f_minus[i, j, 3] = (f[i, j, 3] - f[i, j, 3]) / 2
    f_minus[i, j, 4] = (f[i, j, 4] - f[i, j, 4]) / 2
    f_minus[i, j, 5] = (f[i, j, 5] - f[i, j, 5]) / 2
    f_minus[i, j, 6] = (f[i, j, 6] - f[i, j, 6]) / 2
    f_minus[i, j, 7] = (f[i, j, 7] - f[i, j, 7]) / 2
    f_minus[i, j, 8] = (f[i, j, 8] - f[i, j, 8]) / 2

    return f_plus, f_minus

@njit
def upper_right_corner(Nx, Ny, f_plus, f_minus, f_star, rho, w, c_s, c, uxw, uyw):
    i = Nx - 1
    j = Ny - 1

    f = f_plus.copy()

    f[i, j, 0] = f_star[i, j, 0]
    f[i, j, 1] = f_star[i-1, j, 1]
    f[i, j, 2] = f_star[i, j-1, 4]
    f[i, j, 3] = f_star[i, j, 1]
    f[i, j, 4] = f_star[i, j, 2] - 2 * w[2] * rho[i, j] / c_s**2 * (uxw * c[2, 0] + uyw * c[2, 1])
    f[i, j, 5] = f_star[i-1, j-1, 5]
    f[i, j, 6] = f_star[i, j, 8]
    f[i, j, 7] = f_star[i, j, 5] - 2 * w[5] * rho[i, j] / c_s**2 * (uxw * c[5, 0] + uyw * c[5, 1])
    f[i, j, 8] = f_star[i, j, 6] - 2 * w[6] * rho[i, j] / c_s**2 * (uxw * c[6, 0] + uyw * c[6, 1])

    # f_plus[i, j, 0] = f_star[i, j, 0]
    # f_plus[i, j, 1] = (f_star[i-1, j, 1] + f_star[i, j, 1]) / 2
    # f_plus[i, j, 2] = (f_star[i, j-1, 2] + f_star[i, j, 2]) / 2
    # f_plus[i, j, 3] = f_plus[i, j, 1]
    # f_plus[i, j, 4] = f_plus[i, j, 2]
    # f_plus[i, j, 5] = (f_star[i-1, j-1, 5] + f_star[i, j, 5]) / 2
    # f_plus[i, j, 6] = (f_star[i, j, 8] + f_star[i, j, 6]) / 2
    # f_plus[i, j, 7] = f_plus[i, j, 5]
    # f_plus[i, j, 8] = f_plus[i, j, 6]
    #
    # f_minus[i, j, 0] = 0
    # f_minus[i, j, 1] = (f_star[i-1, j, 1] - f_star[i, j, 1]) / 2
    # f_minus[i, j, 2] = (f_star[i, j-1, 2] - f_star[i, j, 2]) / 2
    # f_minus[i, j, 3] = -f_minus[i, j, 1]
    # f_minus[i, j, 4] = -f_minus[i, j, 2]
    # f_minus[i, j, 5] = (f_star[i-1, j-1, 5] - f_star[i, j, 5]) / 2
    # f_minus[i, j, 6] = (f_star[i, j, 8] - f_star[i, j, 6]) / 2
    # f_minus[i, j, 7] = -f_minus[i, j, 5]
    # f_minus[i, j, 8] = -f_minus[i, j, 6]

    f_plus[i, j, 0] = f[i, j, 0]
    f_plus[i, j, 1] = (f[i, j, 1] + f[i, j, 1]) / 2
    f_plus[i, j, 2] = (f[i, j, 2] + f[i, j, 2]) / 2
    f_plus[i, j, 3] = (f[i, j, 3] + f[i, j, 3]) / 2
    f_plus[i, j, 4] = (f[i, j, 4] + f[i, j, 4]) / 2
    f_plus[i, j, 5] = (f[i, j, 5] + f[i, j, 5]) / 2
    f_plus[i, j, 6] = (f[i, j, 6] + f[i, j, 6]) / 2
    f_plus[i, j, 7] = (f[i, j, 7] + f[i, j, 7]) / 2
    f_plus[i, j, 8] = (f[i, j, 8] + f[i, j, 8]) / 2

    f_minus[i, j, 0] = 0
    f_minus[i, j, 1] = (f[i, j, 1] - f[i, j, 1]) / 2
    f_minus[i, j, 2] = (f[i, j, 2] - f[i, j, 2]) / 2
    f_minus[i, j, 3] = (f[i, j, 3] - f[i, j, 3]) / 2
    f_minus[i, j, 4] = (f[i, j, 4] - f[i, j, 4]) / 2
    f_minus[i, j, 5] = (f[i, j, 5] - f[i, j, 5]) / 2
    f_minus[i, j, 6] = (f[i, j, 6] - f[i, j, 6]) / 2
    f_minus[i, j, 7] = (f[i, j, 7] - f[i, j, 7]) / 2
    f_minus[i, j, 8] = (f[i, j, 8] - f[i, j, 8]) / 2

    return f_plus, f_minus

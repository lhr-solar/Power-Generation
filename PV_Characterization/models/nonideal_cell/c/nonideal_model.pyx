"""_summary_
$ python setup.py build_ext --inplace
"""

import math as m
from scipy import constants

cdef float k_b = constants.k
cdef float q = constants.e
cdef float i_sc_ref = 6.15
cdef float v_oc_ref = 0.721
cdef float G_ref = 1000
cdef float T_ref = 298.15
cdef float t_coeff_i_sc = 0.005
cdef float t_coeff_v_oc = -0.0022
cdef float n = 1.0
cdef float i_resolution = 0.005
cdef float margin = 0.0005


def model_nonideal_cell(float g, float t, float r_s, float r_sh, float v):
    """_summary_
    Gets the current for a nonideal cell given input conditions using iterative
    solving.

    Args:
        g (float): Incident irradiance (W/m^2).
        t (float): Cell temperature (K).
        r_s (float): Series resistance (Ohms).
        r_sh (float): Shunt resistance (Ohms).
        v (float): Load voltage (V).

    Returns:
        float (OPT): Current (A) in either single or list form.
    """
    cdef float v_t = k_b * t / q
    cdef float i_sc = i_sc_ref * (g / G_ref) * (1 - t_coeff_i_sc * (T_ref - t))
    cdef float v_oc = v_oc_ref * (1 - t_coeff_v_oc * (T_ref - t)) + n * v_t * m.log(g / G_ref)
    cdef float i_0 = i_sc / (m.exp(v_oc / v_t) - 1)
    cdef float term_1 = (i_sc * (r_sh + r_s) / r_sh)

    # Single voltage measurement.

    cdef float prediction = 0.0
    cdef float new_l1_loss = 0.0
    cdef float travel_speed = i_resolution

    # 1. Calculate the seed output.
    cdef float left = prediction
    cdef float term_2 = -i_0 * (m.exp((v + prediction * r_s) / v_t) - 1)
    cdef float term_3 = -(v + prediction * r_s) / r_sh
    cdef float right = term_1 + term_2 + term_3

    # 2. Calculate the seed loss.
    cdef float l1_loss = abs(right - left)

    # 3. Iteratively solve for prediction.
    while True:
        # 3a. Make a new prediction.
        prediction += travel_speed
        left = prediction
        term_2 = -i_0 * (m.exp((v + prediction * r_s) / v_t) - 1)
        term_3 = -(v + prediction * r_s) / r_sh
        right = term_1 + term_2 + term_3

        # 3b. Calculate new L1 loss and determine whether to continue.
        new_l1_loss = abs(right - left)
        if new_l1_loss >= l1_loss:
            break

    return prediction

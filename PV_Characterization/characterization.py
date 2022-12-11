"""_summary_
@file       characterization.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Given a set of cells, characterize each cell.
@version    0.0.0
@date       2022-12-07
@TODO:      - Add PEP documentation.
"""
import json
import os
import random
import sys

import matplotlib.pyplot as plt
import numpy as np
import tqdm
from lmfit import Parameters as lmfit_parameters
from lmfit import minimize as lmfit_minimize
from scipy.interpolate import interp1d as scipy_interp1d
from scipy.stats import truncnorm as scipy_truncnorm

import models.nonideal_cell.c.nonideal_model as model

NUM_SAMPLES = 125
BOUNDS_GUARD = 0.0005
MEAN = 0.5
STD = 0.2
V_OC = 0.8
V_RES = 100

NUM_LARGE_ROUNDS = 8
NUM_SMALL_ROUNDS = 75
MAX_REPEATS = 5


def residual(params, v, data=None, eps=None):
    # Wrapper around nonideal model to get around continuous fitting issues.
    values = params.valuesdict()
    G = values["IRRAD"]
    T = values["TEMP"]
    r_s = values["R_S"]
    r_sh = values["R_SH"]

    G = G * 1e7 * 1000.00
    T = T * 1e7 * 100.00 + 250.00
    R_S = r_s * 1e7 * 5.00
    R_SH = r_sh * 1e7 * 50.00 + 0.01

    error = [
        b - a
        for a, b in zip(
            [model.model_nonideal_cell(G, T, R_S, R_SH, v_) for v_ in v], data
        )
    ]
    return error


def generate_curve_fit(points, fit_target=0.08, position_idx=0):
    points = np.transpose(points)

    def get_truncated_normal(mean, std, low, high):
        return scipy_truncnorm(
            (low - mean) / std, (high - mean) / std, loc=mean, scale=std
        )

    # Generate starting search space context for the fit.
    center_ = {
        "IRRAD": [
            points[1][0] / 6.15 * 1e-7,
            0.1e-7,  # STD?
        ],  # Smartly choose irradiance mean given y val
        "TEMP": [0.5e-7, 0.25e-7],
        "R_S": [0.04e-7, 0.03e-7],
        "R_SH": [0.5e-7, 0.3e-7],
    }
    range_ = {
        "IRRAD": [0, 1e-7],  # range 0 - 1000 W/M^2
        "TEMP": [0, 1e-7],  # range 250 - 350 K
        "R_S": [0, 1e-7],  # range 0 - 5 ohm
        "R_SH": [0, 1e-7],  # range 0.01 - 50.01 ohm
    }
    guess_ = {
        "IRRAD": get_truncated_normal(
            center_["IRRAD"][0],
            center_["IRRAD"][1],
            range_["IRRAD"][0],
            range_["IRRAD"][1],
        ).rvs(NUM_LARGE_ROUNDS),
        "TEMP": get_truncated_normal(
            center_["TEMP"][0], center_["TEMP"][1], range_["TEMP"][0], range_["TEMP"][1]
        ).rvs(NUM_LARGE_ROUNDS),
        "R_S": get_truncated_normal(
            center_["R_S"][0], center_["R_S"][1], range_["R_S"][0], range_["R_S"][1]
        ).rvs(NUM_LARGE_ROUNDS),
        "R_SH": get_truncated_normal(
            center_["R_SH"][0], center_["R_SH"][1], range_["R_SH"][0], range_["R_SH"][1]
        ).rvs(NUM_LARGE_ROUNDS),
    }

    def generate_params(round):
        fit_params = lmfit_parameters()
        fit_params.add(
            "IRRAD",
            value=guess_["IRRAD"][round],
            min=range_["IRRAD"][0],
            max=range_["IRRAD"][1],
            vary=True,
        )
        fit_params.add(
            "TEMP",
            value=guess_["TEMP"][round],
            min=range_["TEMP"][0],
            max=range_["TEMP"][1],
            vary=False,
        )
        fit_params.add(
            "R_S",
            value=guess_["R_S"][round],
            min=range_["R_S"][0],
            max=range_["R_S"][1],
            vary=False,
        )
        fit_params.add(
            "R_SH",
            value=guess_["R_SH"][round],
            min=range_["R_SH"][0],
            max=range_["R_SH"][1],
            vary=False,
        )
        return fit_params

    # Fit a curve defined by the objective function to the interpolated data.
    best_params = None
    best_result = None
    for large_round in tqdm.trange(
        NUM_LARGE_ROUNDS,
        position=(position_idx * 2) + 1,
        desc=f"Large Round {position_idx}",
        leave=False,
    ):
        # For each large round, reset the parameters and re-run the fit.
        new_params = generate_params(large_round)
        repeat = 0
        prev_res = 100.00

        for small_round in tqdm.trange(
            NUM_SMALL_ROUNDS,
            position=(position_idx * 2) + 2,
            desc=f"Small Round {position_idx}",
            leave=False,
        ):
            # For each small round, optimize each parameter until we settle at a
            # good spot.
            randoms = [False] * 4
            if small_round < 8:
                randoms[small_round % 4] = True
            else:
                num_choices = int(random.random() * 3) + 1
                for choice in random.choices([0, 1, 2, 3], k=num_choices):
                    randoms[choice] = True

            # Modify which parameters to optimize.
            new_params["IRRAD"].vary = randoms[0]
            new_params["TEMP"].vary = randoms[1]
            new_params["R_S"].vary = randoms[2]
            new_params["R_SH"].vary = randoms[3]

            # Run curve fitting.
            result = lmfit_minimize(
                residual,
                new_params,
                args=(points[0],),
                kws={"data": points[1]},
                method="Powell",
            )

            # Stash result.
            new_params["IRRAD"].value = result.params["IRRAD"].value
            new_params["TEMP"].value = result.params["TEMP"].value
            new_params["R_S"].value = result.params["R_S"].value
            new_params["R_SH"].value = result.params["R_SH"].value

            # Early exit.
            if result.chisqr == prev_res:
                repeat += 1
                if repeat == MAX_REPEATS:
                    break
            else:
                prev_res = result.chisqr
                repeat = 0

            if result.chisqr <= fit_target:
                break

        if best_result is None or best_result.chisqr > result.chisqr:
            best_params = new_params
            best_result = result

        # Early exit.
        if best_result.chisqr <= fit_target:
            break

    res = [
        best_params["IRRAD"].value * 1e7 * 1000.00,
        best_params["TEMP"].value * 1e7 * 100.00 + 250.00,
        best_params["R_S"].value * 1e7 * 5.00,
        best_params["R_SH"].value * 1e7 * 50.00 + 0.01,
    ]
    return res, best_result.chisqr


def generate_characterization(cell, fit_target=0.08, cell_idx=0):
    # Get the cell data from the file.
    data = {}
    with open(cell["file_path"], encoding="utf-8") as f:
        start = False
        for line in f:
            entries = line.split(",")
            if len(entries) > 1:
                if entries[0] == "Gate (V)":
                    start = True
                elif start:
                    entries = [float(entry.strip()) for entry in entries]
                    if entries[1] in data:
                        data[entries[1]].append(entries[2])
                    else:
                        data[entries[1]] = [entries[2]]

    # points_orig       is original datapoints
    # points            is cleaned up datapoints (averaged duplicates)
    # points_sampled    is uniformly sampled from the cleaned up datapoints
    # points_interp     is interpolated points with a gaussian around the knee point
    # points_fit        is distributed curve fit
    # points_filtered   is the fit without negative y points
    points_orig = []
    points = []
    for x, y in data.items():
        points_orig.extend([x, y[i]] for i in range(len(y)))
        points.append([x, sum(y) / len(y)])

    # Sort ponts.
    points_orig = sorted(points_orig)
    points = sorted(points)

    # Sample points to get a smaller subset for interpolation.
    num_samples = NUM_SAMPLES
    if len(points) < num_samples:
        num_samples = len(points)
    points_sampled = random.sample(points, num_samples)
    points_sampled = sorted(points_sampled)

    # Generate an interpolation from the existing samples.
    f_interp = scipy_interp1d(*np.transpose(points_sampled), kind="slinear")
    resolution = BOUNDS_GUARD
    x_vals = np.transpose(points_sampled)[0]
    points_interp = [
        [sample, f_interp(sample)[()]]
        for sample in np.random.normal(MEAN, STD, NUM_SAMPLES)
        if sample > min(x_vals) + resolution and sample < max(x_vals) - resolution
    ]

    # Join existing samples with the interpolated samples.
    points_interp.extend(points_sampled)
    points_interp = sorted(points_interp)

    # Generate popts associated with the I-V curve fit.
    p_opt, best_fit_err = generate_curve_fit(points_interp, fit_target, cell_idx)

    # Generate the curve from the p_opts.
    points_fit = sorted(
        [
            [v, model.model_nonideal_cell(*p_opt, v)]
            for v in np.arange(0, V_OC, V_OC / V_RES)
        ]
    )

    # Prune all fit points that have negative values.
    points_filtered = sorted([[x, y] for x, y in points_fit if y >= 0.005 and x >= 0])

    v_oc = 0.0
    i_sc = 0.0
    v_mpp = 0.0
    i_mpp = 0.0
    for v, i in points_filtered:
        if v_oc < v:
            v_oc = v
        if i_sc < i:
            i_sc = i
        if v * i > v_mpp * i_mpp:
            v_mpp = v
            i_mpp = i

    cell = {
        "file_name": os.path.split(os.path.splitext(cell["file_path"])[0])[1],
        "points_orig": points,
        "points_filtered": points_filtered,
        "p_opt": p_opt,
        "v_oc": v_oc,
        "i_sc": i_sc,
        "v_mpp": v_mpp,
        "i_mpp": i_mpp,
        "fit_err": best_fit_err,
    }

    return cell


def save_characterization(path, cell):
    with open(f"{path}/{cell['file_name']}.char", "w") as f:
        json.dump(cell, f, indent=4)


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    try:
        import pretty_traceback

        pretty_traceback.install()
    except ImportError:
        pass  # no need to fail because of missing dev dependency

    cells = {
        0: {"file_path": "./cell_data/RP/RP_1_8_27_22.log"},
        1: {"file_path": "./cell_data/control/RP_TEST1_3_2022-10-01_11-04-26.log"},
    }

    for cell_idx, cell in cells.items():
        cells[cell_idx] = generate_characterization(cell)

    fig = plt.figure()

    # Plot graphs of each cell.
    ax = fig.add_subplot(121)
    ax2 = fig.add_subplot(122)

    for cell in cells.values():
        points_orig = np.transpose(cell["points_orig"])
        points_filtered = np.transpose(cell["points_filtered"])

        ax.scatter(points_orig[0], points_orig[1], c="b", s=5)
        ax2.scatter(points_orig[0], points_orig[0] * points_orig[1], c="b", s=5)

        ax.scatter(points_filtered[0], points_filtered[1], c="r", s=5)
        ax2.scatter(
            points_filtered[0], points_filtered[0] * points_filtered[1], c="r", s=5
        )

    ax.set_xlabel("Voltage (V)")
    ax.set_ylabel("Current (A)")
    ax.set_title("I-V Curve")
    ax.grid(True)
    ax2.set_xlabel("Voltage (V)")
    ax2.set_ylabel("Power (W)")
    ax2.set_title("P-V Curve")
    ax2.grid(True)

    plt.show()

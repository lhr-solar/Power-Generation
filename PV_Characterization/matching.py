"""_summary_
@file       matching.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Given a set of cells and a voltage applied across all cells in
            series, determine the voltage across each cell that maximizes some
            metric.
@version    0.0.0
@date       2022-12-08
@TODO:      - Switch matplotlib to pyqtgraph in example.
            - Add PEP documentation.
"""
import itertools
import json
import math
import sys

# import pyqtgraph.opengl as gl
# from pyqtgraph.Qt import QtCore, QtGui
import matplotlib.pyplot as plt
import numpy as np
import tqdm

import models.nonideal_cell.c.nonideal_model as model

STC = {
    "G": 1000.00,
    "T": 298.15,
}
SEARCH_RESOLUTION = 0.005

# NOTE: "dist_from_mpp_opt_0" does not work as expected.
optimizers = ["power_opt_0", "dist_from_mpp_opt_0"]


def optimizer_wrapper(optimizer_name, cells, cell_voltages, cell_currents):
    match optimizer_name:
        case "power_opt_0":
            return [sum(np.multiply(cell_voltages, cell_currents)), "max"]
        case "dist_from_mpp_opt_0":
            # Get mpps frome each cell
            cell_vmpps = [cell["v_mpp"] for cell in cells.values()]
            return [
                np.divide(
                    sum(np.abs(np.subtract(list(cell_voltages), cell_vmpps))),
                    len(cell_voltages),
                ),
                "min",
            ]
        case _:
            return [0, "none"]


def generate_search_space(cells, sum_constraint=None):
    """_summary_
    The search space is an n-dimensional hypercube, where n is the number of
    cells that need to be matched - 1. The center of the hypercube is
        (V_mpp_0, ..., V_mpp_x) which represents the
    maximum power point voltage of each cell in the matching.
    The distance from the center of the hypercube to any of the
    edges is the minimum distance from the v_mpp to v_oc amongst
    all cells in the matching.
    """

    v_mpps = [item["v_mpp"] for item in cells.values()]
    v_ocs = [item["v_oc"] for item in cells.values()]
    v_tot = sum(v_mpps)
    if sum_constraint is not None:
        v_tot = sum_constraint

    # TODO: our bounds only works well for 2D: the lower bound for one can be
    # twice the upper bound distance for two other cells in 3D.

    # Generate bounds to search space.
    d = min(
        [v_oc - v_mpp for v_mpp, v_oc in zip(v_mpps, v_ocs)]
    )  #  + 0.3  # Our constraining factor.

    # Get points that represent the search space.
    search_space = []
    for idx in range(len(cells)):
        bounds = [v_mpps[idx] - d, v_mpps[idx] + d]
        if bounds[0] < 0:
            bounds[0] = 0
        if bounds[1] > v_ocs[idx]:
            bounds[1] = v_ocs[idx]

        components = []
        for component in np.arange(
            bounds[0], bounds[1] + SEARCH_RESOLUTION, SEARCH_RESOLUTION
        ):
            components.append(component)
        search_space.append(components)

    if sum_constraint == 0:
        permutations = [permutation for permutation in itertools.product(*search_space)]
    else:
        permutations = [
            permutation
            for permutation in itertools.product(*search_space)
            if math.isclose(sum(permutation), v_tot, abs_tol=SEARCH_RESOLUTION)
        ]

    return permutations


def solve_search_space(
    cells, permutations, optimizer_name, debug=False, position_index=0
):
    solutions = []
    best_perm = None
    for permutation in tqdm.tqdm(
        permutations,
        desc=f"Voltage Permutation {position_index}",
        position=(position_index * 2) + 2,
        total=len(permutations),
        leave=False,
    ):
        # Grab min current for the set of cells.
        min_current = 100
        for component, cell_id in zip(permutation, cells.keys()):
            cell_params = [
                STC["G"],
                STC["T"],
                cells[cell_id]["r_s"],
                cells[cell_id]["r_sh"],
                component,
            ]
            cell_current = model.model_nonideal_cell(*cell_params)
            if cell_current < min_current:
                min_current = cell_current
        solutions.append(min_current)

        # Run in optimizer to generate evaluation metric.
        # TODO: add parallelization option for multiple optimizer comparisons.
        metric = optimizer_wrapper(
            optimizer_name, cells, permutation, [min_current] * len(permutation)
        )

        if metric[1] not in ["min", "max"]:
            raise Exception("Metric is not resolved.")
        if best_perm is None:
            best_perm = [metric[0], permutation, min_current]
        else:
            match metric[1]:
                case "min":
                    if metric[0] < best_perm[0]:
                        best_perm = [metric[0], permutation, min_current]
                case "max":
                    if best_perm[0] < metric[0]:
                        best_perm = [metric[0], permutation, min_current]
                case _:
                    raise Exception("Metric is not resolved.")

    if debug:
        return best_perm, solutions
    else:
        return best_perm


def generate_matches(
    cells,
    match_size=4,
    max_matches=None,
    optimizer_name=optimizers[0],
    position_index=0,
):
    matches = {}
    attempted_permutations = {}

    cell_names = list(cells.keys())

    # Generate list of permutations.
    permutations = list(itertools.combinations(cell_names, match_size))
    for permutation in tqdm.tqdm(
        permutations,
        desc=f"Cell Permutation {position_index}",
        position=(position_index * 2) + 1,
        total=len(permutations),
        leave=False,
    ):
        cell_data = {}
        for cell_name in permutation:
            cell_data[cell_name] = {
                "v_mpp": cells[cell_name]["v_mpp"],
                "v_oc": cells[cell_name]["v_oc"],
                "r_s": cells[cell_name]["p_opt"][2],
                "r_sh": cells[cell_name]["p_opt"][3],
            }

        # Solve the permutation and update the best permutation.
        search_space = generate_search_space(cell_data)
        solution_space = solve_search_space(
            cell_data, search_space, optimizers[0], position_index=position_index
        )
        attempted_permutations[permutation] = solution_space

    match optimizer_name:
        case "power_opt_0":
            # Sort by max
            attempted_permutations = sorted(
                attempted_permutations.items(),
                key=lambda item: item[1][0],
                reverse=True,
            )
        case "dist_from_mpp_opt_0":
            # Sort by min
            attempted_permutations = sorted(
                attempted_permutations.items(),
                key=lambda item: item[1][0],
                reverse=False,
            )
        case _:
            raise Exception("Metric is not resolved.")

    if max_matches is None:
        while len(attempted_permutations) > 0:
            best_permutation = attempted_permutations.pop(0)

            # Pull out all permutations with one of the members specified
            for index in sorted(
                set(
                    idx
                    for idx, perm in enumerate(attempted_permutations)
                    for cell_name in best_permutation[0]
                    if cell_name in perm[0]
                ),
                reverse=True,
            ):
                del attempted_permutations[index]

            # Generate match
            matches[len(matches)] = {
                "cell_names": {
                    int(
                        cell_name
                    ): f"{' '.join(cells[cell_name]['file_name'].split('_')[:2])}"
                    for cell_name in best_permutation[0]
                },
                "cell_voltages": best_permutation[1][1],
                "match_metric": best_permutation[1][0],
            }

    else:
        while len(attempted_permutations) > 0 and len(matches) <= max_matches:
            best_permutation = attempted_permutations.pop(0)

            # Pull out all permutations with one of the members specified
            for index in sorted(
                set(
                    idx
                    for idx, perm in enumerate(attempted_permutations)
                    for cell_name in best_permutation[0]
                    if cell_name in perm[0]
                ),
                reverse=True,
            ):
                del attempted_permutations[index]

            # Generate match
            matches[len(matches)] = {
                "cell_names": {
                    cell_name: f"{' '.join(cells[cell_name]['file_name'].split('_')[:2])}"
                    for cell_name in best_permutation[0]
                },
                "cell_voltages": best_permutation[1][1],
                "match_metric": best_permutation[1][0],
            }

    return matches


def save_matches(path, matches):
    with open(f"{path}/matches.json", "w") as f:
        json.dump(matches, f, indent=4)


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    try:
        import pretty_traceback

        pretty_traceback.install()
    except ImportError:
        pass  # no need to fail because of missing dev dependency

    cells = {
        0: {"v_mpp": 0.621, "v_oc": 0.721, "p_opt": [1000, 298.15, 0.01, 2]},
        1: {"v_mpp": 0.640, "v_oc": 0.721, "p_opt": [1000, 298.15, 0.01, 2]},
        2: {"v_mpp": 0.621, "v_oc": 0.721, "p_opt": [1000, 298.15, 0.01, 2]},
        3: {"v_mpp": 0.651, "v_oc": 0.721, "p_opt": [1000, 298.15, 0.01, 2]},
        4: {"v_mpp": 0.621, "v_oc": 0.721, "p_opt": [1000, 298.15, 0.05, 2]},
        5: {"v_mpp": 0.621, "v_oc": 0.721, "p_opt": [1000, 298.15, 0.06, 2]},
        6: {"v_mpp": 0.621, "v_oc": 0.638, "p_opt": [1000, 298.15, 0.01, 2]},
        7: {"v_mpp": 0.621, "v_oc": 0.645, "p_opt": [1000, 298.15, 0.01, 2]},
        8: {"v_mpp": 0.621, "v_oc": 0.800, "p_opt": [1000, 298.15, 0.01, 2]},
        9: {"v_mpp": 0.621, "v_oc": 0.780, "p_opt": [1000, 298.15, 0.01, 2]},
    }

    matches = generate_matches(cells, match_size=2, max_matches=5)
    print(matches)

    fig = plt.figure()

    # Plot rank by metric.
    ax = fig.add_subplot()

    ax.plot(
        [match_idx for match_idx in matches.keys()],
        [match["match_metric"] for match in matches.values()],
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=12,
    )

    ax.set_xlim(left=-1.0, right=len(matches))
    ax.set_ylim(bottom=0.0)
    ax.set_xlabel("Ranking")
    ax.set_ylabel("Compatibility Metric")
    ax.set_title("Match Compatibility")
    ax.grid(True)

    plt.show()

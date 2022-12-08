"""_summary_
@file       characterization.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Characterizes, clusters, and matches all cells in a given folder.
@version    0.0.0
@date       2022-12-08
@TODO:      - report cells with bad fit
@TODO:      - report cells with bad r_s, r_sh
"""

import argparse
import json
import multiprocessing
import os
import sys
import time

import matplotlib.pyplot as plt
import numpy as np
import p_tqdm
import pandas as pd
import plottable
from scipy.cluster.hierarchy import dendrogram

from characterization import generate_characterization, save_characterization
from clustering import generate_clusters, save_clusters
from matching import generate_matches, save_matches

fig = plt.figure()


def visualize_cells(cells):
    # Plot graphs of each cell.
    ax = fig.add_subplot(231)
    ax2 = fig.add_subplot(234)

    for cell in cells.values():
        points_orig = np.transpose(cell["points_orig"])
        points_filtered = np.transpose(cell["points_filtered"])

        ax.scatter(points_orig[0], points_orig[1], c="b", s=3)
        ax2.scatter(points_orig[0], points_orig[0] * points_orig[1], c="b", s=3)

        ax.plot(points_filtered[0], points_filtered[1], c="r")
        ax2.plot(
            points_filtered[0],
            points_filtered[0] * points_filtered[1],
            c="r",
        )

    ax.set_xlabel("Voltage (V)")
    ax.set_ylabel("Current (A)")
    ax.set_title("I-V Curve")
    ax.grid(True)
    ax2.set_xlabel("Voltage (V)")
    ax2.set_ylabel("Power (W)")
    ax2.set_title("P-V Curve")
    ax2.grid(True)


def visualize_clusters(clusters, variance_threshold, head, cluster_steps):
    # Plot dendrogram.
    def fancy_dendrogram(*args, **kwargs):
        max_d = kwargs.pop("max_d", None)
        if max_d and "color_threshold" not in kwargs:
            kwargs["color_threshold"] = max_d
        if max_d:
            plt.axhline(y=max_d, c="k")
        plt.title("Clustering Dendrogram")
        plt.xlabel("Cell")
        plt.ylabel("Distance (Ward)")
        ddata = dendrogram(*args, **kwargs)
        plt.ylim(top=max_d * 2.5)
        return ddata

    ax = fig.add_subplot(232)
    ax = fancy_dendrogram(
        cluster_steps,
        orientation="top",
        labels=head,
        leaf_rotation=90.0,
        leaf_font_size=10.0,
        count_sort=False,
        distance_sort=True,
        show_contracted=True,
        no_labels=True,
        max_d=variance_threshold,
    )

    # Plot clusters.
    ax2 = fig.add_subplot(235, projection="3d")
    centroids = []
    for cluster in clusters.values():
        centroids.append(cluster["centroid"])
        colorings = [
            ax["leaves_color_list"][ax["ivl"].index(cell_name)]
            for cell_name in cluster["cells"]
        ]
        ax2.scatter(*np.transpose(cluster["vectors"]), c=colorings, s=8, alpha=0.7)
    ax2.scatter(*np.transpose(centroids), s=15, c="r", alpha=1)
    ax2.set_xlabel("V_OC (V)")
    ax2.set_ylabel("I_SC (A)")
    ax2.set_zlabel("FF")
    ax2.set_title("Cell Clusterings")
    ax2.grid(True)


def visualize_matches(matches, cells):
    # Plot rank by metric.
    ax = fig.add_subplot(233)

    ax.plot(
        [match_idx for match_idx in matches.keys()],
        [match["match_metric"] for match in matches.values()],
        marker="o",
        linestyle="dashed",
        linewidth=2,
        markersize=5,
    )

    ax.set_xlim(left=-1.0, right=len(matches))
    ax.set_ylim(bottom=0.0)
    ax.set_xlabel("Ranking")
    ax.set_ylabel("Compatibility Metric")
    ax.set_title("Match Compatibility")
    ax.grid(True)

    ax2 = fig.add_subplot(236)
    ax2.set_axis_off()
    ax2.set_title("Match Table")

    header = []
    match_table = []
    for idx, match in enumerate(matches.values()):
        if idx == 0:
            header.extend([f"Cell {i}" for i in range(len(match["cell_names"]))])
        match_table.append(
            [
                f"{' '.join(cells[cell_name]['file_name'].split('_')[:2])}"
                for cell_name in match["cell_names"]
            ]
        )

    d = pd.DataFrame(match_table, columns=header)
    plottable.Table(
        d,
        cell_kw={},
        textprops={"ha": "center", "va": "center"},
        odd_row_color="#f0f0f0",
        even_row_color="#e0f6ff",
    )


def multiprocess_generate_characterization(cell_idx, cell, use_cached):
    # If characterization file already exists, load it and skip
    if f"{cell['file_name']}.char" in dir_list and use_cached is True:
        with open(f"{path}{cell['file_name']}.char") as f:
            return cell_idx, json.load(f)

    # Else, characterize it.
    else:
        cell = generate_characterization(cell, cell_idx)
        save_characterization(path, cell)
        return cell_idx, cell


def multiprocess_generate_matching(cluster_idx, cluster_cells, match_size):
    return cluster_idx, generate_matches(
        cluster_cells, match_size=match_size, position_index=cluster_idx
    )


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    try:
        import pretty_traceback

        pretty_traceback.install()
    except ImportError:
        pass  # no need to fail because of missing dev dependency

    parser = argparse.ArgumentParser(
        description="Characterizes, clusters, and matches photovoltaic cells."
    )
    parser.add_argument("folder_path", help="Path to a set of .log PV files.")
    parser.add_argument(
        "--use_cached",
        help="Use any cached .char files for each PV if any. Default True.",
        type=bool,
        default=True,
    )
    parser.add_argument(
        "--num_cpus",
        help="Set the number of CPUs to parallelize the work. Default is the max number of system CPUs.",
        type=int,
        default=multiprocessing.cpu_count(),
    )
    parser.add_argument(
        "--max_matches",
        help="The number of matches to generate of a fixed size. Default is 1.",
        type=int,
        default=1,
    )
    parser.add_argument(
        "--match_size",
        help="The size of the match in number of cells. Default is 2.",
        type=int,
        default=2,
    )

    args = parser.parse_args()

    if args.num_cpus > multiprocessing.cpu_count():
        raise Exception("Too many cpus specified!")
    if args.max_matches < 1:
        raise Exception("Number of matches generated should be a positive integer.")
    if args.match_size < 1:
        raise Exception("Match size should be a positive integer.")

    # Get PV data directory.
    path = args.folder_path
    dir_list = os.listdir(path)

    # Characterize each cell curve.
    print("Characterizing Cells...")
    cells = {}
    for file_name in dir_list:
        if os.path.splitext(file_name)[1] == ".log":
            cells[len(cells)] = {
                "file_name": os.path.splitext(file_name)[0],
                "file_path": f"{path}{file_name}",
            }

    results = p_tqdm.p_umap(
        multiprocess_generate_characterization,
        [cell_idx for cell_idx in range(len(cells))],
        [cells[cell_idx] for cell_idx in range(len(cells))],
        [args.use_cached] * len(cells),
        total=len(cells),
        desc=f"Fitting file",
        leave=False,
        position=0,
        num_cpus=args.num_cpus,
    )

    for cell_idx, cell in results:
        cells[cell_idx] = cell

    print("Visualizing Cells...")
    visualize_cells(cells)

    # Cluster cells.
    print("Clustering Cells...")
    clusters, variance_threshold, head, cluster_steps = generate_clusters(
        cells, "v_oc_i_sc_v_mpp_0", debug=True
    )
    save_clusters(path, clusters)

    print("Visualizing Clusters...")
    visualize_clusters(clusters, variance_threshold, head, cluster_steps)

    # Match cells.
    print("Matching Cells...")
    matches = {}
    if f"matches.json" in dir_list and args.use_cached is True:
        with open(f"{path}matches.json") as f:
            matches = json.load(f)
    else:
        results = p_tqdm.p_umap(
            multiprocess_generate_matching,
            [cluster_idx for cluster_idx in range(len(clusters))],
            [
                {
                    cell_idx: cells[cell_idx]
                    for cell_idx in cells.keys() & cluster["cells"]
                }
                for cluster in clusters.values()
            ],
            [args.match_size] * len(clusters),
            total=len(clusters),
            desc=f"Matching cells in cluster",
            leave=False,
            position=0,
            num_cpus=args.num_cpus,
        )

        clusters = []
        for cluster_idx, matches in results:
            clusters.append([cluster_idx, matches])
        clusters = sorted(clusters)
        for cluster_idx, all_matches in clusters:
            for match_idx, match in all_matches.items():
                if len(matches) > args.max_matches:
                    break
                matches[match_idx] = match

        save_matches(path, matches)

    print("Visualizing Matches...")
    if len(matches) > 0:
        visualize_matches(matches, cells)

    print("End program. Displaying results.")
    plt.show()

    for i in range(3):
        time.sleep(0.2)
        print("\a")

    plt.savefig(f"{path}characterization.png", dpi=2000)
    sys.exit(0)

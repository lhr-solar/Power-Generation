"""_summary_
@file       characterization.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Characterizes, clusters, and matches all cells in a given folder.
@version    0.0.0
@date       2022-12-08
@TODO:      - report cells with bad r_s, r_sh
@TODO       - faster plotting using blitting, then pyqtgraph
"""

import argparse
import json
import multiprocessing
import os
import sys

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


def visualize_clusters(
    clusters, variance_threshold, head, cluster_steps, plot_cluster_zoomed_out
):
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
            ax["leaves_color_list"][ax["ivl"].index(int(cell_name))]
            for cell_name in cluster["cells"].keys()
        ]
        ax2.scatter(*np.transpose(cluster["vectors"]), c=colorings, s=8, alpha=0.7)
    ax2.scatter(*np.transpose(centroids), s=15, c="r", alpha=1)
    if plot_cluster_zoomed_out:
        ax2.set_xlim(
            left=0.0,
        )
        ax2.set_ylim(
            bottom=0.0,
        )
        ax2.set_zlim(
            0.0,
        )
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
                f"{' '.join(cells[int(cell_name)]['file_name'].split('_')[:2])}"
                for cell_name in match["cell_names"].keys()
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


def generate_report(
    path, cells, clusters, matches, threshold_fit_err, threshold_variance
):
    with open(f"{path}report.md", "w") as f:

        def out(str):
            f.write(str + "\n")
            print(str)

        out(f"# Characterization Report")
        out(f"\n## Characterization\n")
        out(f"Characterized {len(cells)} cells from the {path} folder.")

        median = np.median([cell["fit_err"] for cell in cells.values()])
        outliers = [
            cell for cell in cells.values() if cell["fit_err"] > threshold_fit_err
        ]

        out(
            f"The median fit parameter is {median} with {len(outliers)} beyond {threshold_fit_err}."
        )
        if len(outliers) > 0:
            out(f"The outlier cells are:\n")
            for outlier in outliers:
                out(f"- {outlier['file_name']} with fit error {outlier['fit_err']}")
            out(
                f"It is suggested to retest, rerun, or remove these cells from the dataset."
            )

        out(f"\n## Clustering\n")

        median = np.median(
            [cluster["variance"] for cluster in clusters.values()], axis=0
        )
        outliers = [
            (cluster_idx, cluster)
            for cluster_idx, cluster in clusters.items()
            if np.var(cluster["variance"]) > threshold_variance
        ]

        out(
            f"The characterized cells form {len(clusters)} clusters, with a median variance of {median} for each dimension."
        )
        out(
            f"There are {len(outliers)} clusters with a variance beyond {threshold_variance}."
        )
        if len(outliers) > 0:
            out(f"These relatively loose clusters are:\n")
            for outlier in outliers:
                out(
                    f"- {outlier[0]} containing cells {[cells[int(cell_name)]['file_name'] for cell_name in outlier[1]['cells']]}."
                )
                out(f"  - Centroid {outlier[1]['centroid']}")
                out(f"  - Variance {outlier[1]['variance']}")
                out(f"  - STD {outlier[1]['std']}")

            out(f"Loose clusters may generate worse matchings.")

        outliers = [
            (cluster_idx, cluster)
            for cluster_idx, cluster in clusters.items()
            if len(cluster["cells"]) == 1
        ]

        out(f"There are {len(outliers)} clusters with only 1 member.")
        if len(outliers) > 0:
            out(f"These isolated clusters are:\n")
            for outlier in outliers:
                out(
                    f"- {outlier[0]} containing cell {[cells[int(cell_name)]['file_name'] for cell_name in outlier[1]['cells']]}."
                )
                out(f"  - Centroid {outlier[1]['centroid']}")

            out(f"\nIsolated clusters will not be used for final matching.")

        out(f"\n## Matching\n")

        out(
            f"The clusters generate {len(matches)} matches using the specified parameters."
        )
        out(f"The matches, ordered by match metric, are as follows:\n")
        out(f"- metric used `{'power_opt_0'}`")
        for match_idx, match in matches.items():
            out(f"- rank {match_idx} match")
            out(
                f"  - cells {[cells[int(cell_name)]['file_name'] for cell_name in match['cell_names']]}"
            )
            out(f"  - resulted in a metric of {match['match_metric']}")

        """_summary_
        Characterized [] cells from the [] folder.
        The mean fit parameter is [] with [] outliers beyond [].
        The outlier cells are:
          - [] with fit error []
          - ...
        It is suggested to retest, rerun, or remove these cells from the
        dataset.

        The characterized cells form [] clusters, with a median variance of [],
        [], [] for each dimension.

        The clusters generated [] matches using the specified parameters. The
        matches, ordered by match metric, are as follows:
          - metric used []
          - rank [] match
            - cells
              - []
              - ...
            - resulted in a metric of []
          - ...
        """


def multiprocess_generate_characterization(
    cell_idx, cell, no_cache, improve_cell_cache, fit_target
):
    # If characterization file already exists, load it and skip
    if no_cache:
        save_cell = False
        replace_cell = False
        # Generate cell data from scratch.
        if improve_cell_cache and f"{cell['file_name']}.char" in dir_list:
            # Replace existing cell data if better.
            with open(f"{path}{cell['file_name']}.char") as f:
                cell_cache = json.load(f)
            if cell_cache["fit_err"] <= fit_target:
                replace_cell = True
            else:
                # Only run the characterization if we're not already at our
                # target.
                cell = generate_characterization(cell, fit_target, cell_idx)
                if cell["fit_err"] < cell_cache["fit_err"]:
                    save_cell = True
                else:
                    replace_cell = True
        else:
            cell = generate_characterization(cell, fit_target, cell_idx)
            save_cell = True

        if replace_cell:
            cell = cell_cache
        if save_cell:
            save_characterization(path, cell)

        return cell_idx, cell
    else:
        # Use existing cell data.
        with open(f"{path}{cell['file_name']}.char") as f:
            return cell_idx, json.load(f)


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
    parser.add_argument(  # No cache is false: use the cache
        "--no_cache",
        help="Disable the use of cached files generated from previous runs if any. Cache is on by default.",
        action="store_true",
    )
    parser.add_argument(
        "--improve_cell_cache",
        help="If the current cell characterization is better then the cache, replace it. Pairs with --no_cache.",
        action="store_true",
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
    parser.add_argument(
        "--fit_target",
        help="Target fit error for cell characterization. Default is 0.08.",
        type=float,
        default=0.08,
    )
    parser.add_argument(
        "--threshold_variance",
        help="The variance threshold by which to delineate clusters. Default is 0.2.",
        type=float,
        default=0.2,
    )
    parser.add_argument(
        "--no_report",
        help="Disables report generation. Report is generated by default.",
        action="store_true",
    )
    parser.add_argument(
        "--full_plot",
        help="Plots the clusters zoomed out. Default disabled.",
        action="store_true",
    )
    parser.add_argument(
        "--filter_ff",
        help="Value to filter out cells by FF. Default 0.0.",
        type=float,
        default=0.0,
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
    for file_name in sorted(dir_list):
        if os.path.splitext(file_name)[1] == ".log":
            cells[len(cells)] = {
                "file_name": os.path.splitext(file_name)[0],
                "file_path": f"{path}{file_name}",
            }

    results = p_tqdm.p_umap(
        multiprocess_generate_characterization,
        [cell_idx for cell_idx in range(len(cells))],
        [cells[cell_idx] for cell_idx in range(len(cells))],
        [args.no_cache] * len(cells),
        [args.improve_cell_cache] * len(cells),
        [args.fit_target] * len(cells),
        total=len(cells),
        desc=f"Fitting file",
        leave=False,
        position=0,
        num_cpus=args.num_cpus,
    )
    for cell_idx, cell in results:
        cells[cell_idx] = cell

    # Filter cells.
    cells = {
        cell_idx: cell_data
        for cell_idx, cell_data in cells.items()
        if (cell_data["v_mpp"] * cell_data["i_mpp"])
        / (cell_data["v_oc"] * cell_data["i_sc"])
        > args.filter_ff
    }

    os.system("cls||clear")
    print("Visualizing Cells...")
    visualize_cells(cells)

    # Cluster cells.
    print("Clustering Cells...")
    clusters, variance_threshold, head, cluster_steps = generate_clusters(
        cells,
        "v_oc_i_sc_v_mpp_0",
        debug=True,
        variance_threshold=args.threshold_variance,
    )
    save_clusters(path, clusters)

    print("Visualizing Clusters...")
    visualize_clusters(
        clusters, variance_threshold, head, cluster_steps, args.full_plot
    )

    # Match cells.
    print("Matching Cells...")
    matches = {}
    if f"matches.json" in dir_list and args.no_cache is False:
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

        match_clusters = []
        for cluster_idx, cluster_matches in results:
            match_clusters.append([cluster_idx, cluster_matches])
        match_clusters = sorted(match_clusters)
        for cluster_idx, all_matches in match_clusters:
            for match_idx, match in all_matches.items():
                if len(matches) >= args.max_matches:
                    break
                matches[match_idx] = match

        save_matches(path, matches)

    os.system("cls||clear")
    print("Visualizing Matches...")
    if len(matches) > 0:
        visualize_matches(matches, cells)

    print("End program. Displaying results.")

    if args.no_report is False:
        generate_report(
            path, cells, clusters, matches, args.fit_target, args.threshold_variance
        )

    print("\a")

    fig = plt.gcf()
    fig.set_size_inches(15, 9, forward=True)
    plt.tight_layout()
    plt.savefig(f"{path}characterization.png", dpi=500)
    plt.show()

    sys.exit(0)

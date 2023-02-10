"""_summary_
@file       clustering.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Given a set of cells, cluster them based on some heuristic.
@version    0.0.0
@date       2022-12-07
@TODO:      - Add PEP documentation.
            - Play with different clustering algorithms
              https://scikit-learn.org/stable/auto_examples/cluster/plot_cluster\
              _comparison.html#sphx-glr-auto-examples-cluster-plot-cluster-comparison-py
"""
import json
import sys

import matplotlib.pyplot as plt
import numpy as np
from scipy.cluster.hierarchy import cut_tree, dendrogram, linkage

heuristics = ["v_oc_i_sc_v_mpp_0"]


def heuristic_wrapper(heuristic_name, cells):
    head = []
    vectors = []
    match heuristic_name:
        case "v_oc_i_sc_v_mpp_0":
            for cell_id, cell in cells.items():
                head.append(cell_id)
                vectors.append(
                    [
                        cell["v_oc"],
                        cell["i_sc"],
                        (cell["v_mpp"] * cell["i_mpp"]) / (cell["v_oc"] * cell["i_sc"]),
                    ]
                )
        case _:
            return None

    return head, vectors


def generate_clusters(cells, heuristic_name, variance_threshold=0.2, debug=False):
    # Generate n-vectors for each cell based on our heuristic.
    head, vectors = heuristic_wrapper(heuristic_name, cells)
    if head is None:
        raise Exception("Heuristic is not resolved.")

    # Generate the cluster tree using hierarchical clustering.
    cluster_steps = linkage(vectors, "ward", optimal_ordering=True)

    # Cut the tree using our threshold that represents the variance in the
    # cluster.
    cut_indices = cut_tree(cluster_steps, height=variance_threshold)

    # Generate clusters using our cut.
    clusters = {}
    for cell_idx, (cell_name, cut_idx) in enumerate(zip(head, cut_indices)):
        cut_idx = int(cut_idx[0])  # Cast as int to prevent json dump errors later.
        if cut_idx not in clusters:
            clusters[cut_idx] = {
                "cells": {
                    cell_name: f"{' '.join(cells[cell_name]['file_name'].split('_')[:2])}"
                },
                "vectors": [vectors[cell_idx]],
            }
        else:
            clusters[cut_idx]["cells"][
                cell_name
            ] = f"{' '.join(cells[cell_name]['file_name'].split('_')[:2])}"
            clusters[cut_idx]["vectors"].append(vectors[cell_idx])

    # Generate the cluster centroid, variance, and STD.
    for cluster in clusters.values():
        cluster["centroid"] = np.mean(cluster["vectors"], axis=0).tolist()
        cluster["variance"] = np.var(cluster["vectors"], axis=0).tolist()
        cluster["std"] = np.std(cluster["vectors"], axis=0).tolist()

    if debug:
        return clusters, variance_threshold, head, cluster_steps
    else:
        return clusters


def save_clusters(path, clusters):
    with open(f"{path}/clustering.json", "w") as f:
        json.dump(clusters, f, indent=4)


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    try:
        import pretty_traceback

        pretty_traceback.install()
    except ImportError:
        pass  # no need to fail because of missing dev dependency

    cells = {
        "TEST0": {"v_oc": 0.711, "i_sc": 6.15, "v_mpp": 0.621, "i_mpp": 5.84},
        "TEST1": {"v_oc": 0.721, "i_sc": 6.15, "v_mpp": 0.621, "i_mpp": 5.84},
        "TEST2": {"v_oc": 0.731, "i_sc": 6.15, "v_mpp": 0.621, "i_mpp": 5.84},
        "TEST3": {"v_oc": 0.741, "i_sc": 6.15, "v_mpp": 0.621, "i_mpp": 5.84},
    }

    clusters, variance_threshold, head, cluster_steps = generate_clusters(
        cells, heuristics[0], debug=True
    )
    save_clusters(".", clusters)

    print(len(clusters))
    print(clusters)
    print(variance_threshold)

    fig = plt.figure()

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

    ax = fig.add_subplot(121)
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
    ax2 = fig.add_subplot(122, projection="3d")
    centroids = []
    for cluster in clusters.values():
        centroids.append(cluster["centroid"])
        colorings = [
            ax["leaves_color_list"][ax["ivl"].index(cell_name)]
            for cell_name in cluster["cells"]
        ]
        ax2.scatter(*np.transpose(cluster["vectors"]), c=colorings, s=8, alpha=0.7)
    ax2.scatter(*np.transpose(centroids), s=15, c="r", alpha=1)

    plt.show()

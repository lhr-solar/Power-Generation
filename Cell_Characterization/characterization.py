"""_summary_
@file       characterization.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      characterizes and organizes PV data.
@version    0.0.0
@date       2022-10-04
"""

import os
import sys

import matplotlib.pyplot as plt
import numpy as np

pvs = {}


def characterize_pv(file_name, path):
    # Strip PV ID from filename
    pv_id = file_name.split("_")
    pv_id = pv_id[0] + pv_id[1]
    pvs[pv_id] = {
        "points": [],
        "v_oc": 0.00,
        "i_sc": 0.00,
        "p_max": 0.00,
        "v_mpp": 0.00,
        "i_mpp": 0.00,
        "p_mpp": [],
        "ff": 0.00,
        "ff_ranking": 0,
        "sc_ranking": 0,
        "mpp_ranking": 0,
        "overall_ranking": 0,
        "percentile": 0.00,
        "binning": 0,
    }

    # Get lines, convert into floats
    with open(path + file_name, encoding="utf-8") as file:
        start = False
        for line in file:
            entries = line.split(",")
            if len(entries) > 1:
                if entries[0] == "Gate (V)":
                    start = True

                elif start:
                    entries = [float(entry.strip()) for entry in entries]
                    point = [entries[1], entries[2]]
                    pvs[pv_id]["points"].append(point)

    # Sort points.
    pvs[pv_id]["points"] = sorted(pvs[pv_id]["points"])

    # Generate characteristics.
    v_oc = 0
    i_sc = 0
    p_mpp = [0.00, 0.0, 0.0]
    for point in pvs[pv_id]["points"]:
        if v_oc < point[0]:
            v_oc = point[0]
        if i_sc < point[1]:
            i_sc = point[1]
        if point[0] * point[1] > p_mpp[2]:
            p_mpp[2] = point[0] * point[1]
            p_mpp[0] = point[0]
            p_mpp[1] = point[1]

    pvs[pv_id]["v_oc"] = v_oc
    pvs[pv_id]["i_sc"] = i_sc
    pvs[pv_id]["p_max"] = v_oc * i_sc
    pvs[pv_id]["v_mpp"] = p_mpp[0]
    pvs[pv_id]["i_mpp"] = p_mpp[1]
    pvs[pv_id]["p_mpp"] = p_mpp[2]
    try:
        # print(file_name)
        pvs[pv_id]["ff"] = pvs[pv_id]["p_mpp"] / pvs[pv_id]["p_max"]
    except:
        print(f"{file_name} divide by 0 error.")
    pvs[pv_id]["points"] = None
    # print(pvs)


def rank_pvs(pvs, bin_size):
    sorted_pvs = [[pv_id, pv_data] for [pv_id, pv_data] in pvs.items()]

    sorted_pvs = sorted(sorted_pvs, key=lambda pv: pv[1]["ff"])
    for [pv_rank, pv] in enumerate(sorted_pvs):
        # Generate ff_rank
        pv[1]["ff_ranking"] = pv_rank

    sorted_pvs = sorted(sorted_pvs, key=lambda pv: pv[1]["i_sc"])
    for [pv_rank, pv] in enumerate(sorted_pvs):
        # Generate sc_rank
        pv[1]["sc_ranking"] = pv_rank

    sorted_pvs = sorted(sorted_pvs, key=lambda pv: pv[1]["p_mpp"])
    for [pv_rank, pv] in enumerate(sorted_pvs):
        # Generate mpp_rank
        pv[1]["mpp_ranking"] = pv_rank

    # Generate percentiles of FF
    values = np.array([pv_data["ff"] for [pv_id, pv_data] in pvs.items()])
    min_value = values.min()
    max_value = values.max()
    percentiles = (values - min_value) / (max_value - min_value) * 100
    for [percentile, pv] in zip(percentiles, pvs.values()):
        pv["percentile"] = percentile

    # TODO: Generate binning based on bin size
    for [pv_id, pv] in pvs.items():
        pvs[pv_id]["binning"] = 0


def visualize_pvs(pvs):
    def visualize(
        pvs,
        ax,
        metadata=["ff_ranking", "ff", "X axis title", "Y axis title", "Subplot title"],
    ):
        x = []
        y = []
        names = []

        for (pv_id, pv_data) in pvs.items():
            x.append(pv_data[metadata[0]])
            y.append(pv_data[metadata[1]])
            names.append(pv_id)

        sc = ax.scatter(x, y, s=10)
        ax.set_xlabel(metadata[2])
        ax.set_ylabel(metadata[3])
        ax.set_title(metadata[4])
        ax.grid(True)

        # Setup annotation
        annot = ax.annotate(
            "",
            xy=(0, 0),
            xytext=(20, 20),
            textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->"),
        )
        annot.set_visible(False)

        def update_annot(ind):
            pos = sc.get_offsets()[ind["ind"][0]]
            annot.xy = pos
            text = f"{[str(y[n]) for n in ind['ind']]}:{[names[n] for n in ind['ind']]}"
            annot.set_text(text)
            annot.get_bbox_patch().set_alpha(0.4)

        return (sc, update_annot, annot)

    fig, axs = plt.subplots(2, 3)
    (scatter_sc, annot_func_sc, annot_sc) = visualize(
        pvs,
        axs[0][0],
        ["sc_ranking", "i_sc", "Ranking", "I_SC (A)", "PV Ranking by I_SC"],
    )
    (scatter_mpp, annot_func_mpp, annot_mpp) = visualize(
        pvs,
        axs[0][1],
        ["mpp_ranking", "p_mpp", "Ranking", "P_MPP (W)", "PV Ranking by P_MPP"],
    )
    (scatter_mpp2, annot_func_mpp2, annot_mpp2) = visualize(
        pvs,
        axs[0][2],
        ["v_mpp", "i_mpp", "V_MPP (V)", "I_MPP (A)", "PV Scatter of MPP"],
    )
    (scatter_ff, annot_func_ff, annot_ff) = visualize(
        pvs, axs[1][0], ["ff_ranking", "ff", "Ranking", "FF (%)", "PV Ranking by FF"]
    )
    (scatter_percentile, annot_func_percentile, annot_percentile) = visualize(
        pvs,
        axs[1][1],
        [
            "ff_ranking",
            "percentile",
            "Ranking",
            "Percentile (%)",
            "PV Ranking by Percentile",
        ],
    )
    (scatter_bin, annot_func_bin, annot_bin) = visualize(
        pvs, axs[1][2], ["ff", "i_sc", "FF (%)", "I_SC (A)", "Proposed Binning"]
    )

    axes = [axs[0][0], axs[0][1], axs[0][2], axs[1][0], axs[1][1], axs[1][2]]
    scatters = [
        scatter_sc,
        scatter_mpp,
        scatter_mpp2,
        scatter_ff,
        scatter_percentile,
        scatter_bin,
    ]
    annot_funcs = [
        annot_func_sc,
        annot_func_mpp,
        annot_func_mpp2,
        annot_func_ff,
        annot_func_percentile,
        annot_func_bin,
    ]
    annots = [annot_sc, annot_mpp, annot_mpp2, annot_ff, annot_percentile, annot_bin]

    # Hover annotation
    def hover(event):
        for [ax, scatter, annot_func, annot] in zip(
            axes, scatters, annot_funcs, annots
        ):
            if event.inaxes == ax:
                vis = annot.get_visible()
                cont, ind = scatter.contains(event)
                if cont:
                    annot_func(ind)
                    annot.set_visible(True)
                    fig.canvas.draw_idle()
                else:
                    if vis:
                        annot.set_visible(False)
                        fig.canvas.draw_idle()

    fig.canvas.mpl_connect("motion_notify_event", hover)

    # Display plots.
    fig.tight_layout()
    plt.show()


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    # Get PV data directory.
    path = "./cell_data/"
    dir_list = os.listdir(path)
    print("Characterizing PVs...")
    for file_name in dir_list:
        characterize_pv(file_name, path)
    print("Done characterizing PVs.")

    print("Ranking PVs...")
    rank_pvs(pvs, 2)
    print("Done ranking PVs.")

    print("Visualizing PVs...")
    visualize_pvs(pvs)
    print("Done visualizing PVs.")

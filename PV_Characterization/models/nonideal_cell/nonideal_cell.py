"""_summary_
@file       nonideal_cell.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Models a nonideal solar cell.
@version    0.0.0
@date       2022-11-21
"""

import sys

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pretty_traceback
from c.nonideal_model import model_nonideal_cell
from pathos.helpers import cpu_count
from pathos.pools import ProcessPool
from tqdm import trange

PATH = "./cache/nonideal"
FILE_TYPE = "hdf"
PARAMS = {
    "VOLTAGE(V)": [0.00, 1.00, 0.01],
    "IRRAD(W/M^2)": [5.00, 1000.00, 5.00],
    "TEMP(K)": [275.00, 350.00, 5.00],
    "R_S(Ω)": [0.000, 2.500, 0.02],
    "R_SH(Ω)": [1.00, 25.00, 1.00],
}

STC = {
    "IRRAD(W/M^2)": 1000.00,
    "TEMP(K)": 275,
    "R_S(Ω)": 0.00,
    "R_SH(Ω)": 20.00,
}
NUM_CHUNKS = 200


def search_model_nonideal_cell(file_path, params):
    """_summary_
    Pulls a model result from the parameters specified. Parameters
    should be in the format:

    params = {
        "VOLTAGE(V)": 0.10,
        "IRRAD(W/M^2)": 1000.00
        "TEMP(K)": 250.00,
        "R_S(Ω)": 0.01,
        "R_SH(Ω)": 20.00
    }

    Args:
        file_path (str): Path to where cache file should be stored.
        params (dict): Dict of model parameters to retrieve.

    Raises:
        Exception: Invalid file type was specified.

    Returns:
        float: Current.

    Note:
        .hdf only.
        TODO: CSV support
    """
    # Get chunk given parameters.
    chunk = int(params["IRRAD(W/M^2)"] / 5 - 1)
    df = pd.read_hdf(file_path + ".hdf", key=f"idx_{chunk}")
    entries = df[
        (df["IRRAD(W/M^2)"] == params["IRRAD(W/M^2)"])
        & (df["TEMP(K)"] == params["TEMP(K)"])
        & (df["R_S(Ω)"] == params["R_S(Ω)"])
        & (df["R_SH(Ω)"] == params["R_SH(Ω)"])
    ]

    # Find entries closest to voltage
    entries = entries.iloc[
        (entries["VOLTAGE(V)"] - params["VOLTAGE(V)"]).abs().argsort()[:2]
    ]
    if entries.iloc[0]["VOLTAGE(V)"] == params["VOLTAGE(V)"]:
        return entries.iloc[0]["CURRENT(A)"]
    else:
        return (entries.iloc[0]["CURRENT(A)"] + entries.iloc[1]["CURRENT(A)"]) / 2


def model_nonideal_cell_cached_wrapper(combos):
    """_summary_
    Wrapper for generating a group of model outputs given a set of combos.

    Args:
        combos (arrays): A set of combos that need to be modeled.

    Returns:
        list: A list of combo outputs.
    """
    return [model_nonideal_cell(*combo) for combo in combos]


def generate_nonideal_cell_cache(file_path, params, file_type="hdf"):
    """_summary_
    Generates a nonideal model file using the parameters specified. Parameters
    should be in the format:

    params = {
        #             LOW,  HIGH, STEP
        "VOLTAGE(V)": [0.00, 1.00, 0.01],
        "IRRAD(W/M^2)": [5.00, 1000.00, 5.00],
        "TEMP(K)": [275.00, 350.00, 5.00],
        "R_S(Ω)": [0.000, 2.500, 0.02],
        "R_SH(Ω)": [1.00, 25.00, 1.00],
    }

    Args:
        file_path (str): Path to where cache file should be stored.
        params (dict): Dict of model parameters to test.
        file_type (str, optional): Type of file to cache as. Defaults to "hdf".

    Raises:
        Exception: Invalid file type was specified.
    """
    print("Generate combos pandas dataframe.")

    r_sh = np.arange(
        params["R_SH(Ω)"][0],
        params["R_SH(Ω)"][1] + params["R_SH(Ω)"][2],
        params["R_SH(Ω)"][2],
    )
    r_s = np.arange(
        params["R_S(Ω)"][0],
        params["R_S(Ω)"][1] + params["R_S(Ω)"][2],
        params["R_S(Ω)"][2],
    )
    t = np.arange(
        params["TEMP(K)"][0],
        params["TEMP(K)"][1] + params["TEMP(K)"][2],
        params["TEMP(K)"][2],
    )
    g = np.arange(
        params["IRRAD(W/M^2)"][0],
        params["IRRAD(W/M^2)"][1] + params["IRRAD(W/M^2)"][2],
        params["IRRAD(W/M^2)"][2],
    )
    v = np.arange(
        params["VOLTAGE(V)"][0],
        params["VOLTAGE(V)"][1] + params["VOLTAGE(V)"][2],
        params["VOLTAGE(V)"][2],
    )

    print(f"WOMBO COMBOS {len(r_sh) * len(r_s) * len(t) * len(g) * len(v)}")

    pool = ProcessPool(cpu_count())

    # Chunk irradiance into len(g) parts.
    for g_idx in trange(NUM_CHUNKS):
        g_chunk = g[
            int(g_idx * len(g) / NUM_CHUNKS) : int((g_idx + 1) * len(g) / NUM_CHUNKS)
        ]

        combos = np.array(
            [m.flatten() for m in np.meshgrid(g_chunk, t, r_s, r_sh, v, indexing="ij")]
        ).T

        # Split combos into groups.
        combo_groups = np.split(combos, cpu_count())
        results = pool.map(model_nonideal_cell_cached_wrapper, combo_groups)
        currents = []
        for result in results:
            currents.extend(result)

        data = {
            "IRRAD(W/M^2)": combos.T[0],
            "TEMP(K)": combos.T[1],
            "R_S(Ω)": combos.T[2],
            "R_SH(Ω)": combos.T[3],
            "VOLTAGE(V)": combos.T[4],
            "CURRENT(A)": currents,
        }

        # Save to CSV and dump.
        df = pd.DataFrame(data=data)

        if file_type == "csv":
            df.to_csv(
                file_path + ".csv",
                sep=",",
                mode="a",
                header=True,
                index=False,
                chunksize=100000,
                compression="gzip",
                encoding="utf-8",
                float_format="%.3f",
            )
        elif file_type == "hdf":
            df.to_hdf(file_path + ".hdf", key=f"idx_{g_idx}", mode="a")

        else:
            raise Exception("Invalid file type.")


def visualize(file_path, stc, file_type="hdf"):
    """_summary_
    Visualizes an existing model cache using the standard operating conditions
    specified. Conditions should be in the format:

    stc = {
        "IRRAD(W/M^2)": 1000.00,
        "TEMP(K)": 275,
        "R_S(Ω)": 0.00,
        "R_SH(Ω)": 20.00,
    }


    Args:
        file_path (str): Path to where cache file should be stored.
        stc (dict): Dict of model parameters to hold.
        file_type (str, optional): Type of file to cache as. Defaults to "hdf".

    Raises:
        Exception: Invalid file type was specified.
    """
    fig = plt.figure()
    ax1 = fig.add_subplot(221)
    ax2 = fig.add_subplot(222)
    ax3 = fig.add_subplot(223)
    ax4 = fig.add_subplot(224)

    r_s = pd.DataFrame(
        {
            "VOLTAGE(V)": [],
            "IRRAD(W/M^2)": [],
            "TEMP(K)": [],
            "R_S(Ω)": [],
            "R_SH(Ω)": [],
            "CURRENT(A)": [],
        }
    )
    r_sh = pd.DataFrame(
        {
            "VOLTAGE(V)": [],
            "IRRAD(W/M^2)": [],
            "TEMP(K)": [],
            "R_S(Ω)": [],
            "R_SH(Ω)": [],
            "CURRENT(A)": [],
        }
    )
    t = pd.DataFrame(
        {
            "VOLTAGE(V)": [],
            "IRRAD(W/M^2)": [],
            "TEMP(K)": [],
            "R_S(Ω)": [],
            "R_SH(Ω)": [],
            "CURRENT(A)": [],
        }
    )
    g = pd.DataFrame(
        {
            "VOLTAGE(V)": [],
            "IRRAD(W/M^2)": [],
            "TEMP(K)": [],
            "R_S(Ω)": [],
            "R_SH(Ω)": [],
            "CURRENT(A)": [],
        }
    )

    if file_type == "csv":
        CHUNK_SIZE = 500
        while True:
            df = pd.read_csv(file_path + ".csv", chunksize=CHUNK_SIZE)
            chunk_r_sh = df[
                (df["R_S(Ω)"] == stc["R_S(Ω)"])
                & (df["TEMP(K)"] == stc["TEMP(K)"])
                & (df["IRRAD(W/M^2)"] == stc["IRRAD(W/M^2)"])
            ]

            chunk_r_s = df[
                (df["R_SH(Ω)"] == stc["R_SH(Ω)"])
                & (df["TEMP(K)"] == stc["TEMP(K)"])
                & (df["IRRAD(W/M^2)"] == stc["IRRAD(W/M^2)"])
            ]

            chunk_t = df[
                (df["R_SH(Ω)"] == stc["R_SH(Ω)"])
                & (df["R_S(Ω)"] == stc["R_S(Ω)"])
                & (df["IRRAD(W/M^2)"] == stc["IRRAD(W/M^2)"])
            ]

            chunk_g = df[
                (df["R_SH(Ω)"] == stc["R_SH(Ω)"])
                & (df["R_S(Ω)"] == stc["R_S(Ω)"])
                & (df["TEMP(K)"] == stc["TEMP(K)"])
            ]

            r_s = pd.concat([r_s, chunk_r_s])
            r_sh = pd.concat([r_sh, chunk_r_sh])
            t = pd.concat([t, chunk_t])
            g = pd.concat([g, chunk_g])

            if len(df) < CHUNK_SIZE:
                break
    elif file_type == "hdf":
        for chunk in trange(NUM_CHUNKS):
            df = pd.read_hdf(file_path + ".hdf", key=f"idx_{chunk}")
            chunk_r_sh = df[
                (df["R_S(Ω)"] == stc["R_S(Ω)"])
                & (df["TEMP(K)"] == stc["TEMP(K)"])
                & (df["IRRAD(W/M^2)"] == stc["IRRAD(W/M^2)"])
            ]

            chunk_r_s = df[
                (df["R_SH(Ω)"] == stc["R_SH(Ω)"])
                & (df["TEMP(K)"] == stc["TEMP(K)"])
                & (df["IRRAD(W/M^2)"] == stc["IRRAD(W/M^2)"])
            ]

            chunk_t = df[
                (df["R_SH(Ω)"] == stc["R_SH(Ω)"])
                & (df["R_S(Ω)"] == stc["R_S(Ω)"])
                & (df["IRRAD(W/M^2)"] == stc["IRRAD(W/M^2)"])
            ]

            chunk_g = df[
                (df["R_SH(Ω)"] == stc["R_SH(Ω)"])
                & (df["R_S(Ω)"] == stc["R_S(Ω)"])
                & (df["TEMP(K)"] == stc["TEMP(K)"])
            ]

            r_s = pd.concat([r_s, chunk_r_s])
            r_sh = pd.concat([r_sh, chunk_r_sh])
            t = pd.concat([t, chunk_t])
            g = pd.concat([g, chunk_g])
    else:
        raise Exception("Invalid file type.")

    r_s = r_s.sort_values(by=["R_S(Ω)"])
    r_sh = r_sh.sort_values(by=["R_SH(Ω)"])
    t = t.sort_values(by=["TEMP(K)"])
    g = g.sort_values(by=["IRRAD(W/M^2)"])

    for ax, series, level, series_description in zip(
        [ax1, ax2, ax3, ax4],
        [g, t, r_s, r_sh],
        ["IRRAD(W/M^2)", "TEMP(K)", "R_S(Ω)", "R_SH(Ω)"],
        ["Irradiance", "Temperature", "Series Resistance", "Shunt Resistance"],
    ):
        ax.scatter(
            series["VOLTAGE(V)"].values,
            series["CURRENT(A)"].values,
            c=series[level].values,
            cmap=mpl.colormaps["plasma"],
            s=1,
            alpha=1.0,
        )
        ax.set_xlabel("V (V)")
        ax.set_ylabel("I (A)")
        ax.set_title(f"I-V Curve w/ Diff. {series_description}")

    plt.tight_layout()
    fig.savefig("nonideal_model.png")
    plt.show()


"""
Generates a nonideal model cache for faster execution.
"""
if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    try:
        import pretty_traceback

        pretty_traceback.install()
    except ImportError:
        pass  # no need to fail because of missing dev dependency

    # NOTE: Do not uncomment this line unless you're sure you want to overwrite
    # the old HDF file.
    # generate_nonideal_cell_cache(PATH, PARAMS, FILE_TYPE)

    visualize(PATH, STC, FILE_TYPE)

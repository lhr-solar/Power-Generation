"""_summary_
@file       search.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Given a folder path and some search parameter, return all applicable
            results. 
@version    0.0.0
@date       2022-12-11
"""

import argparse
import json
import os
import sys


def search(path, search_param, search_value, search_condition):
    # Load .char files from path
    dir_list = os.listdir(path)
    cells = {}
    for file_name in sorted(dir_list):
        if os.path.splitext(file_name)[1] == ".char":
            file_name = os.path.splitext(file_name)[0]
            with open(f"{path}{file_name}.char") as f:
                cells[file_name] = json.load(f)

    # Load from each file the relevant search_param

    match search_param:
        case "v_oc":
            cells = {
                file_name: cell_data["v_oc"] for file_name, cell_data in cells.items()
            }
        case "i_sc":
            cells = {
                file_name: cell_data["i_sc"] for file_name, cell_data in cells.items()
            }
        case "v_mpp":
            cells = {
                file_name: cell_data["v_mpp"] for file_name, cell_data in cells.items()
            }
        case "i_mpp":
            cells = {
                file_name: cell_data["i_mpp"] for file_name, cell_data in cells.items()
            }
        case "ff":
            cells = {
                file_name: (cell_data["v_mpp"] * cell_data["i_mpp"])
                / (cell_data["v_oc"] * cell_data["i_sc"])
                for file_name, cell_data in cells.items()
            }
        case "irrad":
            cells = {
                file_name: cell_data["p_opt"][0]
                for file_name, cell_data in cells.items()
            }
        case "temp":
            cells = {
                file_name: cell_data["p_opt"][1]
                for file_name, cell_data in cells.items()
            }
        case "r_s":
            cells = {
                file_name: cell_data["p_opt"][2]
                for file_name, cell_data in cells.items()
            }
        case "r_sh":
            cells = {
                file_name: cell_data["p_opt"][3]
                for file_name, cell_data in cells.items()
            }
        case "fit_err":
            cells = {
                file_name: cell_data["fit_err"]
                for file_name, cell_data in cells.items()
            }
        case _:
            raise Exception("Invalid search parameter.")

    match search_condition:
        # Case for range
        case "==":
            cells = {
                file_name: cell_data
                for file_name, cell_data in cells.items()
                if cell_data == search_value
            }
        case "<":
            cells = {
                file_name: cell_data
                for file_name, cell_data in cells.items()
                if cell_data < search_value
            }
        case ">":
            cells = {
                file_name: cell_data
                for file_name, cell_data in cells.items()
                if cell_data > search_value
            }
        case "<=":
            cells = {
                file_name: cell_data
                for file_name, cell_data in cells.items()
                if cell_data <= search_value
            }
        case ">=":
            cells = {
                file_name: cell_data
                for file_name, cell_data in cells.items()
                if cell_data >= search_value
            }
        case _:
            raise Exception("Invalid search condition.")

    return cells


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    try:
        import pretty_traceback

        pretty_traceback.install()
    except ImportError:
        pass  # no need to fail because of missing dev dependency

    path = "./cell_data/RP/"
    results = search(path, "ff", 0.525, "<")
    print(results)

"""_summary_
@file       convert.py
@author     Matthew Yu (matthewjkyu@gmail.com)
@brief      Converts one format of file to another.
@version    0.0.0
@date       2022-10-26
"""

import os
import sys

file_type_to_convert = ".lvm"
file_type_to_convert_to = "LOG_V1"


def convert(file_name, file, new_file_type):
    # Get file type from file, convert it into format specified by file_type.
    # Generate the header for the data to be collected from the file.
    extension = ""
    data = []
    match new_file_type:
        case "LOG_V0":
            pass
        case "LOG_V1":
            data = [["Gate (V)", "Voltage (V)", "Current (A)", "Power (W)"]]
            extension = ".log"
        case _:
            pass

    # Get the internal header for the file.
    head = [next(file).strip() for x in range(3)]

    # Get the file type of the file.
    curr_file_type = None
    match head:
        case ["LabVIEW Measurement", "Writer_Version\t2", "Reader_Version\t2"]:
            curr_file_type = ("LOG_V0", ".lvm")
        case ["SCAN MODE", "", ""]:
            curr_file_type = ("LOG_V1", ".log")
        case _:
            pass

    # Based on the file type, read in the data and fill in data.
    match curr_file_type[0]:
        case "LOG_V0":
            # Move to the 23rd line.
            _ = [next(file) for x in range(19)]
            while True:
                row = next(file, None)
                if row is None:
                    break
                row = row.split()
                row = [float(entry) for entry in row]
                data.append(row)
        case "LOG_V1":
            pass
        case _:
            pass

    # Given the data, save to new file.
    with open(f"{file_name}{extension}", "w", encoding="utf-8") as new_file:
        match new_file_type:
            case "LOG_V0":
                pass
            case "LOG_V1":
                new_file.writelines(["SCAN MODE\n", "\n", "\n"])
                new_file.write(f"{data[0][0]},{data[0][1]},{data[0][2]},{data[0][3]}\n")
                for row in data[1:-1]:
                    [current, voltage, gate] = row
                    current *= 200
                    power = voltage * current
                    new_file.write(f"{gate},{voltage},{current},{power}\n")
            case _:
                pass

    print(f"Generated  {file_name}{extension}.")


if __name__ == "__main__":
    if sys.version_info[0] < 3:
        raise Exception("This program only supports Python 3.")

    # Get PV data directory.
    path = "./cell_data/control/"
    dir_list = os.listdir(path)
    print(
        f"Converting PVs of file type {file_type_to_convert} in path {path} to type {file_type_to_convert_to}"
    )

    file_paths = sorted(
        [
            file_path
            for file_path in dir_list
            if os.path.splitext(file_path)[1] == file_type_to_convert
        ]
    )
    for file_path in file_paths:
        with open(f"{path}{file_path}", mode="r", encoding="utf-8") as file:
            print(f"Converting {path}{file_path}...")
            convert(
                f"{path}{os.path.splitext(file_path)[0]}", file, file_type_to_convert_to
            )

#!/usr/bin/env python3

from collections import defaultdict
import os
import time
import sys
from typing import Any


TEMP_DIR_PATH: str = os.path.join("/tmp", "disk-stat-diff")


def print_fixed_width_table(table: dict[str, list[Any]]) -> None:
    """
    Please note that this function was entirely generated by ChatGPT.
    """
    # Get the list of keys and values from the dictionary
    keys = list(table.keys())
    values = list(table.values())

    # Transpose the values list to get rows instead of columns
    values = list(zip(*values))

    # Calculate the maximum width of each column
    widths = []
    for i in range(len(keys)):
        widths.append(max(len(str(x[i])) for x in values + [keys]))

    # Print the header
    print(" ".join("{:{}}".format(x, w) for x, w in zip(keys, widths)))

    # Print each row
    for row in values:
        print(" ".join("{:{}}".format(x, w) for x, w in zip(row, widths)))


def get_major_minor_numbers(device_path: str) -> tuple[int, int]:
    device_number: int = os.stat(device_path).st_rdev
    return os.major(device_number), os.minor(device_number)


def get_stat_filepath(device_path: str) -> str:
    major_number: int
    minor_number: int
    major_number, minor_number = get_major_minor_numbers(device_path)

    return os.path.join("/sys/dev/block", f"{major_number}:{minor_number}", "stat")


def parse_stats_from_file(filepath: str) -> dict[str, int]:
    with open(filepath) as infile:
        file_contents: str = infile.read()
        stats: list[str] = file_contents.split()

        stats_dict: dict[str, int] = {}

        stats_dict["read_ios"] = int(stats[0])
        stats_dict["read_merges"] = int(stats[1])
        stats_dict["read_sectors"] = int(stats[2])
        stats_dict["read_ticks"] = int(stats[3])
        stats_dict["write_ios"] = int(stats[4])
        stats_dict["write_merges"] = int(stats[5])
        stats_dict["write_sectors"] = int(stats[6])
        stats_dict["write_ticks"] = int(stats[7])
        stats_dict["in_flight"] = int(stats[8])
        stats_dict["io_ticks"] = int(stats[9])
        stats_dict["time_in_queue"] = int(stats[10])
        stats_dict["discard_ios"] = int(stats[11])
        stats_dict["discard_merges"] = int(stats[12])
        stats_dict["discard_sectors"] = int(stats[13])
        stats_dict["discard_ticks"] = int(stats[14])
        stats_dict["flush_ios"] = int(stats[15])
        stats_dict["flush_ticks"] = int(stats[16])

        # Per the
        # [documentation](https://www.kernel.org/doc/html/latest/block/stat.html#read-sectors-write-sectors-discard-sectors),
        # read_sectors etc is given in 512 byte blocks, so we can use this to
        # make the _sectors fields use bytes.
        stats_dict["read_bytes"] = stats_dict["read_sectors"] * 512
        stats_dict["write_bytes"] = stats_dict["write_sectors"] * 512
        stats_dict["discard_bytes"] = stats_dict["discard_sectors"] * 512

    return stats_dict


def store_stats(stat_filepath: str, device_name: str) -> None:
    with open(stat_filepath) as infile:
        with open(get_temp_store_filepath(device_name), "w+") as outfile:
            infile_contents: str = infile.read()
            outfile.write(infile_contents)


def get_temp_store_filepath(device_name: str) -> str:
    return os.path.join(TEMP_DIR_PATH, device_name)


def parse_stats_and_print_diff(device_name: str) -> None:
    temp_stat_store_path: str = get_temp_store_filepath(device_name)

    modified_time: float = os.path.getmtime(temp_stat_store_path)
    current_time: float = time.time()
    seconds_passed: float = current_time - modified_time

    old_stats: dict[str, int] = parse_stats_from_file(temp_stat_store_path)
    device_path: str = os.path.join("/dev", device_name)
    store_stats(get_stat_filepath(device_path), device_name)
    new_stats: dict[str, int] = parse_stats_from_file(temp_stat_store_path)

    print(f"Difference over the past {round(seconds_passed, 2)} second(s).")

    # Calculate stats like `diff` and store them in a dict so that
    # they can be parsed by `print_fixed_width_table`.
    table: dict[str, list[Any]] = defaultdict(list)
    key: str
    value: int
    for key, value in new_stats.items():
        diff: int = value - old_stats[key]

        table["stat"].append(key)
        table["diff"].append(diff)

    print_fixed_width_table(table)


def store_stats_first_time(device_name: str) -> None:
    if not os.path.exists(TEMP_DIR_PATH):
        os.makedirs(TEMP_DIR_PATH)

    device_path: str = os.path.join("/dev", device_name)
    store_stats(get_stat_filepath(device_path), get_temp_store_filepath(device_name))
    print("Storing stats for the first time.")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Provide a device name. e.g. `python3 disk-stat-diff.py sda1`")
        exit(1)
    device_name: str = sys.argv[1]

    if os.path.exists(get_temp_store_filepath(device_name)):
        parse_stats_and_print_diff(device_name)
    else:
        store_stats_first_time(device_name)

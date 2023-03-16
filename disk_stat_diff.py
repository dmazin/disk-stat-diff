from collections import defaultdict
import numbers
import os
import time
import sys
from typing import Any


TEMP_DIR_PATH: str = os.path.join("/tmp", "disk-stat-diff")


def print_fixed_width_table(table: dict[str, list[Any]]) -> None:
    max_col_width: dict[str, int] = {}

    column_name: str
    values: list[Any]
    for column_name, values in table.items():
        len_list: list[int] = [len(str(v)) for v in values]
        len_list.append(len(column_name))
        max_col_width[column_name] = max(len_list)

    header: str = ""
    for header_col in table.keys():
        header += f"{header_col: <{max_col_width[header_col]}}\t"

    

    print(header)


    # values_list: tuple[list[Any]]
    # for values_list in zip(table.values()):
    #     for line 

    # print(f"{'key' :{max_key_len}}\t{'diff' :{max_diff_len}}\t{'avg (per sec)' :{max_avg_len}}")
    # for key, value in new_stats.items():
    #     diff: int = value - old_stats[key]
    #     avg: float = round(diff / seconds_passed, 2)
    #     print(f"{key :{max_key_len}}\t{diff :{max_diff_len}}\t{avg :{max_avg_len}}")

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

    rotated_table: dict[str, list[Any]] = defaultdict(list)

    key: str
    value: int
    for key, value in new_stats.items():
        diff: int = value - old_stats[key]
        avg: float = round(diff / seconds_passed, 2)

        rotated_table['stat'].append(key)
        rotated_table['diff'].append(diff)
        rotated_table['avg'].append(avg)
        # print(f"{key :{max_key_len}}\t{diff :{max_diff_len}}\t{avg :{max_avg_len}}")

    print_fixed_width_table(rotated_table)


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

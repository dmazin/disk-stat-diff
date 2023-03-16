# disk_stat_diff
This is a small Python script that can be invoked multiple times. Each time you
invoke it, it tells you how much various disk statistics for a given partition
have changed since the last invocation.

It depends on the `/sys/dev/block/<major>:<minor>/stat` file provided by Linux.

Example usage: 
```
$ python3 disk_stat_diff.py sda5

Storing stats for the first time.

$ dd if=/dev/zero of=/data/foo bs=4096 count=1

1+0 records in
1+0 records out
4096 bytes (4.1 kB, 4.0 KiB) copied, 0.000172019 s, 23.8 MB/s

$ python3 disk_stat_diff.py sda5

Difference over the past 0.02 second(s).
------------------------------------
| stat            | diff | avg       |
------------------------------------
| read_ios        |    0 |       0.0 |
| read_merges     |    0 |       0.0 |
| read_sectors    |    0 |       0.0 |
| read_ticks      |    0 |       0.0 |
| write_ios       |    1 |     40.79 |
| write_merges    |    0 |       0.0 |
| write_sectors   |    8 |    326.32 |
| write_ticks     |    0 |       0.0 |
| in_flight       |    0 |       0.0 |
| io_ticks        |    4 |    163.16 |
| time_in_queue   |    0 |       0.0 |
| discard_ios     |    0 |       0.0 |
| discard_merges  |    0 |       0.0 |
| discard_sectors |    0 |       0.0 |
| discard_ticks   |    0 |       0.0 |
| flush_ios       |    0 |       0.0 |
| flush_ticks     |    0 |       0.0 |
| read_bytes      |    0 |       0.0 |
| write_bytes     | 4096 | 167073.84 |
| discard_bytes   |    0 |       0.0 |
------------------------------------
```

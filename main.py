from multiprocessing import pool
import subprocess
import re
from pprint import pprint


output = """  pool: tank
 state: DEGRADED
status: One or more devices are faulted in response to persistent errors.
        Sufficient replicas exist for the pool to continue functioning in a
        degraded state.
action: Replace the faulted device, or use 'zpool clear' to mark the device
        repaired.
  scan: resilvered 35.6G in 00:08:47 with 0 errors on Sat Sep 10 01:20:26 2022
config:

        NAME        STATE     READ WRITE CKSUM
        tank        DEGRADED     0     0     0
          raidz2-0  DEGRADED     0     0     0
            sda     ONLINE       0     0     0
            sdc     FAULTED     33     0     0  too many errors
            sdb     ONLINE       0     0     0
            sdd     ONLINE       0     0     0
            sdf     ONLINE       0     0     0

errors: No known data errors
"""


def parse_data(data):
    parts = re.split(r"(?:\n|^)\s*(\w*):\s*", data.strip(), re.MULTILINE)[1:]
    parsed = dict(zip(parts[::2], parts[1::2]))
    return parsed
    # return {**parsed, "config": parse_config(parsed.get("config", ""))}


def parse_config(data):
    lines = [v.strip().split() for v in data.splitlines() if v.strip()]
    if lines:
        return [dict(zip(lines[0], v)) for v in lines[1:]]
    return []


def main():
    zpool: dict = parse_data(output)
    pool: str = zpool["pool"]
    status: str = zpool["status"].replace("\n", " ").replace("  ", "")
    # status = [i for i in range(100) if i % 2 == 0]

    match zpool["state"]:
        case "DEGRADED":
            print(f"Pool `{pool}` is DEGRADED")
        case "FAULTED":
            print(f"Pool `{pool}` has FAULTED")


if __name__ == "__main__":
    main()


# pprint.pprint(d)

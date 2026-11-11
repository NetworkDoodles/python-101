"""Collect `show ip interface brief` from every device in the lab and print a summary.

When a device can't be reached or refuses the login, print one clear line and exit 1: no traceback.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))   # so `import netlab` works

from netlab.devices import Device, DeviceError, collect  # noqa: E402

DEVICES = [
    Device("r1", "172.80.111.11", "cisco_ios"),
    Device("r2", "172.80.111.12", "cisco_ios"),
    Device("sw1", "172.80.111.21", "cisco_ios"),
    Device("r3", "172.80.111.13", "arista_eos"),
]

try:
    tables = collect(DEVICES)
except DeviceError as e:
    print(f"error: {e}", file=sys.stderr)
    sys.exit(1)
for name, rows in tables.items():
    up = sum(1 for r in rows if r["status"] == "up")
    print(f"{name:<4} {len(rows)} IP interfaces, {up} up")

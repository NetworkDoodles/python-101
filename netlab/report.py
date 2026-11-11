"""Chapter 8 · the capstone: every device in the inventory, its facts, one CSV.

scripts/inventory.py runs these, one step at a time:
    devices = load_devices(source)          the inventory, from YAML or the API
    facts(device) for each device           log in, run show version, shape one row
    write_csv(rows, path)                   the rows, as inventory.csv
"""
import csv
import os
import pathlib

from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException, ReadException
from paramiko.ssh_exception import SSHException

from netlab.devices import DeviceError, connect
from netlab.env import load_env
from netlab.inventory import api_to_inventory, get_devices, load_inventory

ROOT = pathlib.Path(__file__).resolve().parents[1]
# What Netmiko raises when a device drops a session it had already opened.
DROPPED = (ReadException, SSHException, OSError, EOFError)
COLUMNS = ["hostname", "model", "version", "serial", "uptime", "ip_interfaces"]


# TODO 8.1a
def load_devices(source="yaml"):
    """The inventory as a list of dicts: from inventory.yml when source is "yaml", or from the lab's API
    when it's "api" (its address and token are LAB_API_URL and LAB_API_TOKEN in the environment)."""
    raise NotImplementedError("TODO 8.1a is still open")


# TODO 8.1b
def facts(device):
    """Log in to one device and return its row for the CSV: a dict with the keys in COLUMNS.

    hostname       the name in the device's prompt (Netmiko keeps it in conn.base_prompt)
    model          from the inventory: show version doesn't report one on these devices
    version        show version, parsed: "version" on cisco_ios, "image" on arista_eos
    serial         show version, parsed: "serial" (a list: take the first) on cisco_ios, "serial_number" on arista_eos
    uptime         show version, parsed: "uptime" on both
    ip_interfaces  how many interfaces in show ip interface brief have an IP address

    Failures to log in or connect come out of connect() as Netmiko's exceptions; turn them into
    DeviceError, as collect() did in chapter 6. So does a device that drops the session halfway through
    a command: Netmiko raises one of DROPPED (a read that timed out, an SSH error, a closed socket).
    """
    raise NotImplementedError("TODO 8.1b is still open")


# TODO 8.1c
def write_csv(rows, path):
    """Write the rows to a CSV file with csv.DictWriter: a header row of COLUMNS, then one row per device."""
    raise NotImplementedError("TODO 8.1c is still open")


# TODO 8.2
def run(devices):
    """facts() for every device, carrying on when one fails.

    Returns (rows, failures): the rows of every device that answered, in inventory order, and a dict
    of device name -> the DeviceError's message for every one that didn't.
    """
    # TODO 8.2: this one stops at the first device that fails. Make it carry on.
    rows = []
    for d in devices:
        rows.append(facts(d))
    return rows, {}

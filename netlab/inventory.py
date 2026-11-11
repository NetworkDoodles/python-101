"""Chapter 7 · YAML, JSON and a first REST call: the same inventory from a file and from an API.

Either way you end up with a list of dicts, one per device, with the same five keys:
    {"name": "r3", "host": "172.80.111.13", "device_type": "arista_eos", "role": "router", "model": "CapeOS-Pulse"}
"""
import json

import requests
import yaml


class ApiError(Exception):
    """The API said no, or didn't answer. The message says why, in one line."""


# TODO 7.1a
def load_inventory(path):
    """The devices in an inventory YAML file (the list under its top-level "devices" key).

    Use yaml.safe_load, never yaml.load.
    """
    raise NotImplementedError("TODO 7.1a is still open")


# TODO 7.1b
def save_json(devices, path):
    """Write the list of devices to a JSON file, indented by 2 spaces so a person can read it."""
    raise NotImplementedError("TODO 7.1b is still open")


# TODO 7.1c
def load_json(path):
    """Read the JSON file save_json wrote, back into a list of dicts."""
    raise NotImplementedError("TODO 7.1c is still open")


# TODO 7.2a
def get_devices(base_url, token):
    """GET <base_url>/api/devices/ with the token, and return the JSON's "results" list as it is.

    The API wants the token in a header, the way NetBox does:  Authorization: Token <token>
    Time out after 5 seconds. When the API answers with an error status (403 for a wrong token), or
    doesn't answer at all, raise ApiError with a one-line message that includes the status code or
    the reason. The lab's API explains its errors in JSON ({"detail": "Invalid token"}), but an error
    can also come from something in front of an API, as an HTML page: the message still needs the status.
    """
    raise NotImplementedError("TODO 7.2a is still open")


# TODO 7.2b
def api_to_inventory(results):
    """The API's devices, reshaped into the same five keys as the YAML inventory.

    In the API, the address is primary_ip.address with its prefix ("172.80.111.11/24" -> "172.80.111.11"),
    the device_type is platform.slug, the role is role.slug and the model is device_type.model.
    """
    raise NotImplementedError("TODO 7.2b is still open")

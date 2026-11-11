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
    # >>> solution
    with open(path) as f:
        return yaml.safe_load(f)["devices"]
    # <<< solution


# TODO 7.1b
def save_json(devices, path):
    """Write the list of devices to a JSON file, indented by 2 spaces so a person can read it."""
    # >>> solution
    with open(path, "w") as f:
        json.dump(devices, f, indent=2)
        f.write("\n")
    # <<< solution


# TODO 7.1c
def load_json(path):
    """Read the JSON file save_json wrote, back into a list of dicts."""
    # >>> solution
    with open(path) as f:
        return json.load(f)
    # <<< solution


# TODO 7.2a
def get_devices(base_url, token):
    """GET <base_url>/api/devices/ with the token, and return the JSON's "results" list as it is.

    The API wants the token in a header, the way NetBox does:  Authorization: Token <token>
    Time out after 5 seconds. When the API answers with an error status (403 for a wrong token), or
    doesn't answer at all, raise ApiError with a one-line message that includes the status code or
    the reason. The lab's API explains its errors in JSON ({"detail": "Invalid token"}), but an error
    can also come from something in front of an API, as an HTML page: the message still needs the status.
    """
    # >>> solution
    try:
        r = requests.get(f"{base_url}/api/devices/", headers={"Authorization": f"Token {token}"}, timeout=5)
        r.raise_for_status()
    except requests.HTTPError:
        try:
            detail = r.json().get("detail", r.reason)
        except ValueError:          # an error page that isn't JSON, from a proxy or a web server
            detail = r.reason
        raise ApiError(f"the API answered {r.status_code}: {detail}") from None
    except requests.RequestException as e:
        raise ApiError(f"no answer from the API at {base_url}: {type(e).__name__}") from None
    return r.json()["results"]
    # <<< solution


# TODO 7.2b
def api_to_inventory(results):
    """The API's devices, reshaped into the same five keys as the YAML inventory.

    In the API, the address is primary_ip.address with its prefix ("172.80.111.11/24" -> "172.80.111.11"),
    the device_type is platform.slug, the role is role.slug and the model is device_type.model.
    """
    # >>> solution
    devices = []
    for d in results:
        devices.append({
            "name": d["name"],
            "host": d["primary_ip"]["address"].split("/")[0],
            "device_type": d["platform"]["slug"],
            "role": d["role"]["slug"],
            "model": d["device_type"]["model"],
        })
    return devices
    # <<< solution

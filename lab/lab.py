"""Helpers the checker, the status page and `make solve` share: ask the lab's devices directly.

These go round your code on purpose (docker exec, not SSH), so the checker always has its own view of
what the devices say right now.
"""
import json
import os
import pathlib
import subprocess
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEVICES = {                     # name: (management address, device_type)
    "r1": ("172.80.111.11", "cisco_ios"),
    "r2": ("172.80.111.12", "cisco_ios"),
    "r3": ("172.80.111.13", "arista_eos"),
    "sw1": ("172.80.111.21", "cisco_ios"),
}
HOSTS = ["host1", "host2"]
API = "api"
NODES = [*DEVICES, API, *HOSTS]


def env():
    """The lab's settings from .env (or .env.example, before `make setup` has copied it)."""
    values = {}
    for name in (".env.example", ".env"):
        p = ROOT / name
        if p.exists():
            for line in p.read_text().splitlines():
                if "=" in line and not line.lstrip().startswith("#"):
                    k, _, v = line.partition("=")
                    values[k.strip()] = v.strip().strip("'\"")
    return values


def run(args, timeout=30, **kw):
    try:
        p = subprocess.run(args, capture_output=True, text=True, timeout=timeout, **kw)
        return p.returncode, (p.stdout + p.stderr).strip()
    except subprocess.TimeoutExpired:
        return 124, "timed out"
    except OSError as e:
        return 127, str(e)


def sh(node, cmd, timeout=20):
    """Run a shell command inside a node's container; return (exit code, output)."""
    return run(["docker", "exec", node, "sh", "-c", cmd], timeout=timeout)


def show(node, cmd, timeout=20):
    """Run a CLI command on a router or the switch; return its output ('' if it can't)."""
    try:
        p = subprocess.run(["docker", "exec", "-i", node, "capeos-cli", "-c", cmd], capture_output=True,
                           text=True, timeout=timeout)
        return p.stdout.rstrip() if p.returncode == 0 else ""
    except (subprocess.TimeoutExpired, OSError):
        return ""


def config(node, *lines):
    """Type configuration commands on a device, as you would: configure terminal ... end."""
    text = "\n".join(["configure terminal", *lines, "end", ""])
    p = subprocess.run(["docker", "exec", "-i", node, "capeos-cli"], input=text, capture_output=True, text=True,
                       timeout=30)
    return p.stdout


def running(node):
    return run(["docker", "inspect", "-f", "{{.State.Running}}", node])[1] == "true"


def ready(node):
    if not running(node):
        return False
    if node in DEVICES:
        return sh(node, "test -e /run/capeos/ready")[0] == 0
    if node == API:
        return api_get("/api/")[0] == 200
    return True


def api_get(path, token=None):
    """GET a path on the lab's API; return (status, parsed JSON or None)."""
    token = token or env().get("LAB_API_TOKEN", "")
    url = env().get("LAB_API_URL", "http://api:8000") + path
    req = urllib.request.Request(url, headers={"Authorization": f"Token {token}"})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, None
    except (OSError, ValueError):
        return 0, None


def brief(node):
    """`show ip interface brief` as [{interface, ip_address, status, protocol}], read straight from the device."""
    rows = []
    for line in show(node, "show ip interface brief").splitlines():
        w = line.split()
        if not w or w[0] in ("Interface", "Address") or set(w[0]) <= {"-"}:
            continue
        if DEVICES[node][1] == "arista_eos":
            # Interface  IP Address  Status  Protocol  MTU  Owner
            rows.append({"interface": w[0], "ip_address": w[1], "status": w[2], "protocol": w[3]})
        else:
            rows.append({"interface": w[0], "ip_address": None if w[1] == "unassigned" else w[1],
                         "status": " ".join(w[4:-1]), "protocol": w[-1]})
    return rows


def version_facts(node):
    """hostname, version, serial and uptime, read straight from `show version`."""
    out = show(node, "show version")
    facts = {"hostname": node}
    for line in out.splitlines():
        s = line.strip()
        if DEVICES[node][1] == "arista_eos":
            if s.startswith("Serial number:"):
                facts["serial"] = s.split(":", 1)[1].strip()
            elif s.startswith("Software image version:"):
                facts["version"] = s.split(":", 1)[1].strip()
            elif s.startswith("Uptime:"):
                facts["uptime"] = s.split(":", 1)[1].strip()
        else:
            if s.startswith("CapeOS Software"):
                facts["version"] = s.split("Version", 1)[1].split(",")[0].strip()
            elif s.startswith("Processor board ID"):
                facts["serial"] = s.split()[-1]
            elif " uptime is " in s:
                facts["uptime"] = s.split(" uptime is ", 1)[1].strip()
    return facts

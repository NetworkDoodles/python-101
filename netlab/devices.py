"""Chapter 6 · talking to devices with Netmiko.

The login comes from the environment (LAB_USER and LAB_PASSWORD, which netlab.env.load_env() reads from
.env), never from the code. Every device has a device_type, the name Netmiko and ntc-templates know its
CLI by: "cisco_ios" for CapeOS Bolt (r1, r2, sw1), "arista_eos" for CapeOS Pulse (r3).
"""
import os
from dataclasses import dataclass

from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoAuthenticationException, NetmikoTimeoutException

from netlab.env import load_env


class DeviceError(Exception):
    """A device we couldn't log in to, or couldn't reach. The message says which and why, in one line."""


# TODO 6.1a
def connect(host, device_type="cisco_ios"):
    """Log in to one device over SSH and return Netmiko's connection object.

    Read the username and password from the environment variables LAB_USER and LAB_PASSWORD (call
    load_env() first, so .env is read). Give up after 5 seconds if the device doesn't answer
    (conn_timeout=5).
    """
    # >>> solution
    load_env()
    return ConnectHandler(
        device_type=device_type,
        host=host,
        username=os.environ["LAB_USER"],
        password=os.environ["LAB_PASSWORD"],
        conn_timeout=5,
    )
    # <<< solution


# TODO 6.1b
def interface_table(conn):
    """`show ip interface brief` on a connected device, parsed by ntc-templates: a list of dicts."""
    # >>> solution
    return conn.send_command("show ip interface brief", use_textfsm=True)
    # <<< solution


# TODO 6.2a
# A device in the inventory: its name, the address to log in to, and its device_type.
#   Device(name="r3", host="172.80.111.13", device_type="arista_eos")
# >>> solution | Device = None
@dataclass
class Device:
    name: str
    host: str
    device_type: str = "cisco_ios"
# <<< solution


# TODO 6.2b
def collect(devices, command="show ip interface brief"):
    """Run one command on every device and return {device name: parsed output}.

    Parse with ntc-templates (use_textfsm=True). Disconnect from each device when you're done with it.
    When a login fails or a device doesn't answer, raise DeviceError with a one-line message that names
    the device, like "r2: login failed (check LAB_USER and LAB_PASSWORD)", instead of Netmiko's
    exception and its traceback.
    """
    # >>> solution
    results = {}
    for d in devices:
        try:
            conn = connect(d.host, d.device_type)
        except NetmikoAuthenticationException:
            raise DeviceError(f"{d.name}: login failed (check LAB_USER and LAB_PASSWORD)") from None
        except NetmikoTimeoutException:
            raise DeviceError(f"{d.name}: no answer from {d.host} on port 22") from None
        try:
            results[d.name] = conn.send_command(command, use_textfsm=True)
        finally:
            conn.disconnect()
    return results
    # <<< solution

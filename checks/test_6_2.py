"""Task 6.2 · the Device dataclass and collect() in netlab/devices.py, over every device, and the error path."""
import pytest
from conftest import ROOT, call, no_todo, script

LAB = [("r1", "172.80.111.11", "cisco_ios"), ("r2", "172.80.111.12", "cisco_ios"),
       ("sw1", "172.80.111.21", "cisco_ios"), ("r3", "172.80.111.13", "arista_eos")]


def devices():
    from netlab.devices import Device
    if Device is None or not callable(Device):
        pytest.fail("TODO 6.2a is still open: Device is still None in netlab/devices.py", pytrace=False)
    return Device


def r2_refuses(lab):
    """Is task 6.2's problem (make break T=6.2) in place?"""
    from netmiko import ConnectHandler
    from netmiko.exceptions import NetmikoAuthenticationException
    env = lab.env()
    try:
        ConnectHandler(device_type="cisco_ios", host="172.80.111.12", username=env["LAB_USER"],
                       password=env["LAB_PASSWORD"], conn_timeout=5).disconnect()
        return False
    except NetmikoAuthenticationException:
        return True


def test_device_dataclass():
    Device = devices()
    d = Device("r3", "172.80.111.13", "arista_eos")
    assert (d.name, d.host, d.device_type) == ("r3", "172.80.111.13", "arista_eos"), \
        "Device(name, host, device_type), in that order"
    assert d == Device("r3", "172.80.111.13", "arista_eos"), "two Devices with the same fields should be equal (a dataclass does that)"


def test_collect_every_device(lab_up):
    from netlab.devices import collect
    Device = devices()
    broken = r2_refuses(lab_up)
    lab = [Device(*d) for d in LAB if not (broken and d[0] == "r2")]
    got = call(collect, lab)
    assert sorted(got) == sorted(d.name for d in lab), f"collect() should return one entry per device, got {sorted(got)}"
    for d in lab:
        live = {r["interface"] for r in lab_up.brief(d.name)}
        mine = {r.get("interface") for r in got[d.name]} if isinstance(got[d.name], list) else set()
        assert mine == live, f"{d.name}: the device has {sorted(live)}, collect() got {sorted(mine)}"


def test_wrong_password(lab_up, monkeypatch):
    from netlab.devices import DeviceError, collect
    Device = devices()
    if not r2_refuses(lab_up):
        monkeypatch.setenv("LAB_PASSWORD", "not-the-password")    # the same problem, without make break
    with pytest.raises(DeviceError) as e:
        call(collect, [Device("r2", "172.80.111.12", "cisco_ios")])
    assert "r2" in str(e.value), f"the message should name the device: {e.value}"


def test_no_answer(lab_up):
    from netlab.devices import DeviceError, collect
    Device = devices()
    with pytest.raises(DeviceError) as e:
        call(collect, [Device("r9", "172.80.111.19", "cisco_ios")])
    assert "r9" in str(e.value), f"the message should name the device: {e.value}"


def test_the_script_says_it_clearly(lab_up):
    devices()
    p = script(ROOT / "scripts" / "collect.py", env={"LAB_PASSWORD": "not-the-password"})
    no_todo(p)
    assert "Traceback" not in p.stderr, f"with a wrong password the script should print one line, not a traceback:\n{p.stderr[-1500:]}"
    assert p.returncode == 1, f"with a wrong password the script should exit 1, it exited {p.returncode}"
    assert "r1" in p.stderr, f"the message should name the first device that refused, r1: {p.stderr}"

"""Task 6.1 · connect() and interface_table() in netlab/devices.py, and scripts/r1_interfaces.py, against r1."""
import pytest
from conftest import ROOT, call, no_todo, script


def test_no_password_in_the_code():
    for f in [ROOT / "netlab" / "devices.py", *sorted((ROOT / "scripts").glob("*.py"))]:
        assert "capeos-lab" not in f.read_text(), f"the lab's password is written in {f.relative_to(ROOT)}: read it from the environment"


def test_the_script(lab_up):
    p = script(ROOT / "scripts" / "r1_interfaces.py")
    no_todo(p)
    assert p.returncode == 0, f"scripts/r1_interfaces.py stopped with an error:\n{p.stderr[-1500:]}"
    printed = {}
    for line in p.stdout.splitlines():
        w = line.split()
        if len(w) >= 3 and "/" in w[-1] and not line.startswith("logged in"):
            printed[w[0]] = (w[1], " ".join(w[2:]))
    live = {r["interface"]: (r["ip_address"] or "unassigned", r["status"]) for r in lab_up.brief("r1")}
    assert sorted(printed) == sorted(live), f"r1 has the interfaces {sorted(live)}; the script printed {sorted(printed)}"
    for name, (address, _) in live.items():
        assert printed[name][0] == address, f"{name}: r1 says {address}, the script printed {printed[name][0]}"


def test_credentials_come_from_the_environment(lab_up, monkeypatch):
    from netmiko.exceptions import NetmikoAuthenticationException
    from netlab.devices import connect
    monkeypatch.setenv("LAB_PASSWORD", "not-the-password")
    with pytest.raises(NetmikoAuthenticationException):
        conn = call(connect, "r1", "cisco_ios")
        conn.disconnect()
    # With a wrong LAB_PASSWORD the login has to fail: so connect() really reads it from the environment.


def test_interface_table(lab_up):
    from netlab.devices import connect, interface_table
    conn = call(connect, "r1", "cisco_ios")
    try:
        rows = call(interface_table, conn)
    finally:
        conn.disconnect()
    assert isinstance(rows, list) and rows and isinstance(rows[0], dict), \
        f"interface_table should return a list of dicts (use_textfsm=True), not {type(rows).__name__}"
    assert {r["interface"] for r in rows} == {r["interface"] for r in lab_up.brief("r1")}

"""Task 8.2 · run() in netlab/report.py: carry on past devices that fail, list them, and exit 2."""
import csv
import textwrap

from conftest import PY, ROOT, call, no_todo

import subprocess

# The script, with a device that doesn't exist added to whatever the inventory says (make break T=8.2
# also stops r2, and adds r9 to inventory.yml).
RUN = textwrap.dedent(f"""
    import runpy, sys
    sys.path.insert(0, {str(ROOT)!r})
    import netlab.report as report
    real = report.load_devices
    def load_devices(source="yaml"):
        devices = real(source)
        if not any(d["name"] == "ghost" for d in devices):
            devices.append(dict(name="ghost", host="172.80.111.29", device_type="cisco_ios", role="router", model="CapeOS-Bolt"))
        return devices
    report.load_devices = load_devices
    sys.argv = ["inventory.py"]
    runpy.run_path({str(ROOT / "scripts" / "inventory.py")!r}, run_name="__main__")
""")


def test_run_carries_on(lab_up):
    from netlab.report import run
    devices = [dict(name="ghost", host="172.80.111.29", device_type="cisco_ios", role="router", model="CapeOS-Bolt"),
               dict(name="r1", host="172.80.111.11", device_type="cisco_ios", role="router", model="CapeOS-Bolt")]
    rows, failures = call(run, devices)
    assert [r["hostname"] for r in rows] == ["r1"], f"run() should return r1's row and carry on past ghost: {rows}"
    assert list(failures) == ["ghost"], f"failures should be {{'ghost': <the reason>}}, got {failures}"
    assert "ghost" in failures["ghost"], f"the reason should name the device: {failures['ghost']}"


def test_the_script(lab_up, tmp_path):
    p = subprocess.run([PY, "-c", RUN], cwd=tmp_path, capture_output=True, text=True, timeout=240)
    no_todo(p)
    assert "Traceback" not in p.stderr, f"the script crashed instead of carrying on:\n{p.stderr[-2000:]}"
    assert p.returncode == 2, f"with devices that failed the script should exit 2, it exited {p.returncode}"
    expected_down = {"ghost"} | ({"r9"} if "name: r9" in (ROOT / "inventory.yml").read_text() else set()) \
        | (set() if lab_up.running("r2") else {"r2"})
    for name in expected_down:
        assert name in p.stderr, f"the script should list {name} as a failure on stderr. It printed:\n{p.stderr}"
    with (tmp_path / "inventory.csv").open() as f:
        written = {r["hostname"] for r in csv.DictReader(f)}
    reached = {"r1", "r2", "r3", "sw1"} - expected_down
    assert written == reached, f"the CSV should have every device that answered ({sorted(reached)}), it has {sorted(written)}"

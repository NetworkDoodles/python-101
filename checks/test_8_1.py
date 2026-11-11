"""Task 8.1 · netlab/report.py and scripts/inventory.py: one CSV row per device, checked against the devices."""
import csv

import pytest
from conftest import ROOT, no_todo, script

COLUMNS = ["hostname", "model", "version", "serial", "uptime", "ip_interfaces"]
MODELS = {"r1": "CapeOS-Bolt", "r2": "CapeOS-Bolt", "r3": "CapeOS-Pulse", "sw1": "CapeOS-Bolt"}


def run_inventory(lab, tmp_path, *args):
    if not lab.running("r2"):
        pytest.fail("r2 is stopped (make break T=8.2 does that). make reset starts it again; then check 8.1.",
                    pytrace=False)
    p = script(ROOT / "scripts" / "inventory.py", *args, cwd=tmp_path if not args else ROOT)
    no_todo(p)
    return p


def check_csv(lab, path):
    assert path.exists(), f"the script didn't write {path.name}"
    with path.open() as f:
        reader = csv.DictReader(f)
        assert reader.fieldnames == COLUMNS, f"the header row should be {','.join(COLUMNS)}, not {','.join(reader.fieldnames or [])}"
        rows = {r["hostname"]: r for r in reader}
    assert sorted(rows) == sorted(MODELS), f"expected a row for each of {sorted(MODELS)}, got {sorted(rows)}"
    for name, row in rows.items():
        live = lab.version_facts(name)
        for col in ("version", "serial"):
            assert row[col] == live[col], f"{name}: show version says {col} {live[col]}, the CSV says {row[col]}"
        assert row["model"] == MODELS[name], f"{name}: the inventory says model {MODELS[name]}, the CSV says {row['model']}"
        assert row["uptime"], f"{name}: the uptime is empty"
        count = sum(1 for r in lab.brief(name) if r["ip_address"])
        assert row["ip_interfaces"] == str(count), f"{name} has {count} interfaces with an IP address, the CSV says {row['ip_interfaces']}"


def test_inventory_csv(lab_up, tmp_path):
    p = run_inventory(lab_up, tmp_path)
    assert p.returncode == 0, f"scripts/inventory.py stopped with an error:\n{p.stderr[-2000:]}"
    check_csv(lab_up, tmp_path / "inventory.csv")

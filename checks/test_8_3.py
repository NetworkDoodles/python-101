"""Task 8.3 · --source and --out on scripts/inventory.py: both sources give the same CSV."""
import csv

import pytest
from conftest import ROOT, no_todo, script


def rows(path):
    with path.open() as f:
        return [{k: v for k, v in r.items() if k != "uptime"} for r in csv.DictReader(f)]


def test_help():
    p = script(ROOT / "scripts" / "inventory.py", "--help")
    no_todo(p)
    assert p.returncode == 0 and "--source" in p.stdout and "--out" in p.stdout, \
        f"--help should list --source and --out (argparse writes it for you):\n{p.stdout}{p.stderr}"


def test_bad_source():
    p = script(ROOT / "scripts" / "inventory.py", "--source", "xml")
    assert p.returncode == 2 and "invalid choice" in p.stderr, \
        "--source xml should be refused by argparse (choices=[...]), with exit code 2"


def test_both_sources(lab_up, tmp_path):
    if not lab_up.running("r2"):
        pytest.fail("r2 is stopped (make break T=8.2 does that). make reset starts it again; then check 8.3.", pytrace=False)
    a, b = tmp_path / "from-yaml.csv", tmp_path / "from-api.csv"
    for source, out in (("yaml", a), ("api", b)):
        p = script(ROOT / "scripts" / "inventory.py", "--source", source, "--out", out)
        no_todo(p)
        assert p.returncode == 0, f"--source {source} stopped with an error:\n{p.stderr[-2000:]}"
        assert out.exists(), f"--out {out.name} didn't write {out.name}"
    assert rows(a) == rows(b), "the two CSVs differ (uptime aside): the API and the YAML should give the same devices"
    assert len(rows(a)) >= 4

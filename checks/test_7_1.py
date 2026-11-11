"""Task 7.1 · inventory.yml, and load_inventory(), save_json() and load_json() in netlab/inventory.py."""
import json

import gen
import yaml
from conftest import ROOT, call

from netlab.inventory import load_inventory, load_json, save_json


def test_the_surprises_are_quoted():
    doc = yaml.safe_load((ROOT / "inventory.yml").read_text())
    assert doc["country"] == "NO", f"country loads as {doc['country']!r}: Norway's code should stay the string 'NO'"
    assert doc["rack"] == "0123", f"rack loads as {doc['rack']!r}: the label is the string '0123'"
    assert "on" in doc["backup"], f"backup's keys load as {list(doc['backup'])}: the key 'on' should stay a string"
    assert doc["backup"]["at"] == "2:30", f"backup at loads as {doc['backup']['at']!r}: the time should stay '2:30'"


def test_lab_inventory():
    devices = call(load_inventory, ROOT / "inventory.yml")
    assert [d["name"] for d in devices][:4] == ["r1", "r2", "r3", "sw1"], "load_inventory returns the list under devices:"


def test_safe_load_only():
    src = (ROOT / "netlab" / "inventory.py").read_text()
    assert "yaml.load(" not in src, "use yaml.safe_load: yaml.load can build any Python object a file asks for"


def test_unseen_round_trip(tmp_path):
    for i in range(10):
        devices, _ = gen.inventory()
        y = tmp_path / f"inv{i}.yml"
        y.write_text(yaml.safe_dump({"site": "x", "devices": devices}, sort_keys=False))
        got = call(load_inventory, y)
        assert got == devices, f"load_inventory on\n{y.read_text()}\ngave {got}"
        j = tmp_path / f"inv{i}.json"
        call(save_json, got, j)
        assert json.loads(j.read_text()) == devices, "save_json should write the devices as JSON"
        assert "\n  " in j.read_text(), "indent the JSON (indent=2), so a person can read it"
        assert call(load_json, j) == devices, "load_json should give back exactly what save_json wrote"

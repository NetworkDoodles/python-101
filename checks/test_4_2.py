"""Task 4.2 · load_configs_safe() in netlab/configs.py: bad files are reported, and the rest carries on."""
import csv
import os

import gen
import pytest
from conftest import ROOT, call, no_todo, script

from netlab.configs import load_configs_safe


def bad_folder(tmp_path):
    folder = tmp_path / "configs"
    folder.mkdir()
    good = {}
    for i in range(4):
        name = gen.device_name(i)
        ntp = i % 2 == 0
        (folder / f"{name}.cfg").write_text(gen.config(name, ntp))
        good[name] = "yes" if ntp else "no"
    bad = []
    latin = f"{gen.device_name(7)}.cfg"
    (folder / latin).write_bytes("hostname x\nbanner motd ^C Caf\xe9 ^C\n".encode("latin-1"))
    bad.append(latin)
    if os.geteuid() != 0:                    # root can read anything, so this one only works as a normal user
        locked = folder / f"{gen.device_name(8)}.cfg"
        locked.write_text("hostname y\n")
        locked.chmod(0)
        bad.append(locked.name)
    return folder, good, bad


def test_function(tmp_path):
    folder, good, bad = bad_folder(tmp_path)
    configs, problems = call(load_configs_safe, folder)
    assert sorted(configs) == sorted(good), f"the readable configs are {sorted(good)}, got {sorted(configs)}"
    assert sorted(problems) == sorted(bad), f"problems should name the bad files {sorted(bad)}, got {sorted(problems)}"
    for name, reason in problems.items():
        assert isinstance(reason, str) and reason, f"give a short reason for {name}"


def test_only_what_you_can_handle(tmp_path):
    folder = tmp_path / "configs"
    (folder / "not-a-file.cfg").mkdir(parents=True)
    with pytest.raises(IsADirectoryError):
        call(load_configs_safe, folder)
    # (a folder called *.cfg is a mistake in the code's world, not a bad file: it should still stop you)


def test_the_script(tmp_path):
    folder, good, bad = bad_folder(tmp_path)
    out = tmp_path / "ntp.csv"
    p = script(ROOT / "scripts" / "ntp_report.py", folder, out)
    no_todo(p)
    assert "Traceback" not in p.stderr, f"the script crashed on a bad file:\n{p.stderr}"
    assert p.returncode == 1, f"with bad files the script should exit 1, it exited {p.returncode}"
    for name in bad:
        assert name in p.stderr, f"the script should name {name} on stderr. It printed:\n{p.stderr}"
    with out.open() as f:
        got = {r["device"]: r["has_ntp"] for r in csv.DictReader(f)}
    assert got == good, f"the CSV should still have every good config: expected {good}, got {got}"

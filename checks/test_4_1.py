"""Task 4.1 · netlab/configs.py and scripts/ntp_report.py, on a folder of configs they haven't seen."""
import csv

import gen
from conftest import ROOT, call, no_todo, script

from netlab.configs import has_ntp, load_configs


def make_folder(tmp_path, n=6):
    folder = tmp_path / "configs"
    folder.mkdir()
    want = {}
    for i in range(n):
        name = gen.device_name(i)
        ntp = gen.R.random() < 0.5
        (folder / f"{name}.cfg").write_text(gen.config(name, ntp))
        want[name] = "yes" if ntp else "no"
    (folder / "README.txt").write_text("not a config\nntp server 10.9.9.9\n")
    return folder, want


def test_has_ntp():
    assert call(has_ntp, "hostname r1\nntp server 10.0.0.1\n") is True
    assert call(has_ntp, "hostname r2\nntp master 3\n") is False
    assert call(has_ntp, "hostname r3\n! ntp server 10.0.0.1\n") is False, "a comment (!) isn't an ntp server line"
    assert call(has_ntp, "") is False


def test_load_configs(tmp_path):
    folder, want = make_folder(tmp_path)
    got = call(load_configs, folder)
    assert sorted(got) == sorted(want), f"expected the devices {sorted(want)} (only the .cfg files), got {sorted(got)}"
    for name in want:
        assert got[name] == (folder / f"{name}.cfg").read_text(), f"{name}'s text isn't the whole file"


def test_the_script(tmp_path):
    folder, want = make_folder(tmp_path)
    out = tmp_path / "out" / "ntp.csv"
    p = script(ROOT / "scripts" / "ntp_report.py", folder, out)
    no_todo(p)
    assert p.returncode == 0, f"scripts/ntp_report.py stopped with an error:\n{p.stderr}"
    assert out.exists(), f"the script didn't write {out}"
    with out.open() as f:
        rows = list(csv.reader(f))
    assert rows[0] == ["device", "has_ntp"], f"the header row should be device,has_ntp, not {','.join(rows[0])}"
    got = {r[0]: r[1] for r in rows[1:]}
    assert got == want, f"expected {want}\ngot      {got}"
    assert [r[0] for r in rows[1:]] == sorted(want), "the rows should be sorted by device name"


def test_the_lab_folder():
    p = script(ROOT / "scripts" / "ntp_report.py")
    no_todo(p)
    assert (ROOT / "reports" / "ntp.csv").exists(), "python scripts/ntp_report.py should write reports/ntp.csv"

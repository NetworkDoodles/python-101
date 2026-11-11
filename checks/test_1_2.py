"""Task 1.2 · a venv of your own: scratch/.venv, scratch/requirements.txt, and a package only it has."""
import os
import re
import shutil
import subprocess

import pytest
from conftest import ROOT

SCRATCH = ROOT / "scratch"


def outside_python():
    venv_bin = os.path.dirname(os.path.realpath(os.sys.executable))
    path = os.pathsep.join(p for p in os.environ["PATH"].split(os.pathsep)
                           if p and os.path.realpath(p) != venv_bin and "/.venv" not in p and "/.venvs/" not in p)
    return shutil.which("python3", path=path)


def pins():
    req = SCRATCH / "requirements.txt"
    assert req.exists(), "there's no scratch/requirements.txt yet"
    lines = [l.split("#")[0].strip() for l in req.read_text().splitlines()]
    return [l for l in lines if l]


def test_venv():
    cfg = SCRATCH / ".venv" / "pyvenv.cfg"
    assert cfg.exists(), "there's no venv in scratch/.venv: python3 -m venv scratch/.venv"
    assert (SCRATCH / ".venv" / "bin" / "python").exists()


def test_requirements_pinned():
    lines = pins()
    assert lines, "scratch/requirements.txt is empty"
    loose = [l for l in lines if not re.fullmatch(r"[A-Za-z0-9_.\-\[\]]+==[\w.\-+]+", l)]
    assert not loose, f"these aren't pinned to one version (name==version): {', '.join(loose)}"


def test_only_in_the_venv():
    py = SCRATCH / ".venv" / "bin" / "python"
    outside = outside_python()
    for line in pins():
        name = line.split("==")[0]
        inside = subprocess.run([str(py), "-m", "pip", "show", name], capture_output=True, text=True)
        assert inside.returncode == 0, f"{name} is in requirements.txt but not installed in scratch/.venv"
        version = re.search(r"^Version: (.*)$", inside.stdout, re.M).group(1)
        assert line.endswith("==" + version), f"{line}: scratch/.venv has {name} {version}"
        if outside:
            out = subprocess.run([outside, "-m", "pip", "show", name], capture_output=True, text=True)
            assert out.returncode != 0, (f"{name} is installed outside the venv too ({outside}). "
                                         f"Remove it there: {outside} -m pip uninstall {name}")

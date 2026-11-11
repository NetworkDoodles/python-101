"""Task 1.1 · Running Python: answers/1.1.yml, and scripts/hello.py."""
import pathlib
import subprocess
import sys

import pytest
from conftest import PY, ROOT, script

VENV_BIN = pathlib.Path(sys.executable).parent


def answers():
    doc = {}
    for line in (ROOT / "answers" / "1.1.yml").read_text().splitlines():
        line = line.split(" #")[0].strip()
        if line and not line.startswith("#") and ":" in line:
            k, _, v = line.partition(":")
            doc[k.strip()] = v.strip().strip("'\"")
    return doc


def test_version():
    real = subprocess.run([PY, "--version"], capture_output=True, text=True).stdout.split()[-1]
    given = answers().get("version", "").removeprefix("Python").strip()
    assert given, "version: is empty in answers/1.1.yml. Run python --version"
    assert given == real, f"version: the lab's Python is {real[:2]}..., and you wrote {given}"


def test_venv_python():
    given = answers().get("venv_python", "")
    assert given, "venv_python: is empty. Run which python in a new terminal"
    assert pathlib.Path(given).parent == VENV_BIN, \
        f"venv_python: {given} isn't in the lab's venv. Is (lab) at the start of your prompt? Open a new terminal"


def test_repl_answer():
    assert answers().get("repl_answer") == str(len("GigabitEthernet1")), \
        'repl_answer: type len("GigabitEthernet1") in the REPL and copy what it prints'


def test_system_python():
    given = answers().get("system_python", "")
    assert given, "system_python: is empty. Run deactivate, then which python"
    assert pathlib.Path(given).parent != VENV_BIN, "system_python: that's still the venv's Python. Run deactivate first"
    p = pathlib.Path(given)
    assert p.exists(), f"system_python: there's no {given}"
    out = subprocess.run([given, "-c", "import sys; print(sys.prefix == sys.base_prefix)"], capture_output=True, text=True)
    assert out.stdout.strip() == "True", f"system_python: {given} runs inside a venv; it should be the one outside"


def test_hello():
    hello = ROOT / "scripts" / "hello.py"
    assert hello.exists(), "there's no scripts/hello.py yet"
    p = script(hello)
    assert p.returncode == 0, f"scripts/hello.py stopped with an error:\n{p.stderr}"
    assert p.stdout.strip() == "Hello, network!", f'scripts/hello.py printed {p.stdout.strip()!r}, not "Hello, network!"'

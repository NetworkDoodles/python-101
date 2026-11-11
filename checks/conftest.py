"""Shared by every check: where the repo is, how to call your code, and how to talk to the lab."""
import os
import pathlib
import subprocess
import sys

import pytest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab"))
sys.path.insert(0, str(ROOT / "checks"))
DATA = ROOT / "checks" / "data"
PY = sys.executable                     # the lab's venv, the one `make check` runs


def call(func, *args, **kwargs):
    """Run one of your functions. A TODO that's still open fails with a short message, not a traceback."""
    try:
        return func(*args, **kwargs)
    except NotImplementedError as e:
        todo = str(e)
    where = f"{func.__module__.replace('.', '/')}.py" if hasattr(func, "__module__") else "your code"
    pytest.fail(f"{todo}: write {func.__name__}() in {where}, then check again", pytrace=False)


def script(*args, env=None, cwd=ROOT, timeout=180):
    """Run one of your scripts with the lab's Python, the way you would in a terminal."""
    full_env = {**os.environ, **(env or {})}
    full_env.pop("PYTHONPATH", None)
    return subprocess.run([PY, *map(str, args)], cwd=cwd, capture_output=True, text=True, timeout=timeout,
                          env=full_env)


def no_todo(p):
    """Fail with a clear message when a script stopped on a TODO."""
    out = p.stdout + p.stderr
    if "NotImplementedError" in out:
        line = [l for l in out.splitlines() if l.startswith("NotImplementedError")][-1:] or [""]
        pytest.fail(f"the script stopped on a TODO: {line[0].split(':', 1)[-1].strip()}", pytrace=False)


@pytest.fixture(scope="session")
def lab_up():
    """The checks that talk to devices need the lab running."""
    import lab
    down = [n for n in [*lab.DEVICES, lab.API] if not lab.ready(n)]
    if "make break T=8.2" in (ROOT / "inventory.yml").read_text() and "r2" in down:
        down.remove("r2")                   # task 8.2 stops r2 on purpose
    if down:
        pytest.fail(f"the lab isn't up ({', '.join(down)} not ready). Run make up, or make reset, and check again.",
                    pytrace=False)
    return lab

"""Read the lab's .env file into the environment, so code can use os.environ["LAB_PASSWORD"].

A .env file holds one setting per line, KEY=value, and stays out of Git (.gitignore lists it). This does
what the python-dotenv package does, in a few lines: a variable already set in your shell wins.
"""
import os
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]


def load_env(path=ROOT / ".env"):
    path = pathlib.Path(path)
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        os.environ.setdefault(key.strip(), value.strip().strip("'\""))


def need(name):
    """The value of an environment variable, or a clear message saying how to set it."""
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"{name} isn't set: it belongs in .env (make setup copies .env.example there)")
    return value

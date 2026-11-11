"""make status · what's running, and where to start.

The dev container runs this when the folder opens. It only reads. Safe to run any time.
"""
import os
import shutil
import sys
import time
import pathlib

sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
import lab  # noqa: E402

GUIDE = "https://networkdoodles.com/labs/python-101"
TTY = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
G, R, Y, D, B, X = (("\033[32m", "\033[31m", "\033[33m", "\033[2m", "\033[1m", "\033[0m") if TTY else ("",) * 6)
WHAT = {
    "r1": "router 1   CapeOS Bolt   cisco_ios    172.80.111.11",
    "r2": "router 2   CapeOS Bolt   cisco_ios    172.80.111.12",
    "r3": "router 3   CapeOS Pulse  arista_eos   172.80.111.13",
    "sw1": "switch     CapeOS Bolt   cisco_ios    172.80.111.21",
    "api": "the inventory API                      http://api:8000/api/",
    "host1": "a host behind sw1", "host2": "a host behind r2",
}


def row(ok, name, value):
    mark = f"{G}✓{X}" if ok else f"{R}✗{X}"
    print(f"  {mark} {name:<6} {value}")


def main():
    wait = "--wait" in sys.argv
    print(f"\n{B}Python 101 for network engineers{X}   {D}{GUIDE}{X}\n")
    if not shutil.which("docker"):
        row(False, "docker", "not found: open the lab in its dev container (Codespaces does this for you)")
        return 1
    deadline = time.time() + (300 if wait else 0)
    while True:
        up = {n: lab.ready(n) for n in lab.NODES}
        if all(up.values()) or time.time() >= deadline:
            break
        print(f"  {D}starting: {', '.join(n for n, ok in up.items() if not ok)} ...{X}", flush=True)
        time.sleep(5)
    for n, ok in up.items():
        row(ok, n, WHAT[n] if ok else f"{WHAT[n]}: not running (make up starts it)")
    env = ".env" if (lab.ROOT / ".env").exists() else f"{R}missing{X}: make setup writes it"
    print(f"\n  {D}python{X}  {sys.executable}   {D}settings{X}  {env}")
    if all(up.values()):
        print(f"\n  {G}Ready.{X} Start with task 1.1: {GUIDE}/task-1-1/\n")
        return 0
    print(f"\n  Not everything is up. {B}make up{X} starts the lab (about a minute).\n")
    return 1


sys.exit(main())

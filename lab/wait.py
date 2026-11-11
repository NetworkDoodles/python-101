"""Wait until the routers, the switch and the API answer, and SSH is open on every device."""
import pathlib
import socket
import sys
import time

sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
import lab  # noqa: E402


def ssh_open(addr):
    try:
        with socket.create_connection((addr, 22), timeout=2) as s:
            return s.recv(64).startswith(b"SSH-")
    except OSError:
        return False


deadline = time.time() + 240
while True:
    pending = [n for n in lab.NODES if not lab.ready(n)]
    pending += [f"SSH on {n}" for n, (addr, _) in lab.DEVICES.items() if n not in pending and not ssh_open(addr)]
    if not pending:
        break
    if time.time() > deadline:
        sys.exit(f"these didn't come up in 4 minutes: {', '.join(pending)}   (docker logs <name> says why)")
    print(f"  waiting for {', '.join(pending)} ...", flush=True)
    time.sleep(4)
print("\n  the lab is up: r1, r2, r3, sw1 and the API. Start with task 1.1: https://networkdoodles.com/labs/python-101/task-1-1/\n")

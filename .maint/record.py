#!/usr/bin/env python3
"""Maintainers only: record real show outputs and configs from the running lab, for the checks and the
lab's configs/ folder. Run from the repo root with the lab up (make up), then make reset afterwards:
it changes a few interfaces on the way.

    python .maint/record.py
"""
import pathlib
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lab"))
import lab  # noqa: E402

DATA = ROOT / "checks" / "data"
DATA.mkdir(parents=True, exist_ok=True)


def save(name, text):
    (DATA / name).write_text(text.rstrip("\n") + "\n")
    print("recorded", name)


# Saved configs for chapter 4: what `show running-config` says on each device.
for node in lab.DEVICES:
    (ROOT / "configs" / f"{node}.cfg").write_text(lab.show(node, "show running-config") + "\n")
    print("saved configs/%s.cfg" % node)

lines = [lab.show(n, "show version").splitlines()[0] for n in ("r1", "sw1")]
save("version-lines.txt", "\n".join(dict.fromkeys(lines)))

for node in ("r1", "r2", "sw1"):
    save(f"brief-{node}.txt", lab.show(node, "show ip interface brief"))
save("brief-r3-pulse.txt", lab.show("r3", "show ip interface brief"))

# A few more states: a port shut, a subinterface, a port that's up with the protocol down.
lab.config("r2", "interface GigabitEthernet3", " shutdown", "interface GigabitEthernet4", " no shutdown",
           "interface GigabitEthernet2.100", " encapsulation dot1Q 100", " ip address 192.168.100.1 255.255.255.0")
lab.config("r1", "interface Loopback9", " ip address 10.255.9.1 255.255.255.255", "interface GigabitEthernet1",
           " ip address dhcp")
time.sleep(3)
save("brief-r2-changed.txt", lab.show("r2", "show ip interface brief"))
save("brief-r1-changed.txt", lab.show("r1", "show ip interface brief"))

for node in ("r1", "r2", "sw1"):
    save(f"ntp-{node}.txt", lab.show(node, "show ntp associations"))
save("version-r1.txt", lab.show("r1", "show version"))
save("version-r3-pulse.txt", lab.show("r3", "show version"))
print("\nnow: make reset")

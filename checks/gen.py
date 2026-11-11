"""Inputs your code hasn't seen: show outputs, configs and inventories made up fresh on every check, in
the same layout the lab's devices use. Each generator returns the text and the answer it should give."""
import random

R = random.Random()


def ip():
    return f"{R.choice([10, 172, 192])}.{R.randint(0, 255)}.{R.randint(0, 255)}.{R.randint(1, 254)}"


def interface_names(n):
    names = ["GigabitEthernet0"] + [f"GigabitEthernet{i}" for i in range(1, R.randint(2, 9))]
    names += [f"GigabitEthernet{R.randint(1, 4)}.{R.choice([10, 20, 100, 210])}" for _ in range(R.randint(0, 2))]
    names += [f"Loopback{i}" for i in range(R.randint(0, 2))] + [f"Vlan{v}" for v in R.sample([1, 10, 20, 99], R.randint(0, 2))]
    return list(dict.fromkeys(names))[:n]


def brief(n=None, blank_lines=False):
    """`show ip interface brief` as CapeOS Bolt prints it, and the dicts chapter 2 asks for."""
    rows = []
    for name in interface_names(n or R.randint(3, 12)):
        state = R.choices(["up", "down", "admin"], weights=[6, 2, 2])[0]
        status, proto = {"up": ("up", R.choice(["up", "up", "up", "down"])), "down": ("down", "down"),
                         "admin": ("administratively down", "down")}[state]
        address = None if R.random() < 0.3 else ip()
        method = "unset" if address is None else ("DHCP" if name == "GigabitEthernet0" else R.choice(["manual", "manual", "NVRAM"]))
        rows.append({"interface": name, "ip_address": address, "ok": "YES", "method": method,
                     "status": status, "protocol": proto})
    lines = ["Interface              IP-Address      OK? Method Status                Protocol"]
    for r in rows:
        lines.append(f"{r['interface']:<23}{r['ip_address'] or 'unassigned':<16}{r['ok']:<4}{r['method']:<7}"
                     f"{r['status']:<22}{r['protocol']}")
        if blank_lines and R.random() < 0.25:
            lines.append("")
    return "\n".join(lines) + "\n", rows


def version_line():
    software = R.choice(["CapeOS Software", "Lab Network OS Software", "Example Router Software", "NetOS"])
    image = R.choice(["CO-BOLT", "CO-BOLT-LAB", "X86_64_LINUX", "EX-K9", "LAB9"])
    version = f"{R.randint(0, 20)}.{R.randint(0, 12)}.{R.randint(0, 9)}{R.choice(['', '', 'a', 'b'])}"
    tail = R.choice([", LAB USE ONLY", ", RELEASE SOFTWARE (fc2)", "", ", EARLY DEPLOYMENT, (test)"])
    return f"{software} ({image}), Version {version}{tail}", {"software": software, "image": image, "version": version}


def ntp_associations(n=None):
    """`show ntp associations` as CapeOS Bolt prints it, and the four fields 5.2 checks."""
    lines = ["  address         ref clock       st   when   poll reach  delay  offset   disp"]
    rows = []
    for i in range(n if n is not None else R.randint(1, 5)):
        synced = R.random() < 0.6
        mark = (R.choice(["*", "+", "-", "x"]) if synced else " ") + "~"
        address = ip()
        ref = R.choice([".LOCL.", ".GPS.", ip()]) if synced else ".INIT."
        st = str(R.randint(1, 15)) if synced else "16"
        when = str(R.randint(0, 900)) if synced else "-"
        poll = R.choice([64, 128, 256, 1024])
        reach = str(R.choice([377, 17, 1, 3, 177])) if synced else "0"
        delay, offset, disp = (R.uniform(0, 50), R.uniform(-5, 5), R.uniform(0, 3)) if synced else (0, 0, 0)
        lines.append(f"{mark}{address:<15} {ref:<15} {st:>2} {when:>6} {poll:>6} {reach:>5} "
                     f"{delay:>6.3f} {offset:>7.3f} {disp:>6.3f}")
        rows.append({"address": address, "ref_clock": ref, "stratum": st, "reach": reach})
    lines.append(" * sys.peer, # selected, + candidate, - outlyer, x falseticker, ~ configured")
    return "\n".join(lines) + "\n", rows


def config(name, ntp):
    lines = [f"hostname {name}", "!", f"interface GigabitEthernet{R.randint(1, 4)}",
             f" description to {R.choice(['core', 'wan', 'lab'])}", f" ip address {ip()} 255.255.255.0", "!"]
    if ntp:
        lines += [f"ntp server {ip()}" for _ in range(R.randint(1, 2))]
    else:
        lines += R.choice([[], ["! ntp server 10.0.0.1 (removed)"], [f"ntp master {R.randint(1, 8)}"],
                           [" ntp server inside an indented block"]])
    return "\n".join(lines + ["!", "end", ""])


def device_name(i):
    return R.choice(["edge", "core", "lab", "dc", "br"]) + f"{i}-{R.choice(['r', 'sw', 'fw'])}{R.randint(1, 99)}"


def inventory(n=None):
    """A list of devices in the five-key shape, plus the same devices as the API would return them."""
    devices, api = [], []
    for i in range(n or R.randint(2, 7)):
        dt = R.choice(["cisco_ios", "arista_eos"])
        role = R.choice(["router", "switch", "firewall"])
        model = R.choice(["CapeOS-Bolt", "CapeOS-Pulse", "Lab-1000"])
        host = ip()
        name = device_name(i)
        devices.append({"name": name, "host": host, "device_type": dt, "role": role, "model": model})
        api.append({"id": i + 1, "url": f"http://api:8000/api/devices/{i + 1}/", "name": name,
                    "device_type": {"model": model, "manufacturer": {"name": "Network Doodles", "slug": "network-doodles"}},
                    "role": {"name": role.capitalize(), "slug": role},
                    "platform": {"name": dt, "slug": dt}, "serial": "", "site": {"name": "LAB", "slug": "lab"},
                    "status": {"value": "active", "label": "Active"},
                    "primary_ip": {"address": f"{host}/{R.choice([24, 26, 32])}", "family": {"value": 4, "label": "IPv4"}}})
    return devices, api

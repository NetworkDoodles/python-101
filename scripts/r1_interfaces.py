"""Log in to r1 and print its interfaces, one per line:  GigabitEthernet1  192.168.10.1  up/up"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))   # so `import netlab` works

from netlab.devices import connect, interface_table  # noqa: E402

conn = connect("r1", "cisco_ios")
print(f"logged in to {conn.find_prompt()}")
for i in interface_table(conn):
    print(f"{i['interface']:<20} {i['ip_address']:<16} {i['status']}/{i['proto']}")
conn.disconnect()

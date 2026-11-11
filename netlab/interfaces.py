"""Chapter 3 · loops, conditionals and functions: questions about a list of interfaces.

The interfaces are dicts like the ones netlab.parse.interfaces_to_dicts() makes:
    {"interface": "GigabitEthernet4", "ip_address": None, "status": "administratively down", "protocol": "down"}
"""


# TODO 3.1a
def down_interfaces(interfaces):
    """The names of the interfaces that aren't working, in the order they came.

    An interface works when both its status and its protocol are "up". Anything else ("down",
    "administratively down", a status up with the protocol down) means it isn't.

    >>> down_interfaces([{"interface": "Gi1", "status": "up", "protocol": "up"},
    ...                  {"interface": "Gi4", "status": "administratively down", "protocol": "down"}])
    ['Gi4']
    """
    # >>> solution
    down = []
    for i in interfaces:
        if i["status"] != "up" or i["protocol"] != "up":
            down.append(i["interface"])
    return down
    # <<< solution


# TODO 3.1b
def count_by_status(interfaces):
    """How many interfaces have each status, as a dict: {"up": 5, "administratively down": 1}.

    Only statuses that occur are keys. No interfaces give {}.
    """
    # >>> solution
    counts = {}
    for i in interfaces:
        counts[i["status"]] = counts.get(i["status"], 0) + 1
    return counts
    # <<< solution


# TODO 3.2
def vlan_ranges(vlans):
    """A list of VLAN numbers, written the way a trunk's allowed list is: [10, 11, 12, 20] -> "10-12,20".

    Sort them first and drop duplicates. Two or more numbers in a row become "first-last"; a number on
    its own stays as it is. No VLANs give "".

    >>> vlan_ranges([20, 12, 10, 11, 11, 30, 31])
    '10-12,20,30-31'
    """
    # >>> solution
    parts = []
    numbers = sorted(set(vlans))
    start = None
    for i, n in enumerate(numbers):
        if start is None:
            start = n
        last = i == len(numbers) - 1
        if last or numbers[i + 1] != n + 1:
            parts.append(str(start) if start == n else f"{start}-{n}")
            start = None
    return ",".join(parts)
    # <<< solution

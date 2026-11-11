"""Chapter 2 · strings, lists and dicts: text from the CLI in, dicts out, and back again."""


# TODO 2.1a
def parse_version_line(line):
    """The first line of `show version`, as a dict.

    >>> parse_version_line("CapeOS Software (CO-BOLT), Version 0.11.0, LAB USE ONLY")
    {'software': 'CapeOS Software', 'image': 'CO-BOLT', 'version': '0.11.0'}

    The line has three parts split by commas. The first is the software's name with the image in
    brackets, the second is "Version" and the version. Whatever comes after the second comma is ignored.
    """
    raise NotImplementedError("TODO 2.1a is still open")


# TODO 2.1b
def version_line(info):
    """The dict from parse_version_line, back into one line of text.

    >>> version_line({"software": "CapeOS Software", "image": "CO-BOLT", "version": "0.11.0"})
    'CapeOS Software CO-BOLT 0.11.0'
    """
    raise NotImplementedError("TODO 2.1b is still open")


# TODO 2.2
def interfaces_to_dicts(text):
    """`show ip interface brief` output, as a list with one dict per interface.

    Each dict has the keys interface, ip_address, ok, method, status and protocol, as strings, except
    that an "unassigned" address becomes None. Skip the header line and any blank lines. Watch out for
    the status "administratively down": it's two words.

    >>> interfaces_to_dicts(SAMPLE)[0]
    {'interface': 'GigabitEthernet0', 'ip_address': '172.80.111.11', 'ok': 'YES', 'method': 'DHCP',
     'status': 'up', 'protocol': 'up'}
    """
    raise NotImplementedError("TODO 2.2 is still open")


# A real `show ip interface brief` from r1, to try your functions on in the REPL:
#   >>> from netlab.parse import SAMPLE, interfaces_to_dicts
SAMPLE = """\
Interface              IP-Address      OK? Method Status                Protocol
GigabitEthernet0       172.80.111.11   YES DHCP   up                    up
GigabitEthernet1       192.168.10.1    YES manual up                    up
GigabitEthernet2       10.0.12.1       YES manual up                    up
GigabitEthernet3       10.0.13.1       YES manual up                    up
GigabitEthernet4       unassigned      YES unset  administratively down down
Loopback0              10.255.0.1      YES manual up                    up
"""

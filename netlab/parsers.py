"""Chapter 5 · parsing show output: the same table with a regular expression, with ntc-templates, and
with a TextFSM template of your own.

Every parser here returns a list of dicts. For `show ip interface brief` that's the four columns that
matter, with the same keys and values whichever parser made them:
    {"interface": "GigabitEthernet4", "ip_address": None, "status": "administratively down", "protocol": "down"}
(an "unassigned" address is None, as in chapter 2).
"""
import pathlib
import re

import textfsm
from ntc_templates.parse import parse_output

TEMPLATES = pathlib.Path(__file__).resolve().parents[1] / "templates"

# TODO 5.1a
# One line of `show ip interface brief`, with a named group for each column. The status is the tricky
# one: it can be two words ("administratively down").
# >>> solution | BRIEF_LINE = re.compile(r"")
BRIEF_LINE = re.compile(
    r"^(?P<interface>\S+)\s+(?P<ip_address>\S+)\s+(?P<ok>YES|NO)\s+(?P<method>\S+)\s+"
    r"(?P<status>up|down|administratively down)\s+(?P<protocol>\S+)\s*$"
)
# <<< solution


# TODO 5.1b
def parse_brief_regex(text):
    """`show ip interface brief` (CapeOS Bolt) with BRIEF_LINE, as a list of dicts (see the top of this file)."""
    # >>> solution
    rows = []
    for line in text.splitlines():
        m = BRIEF_LINE.match(line)
        if m:
            address = m["ip_address"]
            rows.append({
                "interface": m["interface"],
                "ip_address": None if address == "unassigned" else address,
                "status": m["status"],
                "protocol": m["protocol"],
            })
    return rows
    # <<< solution


# TODO 5.1c
def parse_brief_ntc(text, platform="cisco_ios"):
    """The same table, parsed by ntc-templates' template for `show ip interface brief` on this platform.

    ntc-templates calls the protocol column "proto" in its cisco_ios template and "protocol" in its
    arista_eos one. Return the same keys and values as parse_brief_regex, so the two can be compared.
    """
    # >>> solution
    rows = []
    for r in parse_output(platform=platform, command="show ip interface brief", data=text):
        rows.append({
            "interface": r["interface"],
            "ip_address": None if r["ip_address"] == "unassigned" else r["ip_address"],
            "status": r["status"],
            "protocol": r.get("proto", r.get("protocol")),
        })
    return rows
    # <<< solution


# TODO 5.2
def parse_ntp_associations(text):
    """`show ntp associations` (CapeOS Bolt), parsed by your template templates/ntp_associations.textfsm.

    ntc-templates has no template for this command, so you write one. It returns a list of dicts, one
    per server, with keys in lower case. These four must be there: address, ref_clock, stratum and
    reach. The header line and the legend at the bottom ("* sys.peer, # selected, ...") aren't servers.
    """
    # >>> solution
    with open(TEMPLATES / "ntp_associations.textfsm") as f:
        fsm = textfsm.TextFSM(f)
    keys = [h.lower() for h in fsm.header]
    return [dict(zip(keys, row)) for row in fsm.ParseText(text)]
    # <<< solution

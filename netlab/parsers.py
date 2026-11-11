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
BRIEF_LINE = re.compile(r"")


# TODO 5.1b
def parse_brief_regex(text):
    """`show ip interface brief` (CapeOS Bolt) with BRIEF_LINE, as a list of dicts (see the top of this file)."""
    raise NotImplementedError("TODO 5.1b is still open")


# TODO 5.1c
def parse_brief_ntc(text, platform="cisco_ios"):
    """The same table, parsed by ntc-templates' template for `show ip interface brief` on this platform.

    ntc-templates calls the protocol column "proto". Return the same keys and values as
    parse_brief_regex, so the two can be compared.
    """
    raise NotImplementedError("TODO 5.1c is still open")


# TODO 5.2
def parse_ntp_associations(text):
    """`show ntp associations` (CapeOS Bolt), parsed by your template templates/ntp_associations.textfsm.

    ntc-templates has no template for this command, so you write one. It returns a list of dicts, one
    per server, with keys in lower case. These four must be there: address, ref_clock, stratum and
    reach. The header line and the legend at the bottom ("* sys.peer, # selected, ...") aren't servers.
    """
    raise NotImplementedError("TODO 5.2 is still open")

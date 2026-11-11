"""Task 5.1 · parse_brief_regex() and parse_brief_ntc() in netlab/parsers.py: the same table, two ways."""
import gen
from conftest import DATA, call

from netlab.parsers import parse_brief_ntc, parse_brief_regex

KEYS = ("interface", "ip_address", "status", "protocol")


def four(rows):
    return [{k: r[k] for k in KEYS} for r in rows]


def test_regex_unseen():
    for _ in range(30):
        text, want = gen.brief(blank_lines=True)
        got = call(parse_brief_regex, text)
        assert got == four(want), f"the regex parse of\n{text}\nshould be\n{four(want)}\nand is\n{got}"


def test_ntc_unseen():
    for _ in range(15):
        text, want = gen.brief()
        got = call(parse_brief_ntc, text)
        assert got == four(want), f"the ntc-templates parse of\n{text}\nshould be\n{four(want)}\nand is\n{got}"


def test_they_agree_on_real_output():
    for f in sorted(DATA.glob("brief-*.txt")):
        text = f.read_text()
        a, b = call(parse_brief_regex, text), call(parse_brief_ntc, text)
        assert a == b, f"on {f.name} the two parsers disagree:\nregex: {a}\nntc:   {b}"
        assert len(a) == len([l for l in text.splitlines() if l.strip()]) - 1, f"{f.name}: one row per interface"

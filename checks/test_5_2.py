"""Task 5.2 · your TextFSM template, templates/ntp_associations.textfsm, through parse_ntp_associations()."""
import gen
import pytest
from conftest import DATA, ROOT, call

from netlab.parsers import parse_ntp_associations

KEYS = ("address", "ref_clock", "stratum", "reach")


def parse(text):
    try:
        return call(parse_ntp_associations, text)
    except Exception as e:                      # textfsm's own errors, with the line it stopped at
        pytest.fail(f"the template stopped with {type(e).__name__}: {e}", pytrace=False)


def test_template_exists():
    assert (ROOT / "templates" / "ntp_associations.textfsm").exists(), "there's no templates/ntp_associations.textfsm"


def test_the_keys():
    rows = parse((DATA / "ntp-r1.txt").read_text())
    assert rows, "the template found no servers in r1's output"
    missing = [k for k in KEYS if k not in rows[0]]
    assert not missing, f"each row needs the keys {', '.join(KEYS)} (Values in capitals become lower case). Missing: {missing}"


def test_real_outputs():
    for f in sorted(DATA.glob("ntp-*.txt")):
        text = f.read_text()
        servers = [l for l in text.splitlines()[1:] if l[2:3].isdigit()]
        rows = parse(text)
        assert len(rows) == len(servers), f"{f.name} has {len(servers)} servers, the template found {len(rows)}"


def test_unseen_outputs():
    for _ in range(40):
        text, want = gen.ntp_associations()
        got = [{k: r.get(k) for k in KEYS} for r in parse(text)]
        assert got == want, f"for this output\n{text}\nwe expected\n{want}\nand got\n{got}"


def test_no_servers():
    text, _ = gen.ntp_associations(0)
    assert parse(text) == [], "with no servers configured there are no rows"

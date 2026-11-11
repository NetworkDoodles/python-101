"""Task 2.2 · interfaces_to_dicts() in netlab/parse.py, on show outputs it hasn't seen."""
import gen
from conftest import DATA, call

from netlab.parse import interfaces_to_dicts


def show(rows):
    return "\n".join(f"    {r}" for r in rows)


def test_r1():
    text = (DATA / "brief-r1.txt").read_text()
    got = call(interfaces_to_dicts, text)
    assert len(got) == len(text.strip().splitlines()) - 1, "one dict per interface line: the header isn't an interface"
    gi4 = next((r for r in got if r.get("interface") == "GigabitEthernet4"), None)
    assert gi4, "GigabitEthernet4 is missing"
    assert gi4["status"] == "administratively down", f'GigabitEthernet4\'s status is "administratively down", not {gi4["status"]!r}'
    assert gi4["ip_address"] is None, "an unassigned address should be None"


def test_unseen_outputs():
    for _ in range(30):
        text, want = gen.brief(blank_lines=True)
        got = call(interfaces_to_dicts, text)
        assert got == want, f"for this output\n{text}\nwe expected\n{show(want)}\nand got\n{show(got)}"


def test_no_interfaces():
    header = "Interface              IP-Address      OK? Method Status                Protocol\n"
    assert call(interfaces_to_dicts, header) == [], "only the header: no interfaces, so []"
    assert call(interfaces_to_dicts, "") == [], "no output at all: []"

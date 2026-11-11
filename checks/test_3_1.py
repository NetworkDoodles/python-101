"""Task 3.1 · down_interfaces() and count_by_status() in netlab/interfaces.py."""
import gen
from conftest import call

from netlab.interfaces import count_by_status, down_interfaces


def test_down_interfaces():
    for _ in range(30):
        _, rows = gen.brief()
        want = [r["interface"] for r in rows if not (r["status"] == "up" and r["protocol"] == "up")]
        got = call(down_interfaces, rows)
        assert got == want, f"for these interfaces\n{rows}\nwe expected {want}\nand got      {got}"


def test_up_but_protocol_down():
    rows = [{"interface": "Gi1", "status": "up", "protocol": "down"}]
    assert call(down_interfaces, rows) == ["Gi1"], "status up but protocol down still isn't working"


def test_count_by_status():
    for _ in range(30):
        _, rows = gen.brief()
        want = {}
        for r in rows:
            want[r["status"]] = want.get(r["status"], 0) + 1
        got = call(count_by_status, rows)
        assert got == want, f"for statuses {[r['status'] for r in rows]}\nwe expected {want}\nand got      {got}"


def test_empty():
    assert call(down_interfaces, []) == []
    assert call(count_by_status, []) == {}

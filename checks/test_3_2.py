"""Task 3.2 · vlan_ranges() in netlab/interfaces.py: [10, 11, 12, 20] -> "10-12,20"."""
import random

from conftest import call

from netlab.interfaces import vlan_ranges


def expected(vlans):
    out, run = [], []
    for v in sorted(set(vlans)):
        if run and v == run[-1] + 1:
            run.append(v)
        else:
            if run:
                out.append(run)
            run = [v]
    if run:
        out.append(run)
    return ",".join(str(r[0]) if len(r) == 1 else f"{r[0]}-{r[-1]}" for r in out)


def test_the_example():
    assert call(vlan_ranges, [10, 11, 12, 20]) == "10-12,20"


def test_edges():
    for vlans, want in [([], ""), ([1], "1"), ([5, 6], "5-6"), ([1, 3, 5], "1,3,5"), ([4094, 4093], "4093-4094"),
                        ([20, 10, 11, 10, 12, 20], "10-12,20")]:
        assert call(vlan_ranges, vlans) == want, f"vlan_ranges({vlans}) should be {want!r}"


def test_unseen_lists():
    for _ in range(100):
        vlans = [random.randint(1, 60) for _ in range(random.randint(0, 25))]
        assert call(vlan_ranges, list(vlans)) == expected(vlans), f"vlan_ranges({vlans}) should be {expected(vlans)!r}"


def test_leaves_the_list_alone():
    vlans = [30, 10, 20, 10]
    call(vlan_ranges, vlans)
    assert vlans == [30, 10, 20, 10], "vlan_ranges changed the list it was given: sort a copy (sorted() makes one)"

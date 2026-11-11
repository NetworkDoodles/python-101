"""Task 2.1 · parse_version_line() and version_line() in netlab/parse.py, on lines they haven't seen."""
import gen
from conftest import DATA, call

from netlab.parse import parse_version_line, version_line

REAL = (DATA / "version-lines.txt").read_text().splitlines()


def test_the_lab_line():
    assert call(parse_version_line, "CapeOS Software (CO-BOLT), Version 0.11.0, LAB USE ONLY") == \
        {"software": "CapeOS Software", "image": "CO-BOLT", "version": "0.11.0"}


def test_lines_from_the_lab_devices():
    for line in REAL:
        got = call(parse_version_line, line)
        assert set(got) == {"software", "image", "version"}, f"the keys should be software, image and version: {got}"
        assert line.startswith(got["software"]) and f"({got['image']})" in line and f"Version {got['version']}" in line, \
            f"{line!r} gave {got}"


def test_unseen_lines():
    for _ in range(40):
        line, want = gen.version_line()
        got = call(parse_version_line, line)
        assert got == want, f"for the line\n    {line}\nwe expected {want}\nand got      {got}"


def test_back_into_a_line():
    for _ in range(20):
        line, want = gen.version_line()
        assert call(version_line, want) == f"{want['software']} {want['image']} {want['version']}", \
            f"version_line({want}) should give one line: software, image and version, with a space between each"

"""Inventory every device: log in, read show version, and write one CSV row per device.

    python scripts/inventory.py                           inventory.yml -> inventory.csv
    python scripts/inventory.py --source api --out x.csv  the lab's API instead, another file (task 8.3)

It writes every device it reached, lists the ones it couldn't on stderr, and exits 2 if there were any.
"""
import argparse
import sys
import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))               # so `import netlab` finds the repo's netlab/

from netlab.report import load_devices, run, write_csv  # noqa: E402


# TODO 8.3
def parse_args(argv=None):
    """The command line's options: --source yaml|api (default yaml) and --out FILE (default inventory.csv)."""
    # TODO 8.3: no options yet, just the defaults.
    return argparse.Namespace(source="yaml", out="inventory.csv")


def main(argv=None):
    args = parse_args(argv)
    devices = load_devices(args.source)
    rows, failures = run(devices)
    write_csv(rows, args.out)
    print(f"wrote {args.out}: {len(rows)} of {len(devices)} devices")
    for name, reason in failures.items():
        print(f"  couldn't inventory {reason}", file=sys.stderr)
    return 2 if failures else 0


if __name__ == "__main__":
    sys.exit(main())

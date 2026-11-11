"""Which devices have an NTP server configured? Reads a folder of saved configs, writes a CSV.

    python scripts/ntp_report.py                       configs/ -> reports/ntp.csv
    python scripts/ntp_report.py FOLDER OUT.csv        any folder, any output file
"""
import pathlib
import sys

# Python looks for modules next to the script it runs (scripts/). This adds the repo's own folder too,
# so `import netlab` finds netlab/.
ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from netlab.configs import load_configs_safe, write_report  # noqa: E402


def main(argv):
    folder = pathlib.Path(argv[1]) if len(argv) > 1 else ROOT / "configs"
    out = pathlib.Path(argv[2]) if len(argv) > 2 else ROOT / "reports" / "ntp.csv"
    configs, problems = load_configs_safe(folder)
    write_report(configs, out)
    print(f"wrote {out} ({len(configs)} devices)")
    for name, reason in problems.items():
        print(f"skipped {name}: {reason}", file=sys.stderr)
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

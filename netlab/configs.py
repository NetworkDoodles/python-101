"""Chapter 4 · files, modules and errors: a folder of saved configs in, a CSV report out.

scripts/ntp_report.py runs these. Each file in the folder is one device's saved running-config, and the
file name without .cfg is the device's name: configs/r1.cfg is r1.
"""
import csv
import pathlib


# TODO 4.1a
def has_ntp(config_text):
    """True when the config has at least one line that starts with "ntp server", otherwise False."""
    # >>> solution
    for line in config_text.splitlines():
        if line.startswith("ntp server"):
            return True
    return False
    # <<< solution


# TODO 4.1b
def load_configs(folder):
    """Every *.cfg file in the folder, as a dict of device name -> the file's text, sorted by name.

    Other files (a README, a .txt) are ignored. Read the files as UTF-8.
    """
    # >>> solution
    configs = {}
    for path in sorted(pathlib.Path(folder).glob("*.cfg")):
        configs[path.stem] = path.read_text(encoding="utf-8")
    return configs
    # <<< solution


# TODO 4.1c
def write_report(configs, out_path):
    """Write the NTP report as a CSV file with a header row and one row per device, sorted by name:

        device,has_ntp
        r1,yes
        r2,no

    Create the folder the file goes in if it isn't there yet.
    """
    # >>> solution
    out_path = pathlib.Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["device", "has_ntp"])
        for name in sorted(configs):
            writer.writerow([name, "yes" if has_ntp(configs[name]) else "no"])
    # <<< solution


# TODO 4.2
def load_configs_safe(folder):
    """Like load_configs, but a file that can't be read doesn't stop the others.

    Returns two dicts: (configs, problems). configs is device name -> text for every file that read
    cleanly. problems is file name (like "r9.cfg") -> a short reason, for every *.cfg file that
    couldn't be read: one you're not allowed to read (PermissionError), or one that isn't UTF-8 text
    (UnicodeDecodeError). Catch only those two: anything else is a bug, and should still stop you.
    """
    # >>> solution
    configs, problems = {}, {}
    for path in sorted(pathlib.Path(folder).glob("*.cfg")):
        try:
            configs[path.stem] = path.read_text(encoding="utf-8")
        except PermissionError:
            problems[path.name] = "permission denied"
        except UnicodeDecodeError as e:
            problems[path.name] = f"not UTF-8 text (byte {e.start})"
    return configs, problems
    # --- starter: this one stops at the first bad file. Make it carry on.
    #| return load_configs(folder), {}
    # <<< solution

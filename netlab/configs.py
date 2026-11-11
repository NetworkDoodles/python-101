"""Chapter 4 · files, modules and errors: a folder of saved configs in, a CSV report out.

scripts/ntp_report.py runs these. Each file in the folder is one device's saved running-config, and the
file name without .cfg is the device's name: configs/r1.cfg is r1.
"""
import csv
import pathlib


# TODO 4.1a
def has_ntp(config_text):
    """True when the config has at least one line that starts with "ntp server", otherwise False."""
    raise NotImplementedError("TODO 4.1a is still open")


# TODO 4.1b
def load_configs(folder):
    """Every *.cfg file in the folder, as a dict of device name -> the file's text, sorted by name.

    Other files (a README, a .txt) are ignored. Read the files as UTF-8.
    """
    raise NotImplementedError("TODO 4.1b is still open")


# TODO 4.1c
def write_report(configs, out_path):
    """Write the NTP report as a CSV file with a header row and one row per device, sorted by name:

        device,has_ntp
        r1,yes
        r2,no

    Create the folder the file goes in if it isn't there yet.
    """
    raise NotImplementedError("TODO 4.1c is still open")


# TODO 4.2
def load_configs_safe(folder):
    """Like load_configs, but a file that can't be read doesn't stop the others.

    Returns two dicts: (configs, problems). configs is device name -> text for every file that read
    cleanly. problems is file name (like "r9.cfg") -> a short reason, for every *.cfg file that
    couldn't be read: one you're not allowed to read (PermissionError), or one that isn't UTF-8 text
    (UnicodeDecodeError). Catch only those two: anything else is a bug, and should still stop you.
    """
    # TODO 4.2: this one stops at the first bad file. Make it carry on.
    return load_configs(folder), {}

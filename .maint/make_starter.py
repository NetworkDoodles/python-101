#!/usr/bin/env python3
"""Maintainers only: turn the solution files into the starter files learners get on main.

Solution code sits between marker lines:

    # >>> solution | <optional one-line starter>
    ...finished code...
    # --- starter: <optional note>          (optional: a starter block of several lines follows)
    #| starter code, one line each
    # <<< solution

On main each block becomes, in this order of preference: the starter lines (with the note as a comment),
the one-line starter, or `raise NotImplementedError("TODO x.ya is still open")`, where x.ya comes from
the last `# TODO x.ya` line above the block. Files in .maint/starter/ replace their solution twins whole.

    python .maint/make_starter.py <solution checkout> <starter checkout>
"""
import pathlib
import re
import shutil
import sys

# The files each chapter's solution changes. main has the starter version of each (or none, for the
# ones in ONLY_SOLUTION, which the learner writes).
CHAPTERS = {
    1: ["scripts/hello.py", "answers/1.1.yml", "scratch/requirements.txt"],
    2: ["netlab/parse.py"],
    3: ["netlab/interfaces.py"],
    4: ["netlab/configs.py"],
    5: ["netlab/parsers.py", "templates/ntp_associations.textfsm"],
    6: ["netlab/devices.py"],
    7: ["netlab/inventory.py", "inventory.yml"],
    8: ["netlab/report.py", "scripts/inventory.py"],
}
ONLY_SOLUTION = ["scripts/hello.py", "scratch/requirements.txt"]
STARTER_DIR = pathlib.Path(__file__).resolve().parent / "starter"

OPEN = re.compile(r"^(\s*)# >>> solution(?: \| (.*))?$")
STARTER = re.compile(r"^\s*# --- starter(?::\s*(.*))?$")
CLOSE = re.compile(r"^\s*# <<< solution$")
TODO = re.compile(r"\s*# (TODO \d+\.\d+[a-z]?)")


def strip(text):
    out, todo, state, indent, one_liner, starter = [], "TODO", "code", "", None, []
    for line in text.splitlines():
        if state == "code":
            if m := TODO.match(line):
                todo = m.group(1)
            if m := OPEN.match(line):
                indent, one_liner, starter, state = m.group(1), m.group(2), [], "solution"
                continue
            out.append(line)
        elif state == "solution":
            if m := STARTER.match(line):
                if m.group(1):
                    starter.append(f"{indent}# {todo}: {m.group(1)}")
                state = "starter"
            elif CLOSE.match(line):
                out.append(indent + one_liner if one_liner else f'{indent}raise NotImplementedError("{todo} is still open")')
                state = "code"
        elif state == "starter":
            if CLOSE.match(line):
                out.extend(starter)
                state = "code"
            else:
                starter.append(re.sub(r"^(\s*)#\| ?", r"\1", line))
    return "\n".join(out) + "\n"


def main(src, dst):
    for files in CHAPTERS.values():
        for f in files:
            target = dst / f
            if f in ONLY_SOLUTION:
                if target.exists():
                    target.unlink()
                continue
            if (STARTER_DIR / f).exists():
                shutil.copy(STARTER_DIR / f, target)
            else:
                target.write_text(strip((src / f).read_text()))
            print("starter:", f)


if __name__ == "__main__":
    main(*(pathlib.Path(p) for p in sys.argv[1:3]))

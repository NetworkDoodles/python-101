"""make check T=2.1 · CH=2 · (nothing)  ·  verifies a task, a chapter or the whole lab, with pytest.

Each task has its own file of checks, checks/test_<chapter>_<task>.py. They import your functions and call
them on inputs you haven't seen (made up fresh each time, or recorded from devices), and the live ones
compare your results with what the devices say right now. Read them: they're the spec, written as code.
"""
import os
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
TASKS = sorted(p.stem[5:].replace("_", ".") for p in (ROOT / "checks").glob("test_*_*.py"))
TTY = sys.stdout.isatty() and not os.environ.get("NO_COLOR")
G, R, B, D, X = (("\033[32m", "\033[31m", "\033[1m", "\033[2m", "\033[0m") if TTY else ("",) * 5)


def files(what):
    if what == "all":
        return TASKS
    if what.startswith("ch"):
        return [t for t in TASKS if t.split(".")[0] == what[2:]]
    return [what] if what in TASKS else []


def main():
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    tasks = files(what)
    if not tasks:
        sys.exit(f"there's no task {what}. The tasks are {', '.join(TASKS)}")
    failed = []
    for t in tasks:
        print(f"\n{B}task {t}{X}  {D}checks/test_{t.replace('.', '_')}.py{X}", flush=True)
        args = [sys.executable, "-m", "pytest", f"checks/test_{t.replace('.', '_')}.py", "-v", "--tb=short",
                "--no-header", "-p", "no:cacheprovider", "-W", "ignore::DeprecationWarning", "-rN", "--color=" + ("yes" if TTY else "no")]
        if subprocess.run(args, cwd=ROOT).returncode != 0:
            failed.append(t)
    print()
    if failed:
        print(f"{R}✗{X} not yet: {', '.join(failed)}. Each failure above says what's missing (pytest marks the line "
              f"with E); the checks themselves are in checks/.\n")
        return 1
    print(f"{G}✓{X} {'all ' + str(len(tasks)) + ' tasks' if len(tasks) > 1 else 'task ' + tasks[0]} done\n")
    return 0


sys.exit(main())

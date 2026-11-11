"""make solve T=2.1 · make skip CH=4 · make break T=6.2

solve  Stuck, or want to compare? Puts the solution of one task into your files: only the functions that
       task asks for, taken from the solution tag of its chapter (solution-ch2 for task 2.1), so your other
       work stays as it is. Tasks 1.1 and 1.2 have no code to copy: solve runs their commands for you,
       printing each one. Afterwards, `git diff --staged` shows what changed.
skip   Start at a later chapter: solves every task before it.
break  Sets up a task's problem on purpose (4.2, 6.2, 8.2). `make reset` puts everything back.
"""
import ast
import os
import pathlib
import re
import shutil
import subprocess
import sys

sys.path.insert(0, pathlib.Path(__file__).resolve().parent.as_posix())
import lab  # noqa: E402

ROOT = lab.ROOT
ANSWERS = ROOT / "answers"

# Which names (functions, classes, variables) each task asks for, by file. None means the whole file.
TASKS = {
    "1.1": {}, "1.2": {},
    "2.1": {"netlab/parse.py": ["parse_version_line", "version_line"]},
    "2.2": {"netlab/parse.py": ["interfaces_to_dicts"]},
    "3.1": {"netlab/interfaces.py": ["down_interfaces", "count_by_status"]},
    "3.2": {"netlab/interfaces.py": ["vlan_ranges"]},
    "4.1": {"netlab/configs.py": ["has_ntp", "load_configs", "write_report"]},
    "4.2": {"netlab/configs.py": ["load_configs_safe"]},
    "5.1": {"netlab/parsers.py": ["BRIEF_LINE", "parse_brief_regex", "parse_brief_ntc"]},
    "5.2": {"netlab/parsers.py": ["parse_ntp_associations"], "templates/ntp_associations.textfsm": None},
    "6.1": {"netlab/devices.py": ["connect", "interface_table"]},
    "6.2": {"netlab/devices.py": ["Device", "collect"]},
    "7.1": {"netlab/inventory.py": ["load_inventory", "save_json", "load_json"], "inventory.yml": None},
    "7.2": {"netlab/inventory.py": ["get_devices", "api_to_inventory"]},
    "8.1": {"netlab/report.py": ["load_devices", "facts", "write_csv"]},
    "8.2": {"netlab/report.py": ["run"]},
    "8.3": {"scripts/inventory.py": ["parse_args"]},
}
MARKER = re.compile(r"^\s*# (>>> solution|<<< solution|--- starter)|^\s*#\| ")
SCRATCH_PACKAGE = "netaddr==1.3.0"


def say(where, what):
    print(f"  {where:<9} {what}")


def sh(cmd, **kw):
    say("$", cmd)
    p = subprocess.run(cmd, shell=True, cwd=ROOT, capture_output=True, text=True, **kw)
    out = (p.stdout + p.stderr).strip()
    for line in out.splitlines()[-6:]:
        print(f"            {line}")
    return p.returncode, out


def outside_venv_path():
    """PATH without any venv on it: what a terminal sees after `deactivate`."""
    venv = os.environ.get("VIRTUAL_ENV")
    exe_dir = str(pathlib.Path(sys.executable).parent)
    return os.pathsep.join(p for p in os.environ.get("PATH", "").split(os.pathsep)
                           if p and p != exe_dir and not (venv and p.startswith(venv)))


def fill(task, values):
    """Write values into answers/<task>.yml after their keys, keeping every comment."""
    path = ANSWERS / f"{task}.yml"
    lines = path.read_text().splitlines()
    for i, line in enumerate(lines):
        key = line.split(":")[0].strip()
        if key in values and not line.lstrip().startswith("#"):
            comment = line[line.index("#"):] if "#" in line else ""
            lines[i] = f"{key + ':':<17} {values[key]}" + (f"   {comment}" if comment else "")
    path.write_text("\n".join(lines) + "\n")
    say("answers", f"filled in answers/{task}.yml")


# ── the solution, from git ─────────────────────────────────────────────────────
def tag_for(task):
    return f"solution-ch{task.split('.')[0]}"


def from_tag(tag, path):
    p = subprocess.run(["git", "show", f"{tag}:{path}"], cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        subprocess.run(["git", "fetch", "-q", "origin", "--tags"], cwd=ROOT, capture_output=True)
        p = subprocess.run(["git", "show", f"{tag}:{path}"], cwd=ROOT, capture_output=True, text=True)
    if p.returncode != 0:
        sys.exit(f"can't read {path} from {tag}: {p.stderr.strip()}  (is this a clone of the lab's repo?)")
    return p.stdout


def spans(source):
    """{top-level name: (first line, last line)} for every function, class and assignment, 1-based,
    decorators included."""
    out = {}
    for node in ast.parse(source).body:
        names = []
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            names = [node.name]
        elif isinstance(node, ast.Assign):
            names = [t.id for t in node.targets if isinstance(t, ast.Name)]
        start = min([node.lineno] + [d.lineno for d in getattr(node, "decorator_list", [])])
        for n in names:
            out[n] = (start, node.end_lineno)
    return out


def clean(lines):
    return [l for l in lines if not MARKER.match(l)]


def patch(path, names, tag):
    """Replace the named functions in the learner's file with the solution's, leaving the rest alone."""
    solution = from_tag(tag, path)
    target = ROOT / path
    mine = target.read_text()
    try:
        my_spans = spans(mine)
    except SyntaxError as e:
        sys.exit(f"{path} has a syntax error on line {e.lineno}, so solve can't find the functions in it. "
                 f"Fix it, or start the file again: git checkout {path}")
    sol_lines, sol_spans = solution.splitlines(), spans(solution)
    my_lines = mine.splitlines()
    # Replace from the bottom up, so earlier line numbers stay right.
    for name in sorted(names, key=lambda n: my_spans.get(n, (10**9,))[0], reverse=True):
        a, b = sol_spans[name]
        new = clean(sol_lines[a - 1:b])
        if name in my_spans:
            x, y = my_spans[name]
            # Marker lines sit just above a block in the solution; don't leave the starter's copy behind.
            my_lines[x - 1:y] = new
        else:
            my_lines += ["", ""] + new
    target.write_text("\n".join(my_lines) + "\n")
    say("solution", f"{', '.join(n + ('()' if not n.isupper() and n[0].islower() else '') for n in names)} "
                    f"in {path}, from {tag}")


def stage(path):
    """git add the file solve changed, so `git diff --staged` shows it against your last commit."""
    subprocess.run(["git", "add", "--", path], cwd=ROOT, capture_output=True)


def solve_code(task):
    tag = tag_for(task)
    for path, names in TASKS[task].items():
        if names is None:
            (ROOT / path).write_text("\n".join(clean(from_tag(tag, path).splitlines())) + "\n")
            say("solution", f"{path}, from {tag}")
        else:
            patch(path, names, tag)
        stage(path)


# ── the tasks with nothing to copy ─────────────────────────────────────────────
def solve_1_1():
    hello = ROOT / "scripts" / "hello.py"
    hello.write_text('print("Hello, network!")\n')
    say("wrote", "scripts/hello.py:  print(\"Hello, network!\")")
    sh("python scripts/hello.py")
    venv_python = pathlib.Path(sys.executable)
    version = subprocess.run([str(venv_python), "--version"], capture_output=True, text=True).stdout.split()[-1]
    system = shutil.which("python", path=outside_venv_path()) or shutil.which("python3", path=outside_venv_path())
    say("$", "which python   (inside the venv, then after deactivate)")
    fill("1.1", {"version": version, "venv_python": str(venv_python.parent / "python"),
                 "repl_answer": len("GigabitEthernet1"), "system_python": system})


def solve_1_2():
    system = shutil.which("python3", path=outside_venv_path())
    sh(f"{system} -m venv scratch/.venv")
    sh(f"scratch/.venv/bin/python -m pip install -q --disable-pip-version-check {SCRATCH_PACKAGE}")
    code, freeze = sh("scratch/.venv/bin/python -m pip freeze")
    (ROOT / "scratch" / "requirements.txt").write_text(freeze.strip() + "\n")
    say("wrote", "scratch/requirements.txt (the pip freeze above)")
    sh(f"{system} -c 'import netaddr'")
    say("", "^ outside the scratch venv, Python can't find netaddr: that's the point")


def solve(task):
    if task not in TASKS:
        sys.exit(f"there's no task {task}: the tasks are {', '.join(TASKS)}")
    print(f"\n  solving task {task}\n")
    if task == "1.1":
        solve_1_1()
    elif task == "1.2":
        solve_1_2()
    else:
        solve_code(task)
    if task in ("6.1", "6.2", "7.2", "8.1", "8.2", "8.3") and not (ROOT / ".env").exists():
        shutil.copy(ROOT / ".env.example", ROOT / ".env")
        say("wrote", ".env, from .env.example")
    print(f"\n  done. See what changed with  git diff --staged   and check it with  make check T={task}\n")


def skip(chapter):
    if not chapter.isdigit() or not 2 <= int(chapter) <= 8:
        sys.exit("usage: make skip CH=<2-8>: solves every task in the chapters before it")
    for task in TASKS:
        if int(task.split(".")[0]) < int(chapter):
            solve(task)
    print(f"  you're at the start of chapter {chapter}.\n")


# ── problems on purpose ────────────────────────────────────────────────────────
BROKEN = ["configs/old-r9.cfg", "configs/locked.cfg"]
R9 = """  # added by make break T=8.2 (make reset takes it out again)
  - name: r9
    host: 172.80.111.19
    device_type: cisco_ios
    role: router
    model: CapeOS-Bolt
  # end of make break T=8.2
"""


def break_4_2():
    old, locked = (ROOT / p for p in BROKEN)
    old.write_bytes("! r9, saved by an old backup tool\nhostname r9\nbanner motd ^C Caf\xe9 network ^C\n"
                    "ntp server 172.80.111.12\n".encode("latin-1"))
    say("wrote", f"{BROKEN[0]}: saved in Latin-1, so the é isn't valid UTF-8")
    locked.write_text("hostname r8\nntp server 172.80.111.12\n")
    locked.chmod(0)
    say("wrote", f"{BROKEN[1]}: and took away every permission on it (chmod 000)")


def break_6_2():
    lab.config("r2", "username admin privilege 15 secret not-the-lab-password")
    say("r2", "username admin privilege 15 secret not-the-lab-password")
    say("", "r2 now refuses the lab's password: your code has to say so in one clear line")


def break_8_2():
    lab.run(["docker", "stop", "-t", "1", "r2"])
    say("docker", "stop r2   (as if it lost power)")
    inv = ROOT / "inventory.yml"
    text = inv.read_text()
    if "name: r9" not in text:
        inv.write_text(text.rstrip("\n") + "\n" + R9)
    say("wrote", "r9 at the end of inventory.yml: a device that doesn't exist")
    devices = [dict(id=d["id"], name=d["name"], role=d["role"]["slug"], model=d["device_type"]["model"],
                    platform=d["platform"]["slug"], ip=d["primary_ip"]["address"], site="lab")
               for d in (lab.api_get("/api/devices/")[1] or {}).get("results", [])]
    if devices and not any(d["name"] == "r9" for d in devices):
        devices.append(dict(id=9, name="r9", role="router", model="CapeOS-Bolt", platform="cisco_ios",
                            ip="172.80.111.19/24", site="lab"))
        import json
        lab.sh("api", f"mkdir -p /run/api && cat > /run/api/devices.json <<'EOF'\n{json.dumps(devices)}\nEOF")
        say("api", "r9 in the API's devices too")


def unbreak():
    """Undo what `make break` did to your files (the network comes back with `make up`)."""
    for p in BROKEN:
        f = ROOT / p
        if f.exists():
            f.chmod(0o644)
            f.unlink()
            say("removed", p)
    inv = ROOT / "inventory.yml"
    if inv.exists() and "make break T=8.2" in inv.read_text():
        inv.write_text(re.sub(r"  # added by make break T=8\.2.*?# end of make break T=8\.2\n", "",
                              inv.read_text(), flags=re.S))
        say("removed", "r9 from inventory.yml")


BREAKS = {"4.2": break_4_2, "6.2": break_6_2, "8.2": break_8_2}

if __name__ == "__main__":
    what, arg = (sys.argv[1:] + ["", ""])[:2]
    if what == "solve":
        solve(arg)
    elif what == "skip":
        skip(arg)
    elif what == "break":
        if arg not in BREAKS:
            sys.exit(f"only tasks {', '.join(BREAKS)} have a problem to set up")
        print(f"\n  setting up task {arg}'s problem\n")
        BREAKS[arg]()
        print("\n  make reset puts everything back.\n")
    elif what == "unbreak":
        unbreak()
    else:
        sys.exit(__doc__)

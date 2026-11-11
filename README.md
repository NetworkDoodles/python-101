# Python 101 for network engineers

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/NetworkDoodles/python-101?quickstart=1)

The hands-on lab for [Python 101 for network engineers](https://networkdoodles.com/lessons/python-101/) by
David Henderson. You write small Python functions that turn CLI output into data, then point them at real
devices: log in with Netmiko, parse with TextFSM and ntc-templates, read an inventory from YAML and from a
REST API, and finish with a script that inventories every device to a CSV and says which ones it couldn't
reach.

**The guide:** https://networkdoodles.com/labs/python-101/

```
  host1 ── sw1 ── r1 ════ 10.0.12.0/30 ════ r2 ── host2
     192.168.10.0/24  ╲                    ╱  192.168.20.0/24
              10.0.13.0/30 ╲            ╱ 10.0.23.0/30
                             r3 (Pulse)

  management network 172.80.111.0/24:  r1 .11   r2 .12   r3 .13   sw1 .21   api .50 (http://api:8000)
```

## Start

1. Click **Open in GitHub Codespaces** above, then **Create codespace**. If VS Code asks whether you trust
   the folder, click **Trust Folder & Continue**.
2. Wait for the **Lab status** terminal to show every node with a green tick (the first start takes a few
   minutes).
3. Follow [task 1.1](https://networkdoodles.com/labs/python-101/task-1-1/).

## Commands

| Command | What it does |
|---|---|
| `make check T=2.1` | check a task (`CH=2` checks a chapter, nothing checks them all). The checks are pytest files in `checks/` |
| `make solve T=2.1` | stuck? puts that task's solution in your files: only the functions it asks for |
| `make skip CH=5` | start at a later chapter: solves every task before it |
| `make break T=6.2` | a task's problem, on purpose (4.2, 6.2 and 8.2 have one) |
| `make reset` | put the whole lab back how it started. Your code stays as it is |
| `make shell H=r1` | log in to a device's CLI (`r1 r2 r3 sw1`) or a host (`host1 host2 api`) |
| `make status` | what's running |
| `make help` | everything else |

## What's where

| | |
|---|---|
| `netlab/` | your code: one module per chapter, with a `TODO x.ya` where each task starts |
| `scripts/` | the scripts that run it: `ntp_report.py`, `r1_interfaces.py`, `collect.py`, `inventory.py` |
| `templates/` | your TextFSM template (task 5.2) |
| `configs/` | saved configs from the lab's devices (chapter 4) |
| `inventory.yml` | the lab's devices (chapters 7 and 8) |
| `.env` | the lab's login and API token: `make setup` copies `.env.example` there. Git ignores it |
| `checks/` | the checker: one pytest file per task |
| `lab/` | the lab itself: topology, device configs, the API |

The `solution` branch has the finished code, one commit per chapter, tagged `solution-ch1` to `solution-ch8`.

## The devices

r1, r2 and sw1 run CapeOS Bolt, and r3 runs CapeOS Pulse: an open-source lab network OS whose two dialects
behave like the CLIs that automation tools already know. So Netmiko, TextFSM, ntc-templates and the rest are
used here exactly as they are, with `device_type` `cisco_ios` for Bolt and `arista_eos` for Pulse. The login is
`admin` / `capeos-lab`, in `.env`.

Python is the dev container's own, 3.11, with the packages pinned in `requirements.txt` in a venv at
`~/.venvs/lab`. Every new terminal activates it.

## On a laptop

Open the folder in VS Code with the Dev Containers extension (**Reopen in Container**), or run
`devcontainer up --workspace-folder .` and open http://localhost:13337. Docker Desktop with 4 GB for it is
plenty.

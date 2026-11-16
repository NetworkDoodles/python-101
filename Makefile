# Network Doodles lab · Python 101 for network engineers
# Guide: https://networkdoodles.com/labs/python-101/
#
# Tasks are numbered chapter.task, so T=2.1 is chapter 2, task 1. CH=<n> means a whole chapter.
.DEFAULT_GOAL := help
# The dev container keeps the lab's venv outside the repo (VENV is set there); on a laptop it's .venv.
VENV ?= .venv
PY := $(VENV)/bin/python
TOPO := lab/topology.clab.yml
BOLT := ghcr.io/dkhenderson2/capeos-bolt:0.11.2
PULSE := ghcr.io/dkhenderson2/capeos-pulse:0.11.2
HOST := nd-pyhost:1
NODES := r1 r2 r3 sw1 api host1 host2
T ?=
CH ?=
H ?=

help: ## show this help
	@grep -hE '^[a-z0-9-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  \033[36m%-8s\033[0m %s\n", $$1, $$2}'

REQS := requirements.txt
REQ_HASH = $(shell python3 -c "import hashlib,sys; print(hashlib.sha256(b''.join(open(f,'rb').read() for f in sys.argv[1:])).hexdigest()[:16])" $(REQS))

setup: ## create the lab's venv (the pinned packages in requirements.txt) and .env
	@if [ "$$(cat $(VENV)/.ok 2>/dev/null)" = "$(REQ_HASH)" ] && [ -x $(PY) ]; then :; else \
	  echo "installing the lab's Python packages into $(VENV)"; \
	  python3 -m venv --prompt lab $(VENV) && $(PY) -m pip install -q --disable-pip-version-check -r $(REQS) \
	  && echo "$(REQ_HASH)" > $(VENV)/.ok; \
	fi
	@test -f .env || (cp .env.example .env && echo "wrote .env from .env.example: the lab's login and API token")

# The dev container's own Docker engine starts alongside the container, so the first commands can beat it.
docker-ready:
	@for i in $$(seq 1 60); do docker info >/dev/null 2>&1 && exit 0; [ $$i = 1 ] && echo "  waiting for Docker to start ..."; sleep 2; done; \
	echo "Docker isn't answering. In the dev container it starts on its own; on a laptop, start Docker Desktop."; exit 1

images: docker-ready ## pull the device images and build the hosts' image (the dev container does this once)
	@docker image inspect $(BOLT) >/dev/null 2>&1 || docker pull -q $(BOLT)
	@docker image inspect $(PULSE) >/dev/null 2>&1 || docker pull -q $(PULSE)
	@docker build -q -t $(HOST) lab/host >/dev/null && echo "  built $(HOST), the lab's hosts and API"

up: setup docker-ready ## start the lab: three routers, a switch, two hosts and the API (about a minute)
	@command -v containerlab >/dev/null || (echo "containerlab isn't installed: it comes with the dev container"; exit 2)
	@$(MAKE) -s images
	containerlab deploy -t $(TOPO) --reconfigure
	@$(PY) lab/wait.py

down: ## remove the lab (your code stays)
	containerlab destroy -t $(TOPO) --cleanup

reset: ## everything back to how it started, make break's problems included (your code stays)
	@$(PY) lab/solve.py unbreak
	$(MAKE) up

shell: ## log in to a device's CLI or a host's shell:  make shell H=r1
	@case " $(NODES) " in *" $(H) "*) ;; *) echo "usage: make shell H=<name>   one of: $(NODES)"; exit 2;; esac
	@case "$(H)" in r1|r2|r3|sw1) docker exec -it $(H) capeos-cli;; *) docker exec -it -w /root $(H) bash;; esac

status: ## what's running, and where to start  (WAIT=1 waits for the lab)
	@$(PY) lab/status.py $(if $(WAIT),--wait)

check: ## verify a task, a chapter or everything:  make check T=2.1 · CH=2 · (nothing)
	@$(PY) checks/check.py $(if $(T),$(T),$(if $(CH),ch$(CH),all))

solve: ## stuck? put one task's solution in your files (only that task's functions):  make solve T=2.1
	@test -n "$(T)" || (echo "usage: make solve T=<chapter.task>, e.g. T=2.1"; exit 2)
	@$(PY) lab/solve.py solve $(T)

skip: ## start at a later chapter: solves every task before it:  make skip CH=5
	@test -n "$(CH)" || (echo "usage: make skip CH=<2-8>"; exit 2)
	@$(PY) lab/solve.py skip $(CH)

break: ## set up a task's problem on purpose:  make break T=4.2 · T=6.2 · T=8.2
	@test -n "$(T)" || (echo "usage: make break T=4.2|6.2|8.2"; exit 2)
	@$(PY) lab/solve.py break $(T)

.PHONY: help setup docker-ready images up down reset shell status check solve skip break

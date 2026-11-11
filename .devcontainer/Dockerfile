# The lab's dev container: containerlab's Docker-in-Docker image plus the lab's Python venv.
# The venv is built here, in the image, so it's ready from the first second. It uses the image's own
# Python (3.11), and every new terminal activates it: that's the (lab) at the start of the prompt.
FROM ghcr.io/srl-labs/containerlab/devcontainer-dind-slim:0.83.0

USER vscode
ENV VENV=/home/vscode/.venvs/lab
COPY --chown=vscode:vscode requirements.txt /tmp/lab/
COPY --chown=vscode:vscode .devcontainer/activate.sh /tmp/lab/
# .ok records which requirements were installed (the same hash `make setup` checks), so the first start
# doesn't reinstall them.
RUN python3 -m venv --prompt lab "$VENV" \
 && "$VENV/bin/python" -m pip install -q --disable-pip-version-check -r /tmp/lab/requirements.txt \
 && cd /tmp/lab && python3 -c "import hashlib,sys; print(hashlib.sha256(b''.join(open(f,'rb').read() for f in sys.argv[1:])).hexdigest()[:16])" requirements.txt > "$VENV/.ok" \
 && cat /tmp/lab/activate.sh >> /home/vscode/.zshrc && cat /tmp/lab/activate.sh >> /home/vscode/.bashrc

# code-server reads its own settings, not devcontainer.json's.
COPY --chown=vscode:vscode .devcontainer/code-server-settings.json /home/vscode/.local/share/code-server/User/settings.json

# The lab's hosts and its inventory API: a small Debian computer with Python and the everyday
# network tools.
FROM debian:bookworm-slim
RUN apt-get update && apt-get install -y --no-install-recommends python3 iproute2 iputils-ping \
 && rm -rf /var/lib/apt/lists/* && echo 'PS1="\h:\w# "' > /root/.bashrc
COPY start.sh /usr/local/bin/start
CMD ["sleep", "infinity"]

#!/bin/sh
# Sets a node up when the lab starts (containerlab runs `start <role>` on it).
set -e
sysctl -qw net.ipv6.conf.all.disable_ipv6=1 net.ipv6.conf.default.disable_ipv6=1 2>/dev/null || true
case "$1" in
  host1)
    ip link set eth1 up
    ip addr add 192.168.10.10/24 dev eth1
    ip route add default via 192.168.10.1
    ;;
  host2)
    ip link set eth1 up
    ip addr add 192.168.20.10/24 dev eth1
    ip route add default via 192.168.20.1
    ;;
  api)
    # The inventory API (lab/api/ in the repo), on port 8000 of the management network.
    nohup python3 /srv/api/server.py >/var/log/api.log 2>&1 &
    ;;
esac

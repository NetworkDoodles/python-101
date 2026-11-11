"""The lab's inventory API: a small, read-only REST service that answers like NetBox does.

    GET /api/                    what's here
    GET /api/devices/            every device (?name=r1, ?role=router, ?limit=2&offset=2)
    GET /api/devices/<id>/       one device

Every request needs the token in a header, as NetBox does:  Authorization: Token <token>
The token is in the lab's .env file (LAB_API_TOKEN). The devices are in devices.json, next to this file;
`make break` swaps in another file to add or remove one.
"""
import json
import os
import pathlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

HERE = pathlib.Path(__file__).resolve().parent
TOKEN = os.environ.get("API_TOKEN", "0123456789abcdef0123456789abcdef01234567")
BASE = "http://api:8000"


def load():
    override = pathlib.Path("/run/api/devices.json")       # make break T=8.2 writes this one
    return json.loads((override if override.exists() else HERE / "devices.json").read_text())


def netbox(d):
    """One device, shaped the way NetBox shapes it: nested objects, not flat strings."""
    return {
        "id": d["id"],
        "url": f"{BASE}/api/devices/{d['id']}/",
        "name": d["name"],
        "device_type": {"model": d["model"], "manufacturer": {"name": "Network Doodles", "slug": "network-doodles"}},
        "role": {"name": d["role"].capitalize(), "slug": d["role"]},
        "platform": {"name": d["platform"], "slug": d["platform"]},
        "serial": d.get("serial") or "",
        "site": {"name": d["site"].upper(), "slug": d["site"]},
        "status": {"value": "active", "label": "Active"},
        "primary_ip": {"address": d["ip"], "family": {"value": 4, "label": "IPv4"}},
    }


class Handler(BaseHTTPRequestHandler):
    server_version = "lab-api/1.0"

    def send(self, status, body):
        data = (json.dumps(body, indent=2) + "\n").encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        url = urlparse(self.path)
        path = url.path.rstrip("/") + "/"
        if self.headers.get("Authorization", "") != f"Token {TOKEN}":
            return self.send(403, {"detail": "Invalid token" if self.headers.get("Authorization")
                                   else "Authentication credentials were not provided."})
        if path == "/api/":
            return self.send(200, {"devices": f"{BASE}/api/devices/"})
        devices = [netbox(d) for d in load()]
        if path == "/api/devices/":
            q = parse_qs(url.query)
            for field, get in (("name", lambda d: d["name"]), ("role", lambda d: d["role"]["slug"]),
                               ("platform", lambda d: d["platform"]["slug"])):
                if field in q:
                    devices = [d for d in devices if get(d) in q[field]]
            try:
                limit = int(q.get("limit", ["50"])[0])
                offset = int(q.get("offset", ["0"])[0])
            except ValueError:
                return self.send(400, {"detail": "limit and offset must be whole numbers"})
            page = devices[offset:offset + limit]
            more = offset + limit < len(devices)
            nxt = f"{BASE}/api/devices/?limit={limit}&offset={offset + limit}" if more else None
            prev = f"{BASE}/api/devices/?limit={limit}&offset={max(0, offset - limit)}" if offset else None
            return self.send(200, {"count": len(devices), "next": nxt, "previous": prev, "results": page})
        parts = path.strip("/").split("/")
        if len(parts) == 3 and parts[:2] == ["api", "devices"] and parts[2].isdigit():
            for d in devices:
                if d["id"] == int(parts[2]):
                    return self.send(200, d)
        return self.send(404, {"detail": "Not found."})

    def do_POST(self):
        self.send(405, {"detail": 'Method "POST" not allowed.'})
    do_PUT = do_PATCH = do_DELETE = do_POST

    def log_message(self, fmt, *args):
        print(f"{self.address_string()} {fmt % args}", flush=True)


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()

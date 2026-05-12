#!/usr/bin/env python3
"""Start the Hermes local proxy connector and print the public preview URL."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit


def main() -> int:
    load_env_file(Path.home() / ".hermes" / ".env")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=os.getenv("LOCAL_PROXY_TARGET", "http://127.0.0.1:3020"))
    parser.add_argument("--site", default=os.getenv("HERMES_PROXY_SITE"))
    parser.add_argument("--base-url", default=os.getenv("HERMES_PROXY_BASE_URL") or os.getenv("CLOUD_PROXY_URL"))
    parser.add_argument("--token", default=os.getenv("HERMES_PROXY_TOKEN"))
    parser.add_argument("--repo-dir", default=os.getenv("HERMES_PROXY_REPO_DIR", "/tmp/hermes_proxy"))
    parser.add_argument("--python", default=os.getenv("HERMES_PROXY_PYTHON") or default_python())
    parser.add_argument("--log-file", default=os.getenv("HERMES_PROXY_CONNECTOR_LOG", "/tmp/hermes-local-proxy.log"))
    parser.add_argument("--wait-seconds", type=float, default=float(os.getenv("HERMES_PROXY_WAIT_SECONDS", "8")))
    args = parser.parse_args()

    if not args.base_url:
        raise SystemExit("HERMES_PROXY_BASE_URL or --base-url is required")
    if not args.token:
      raise SystemExit("HERMES_PROXY_TOKEN or --token is required")

    base_url = args.base_url.rstrip("/")
    site_name = args.site or default_site_name(args.target)
    repo_dir = Path(args.repo_dir)
    connector = repo_dir / "proxy-server" / "local_connector.py"
    if not connector.exists():
        raise SystemExit(f"local connector not found: {connector}")

    before = active_tunnel_ids(base_url)
    env = os.environ.copy()
    env.update(
        {
            "CLOUD_PROXY_URL": base_url,
            "HERMES_PROXY_TOKEN": args.token,
            "LOCAL_PROXY_TARGET": args.target.rstrip("/"),
            "HERMES_PROXY_SITE": site_name,
        }
    )
    log_path = Path(args.log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_file = log_path.open("ab")
    process = subprocess.Popen(
        [args.python, str(connector)],
        cwd=str(connector.parent),
        env=env,
        stdin=subprocess.DEVNULL,
        stdout=log_file,
        stderr=subprocess.STDOUT,
        start_new_session=True,
    )

    deadline = time.time() + args.wait_seconds
    tunnels: list[str] = []
    while time.time() < deadline:
        tunnel = find_matching_tunnel(base_url, args.target.rstrip("/"), site_name)
        if tunnel:
            tunnel_id = tunnel["tunnelId"]
            if tunnel_id:
                print(json.dumps(result(base_url, args.target, site_name, process.pid, log_path, tunnel_id), indent=2))
                return 0
        tunnels = active_tunnel_ids(base_url)
        added = [item for item in tunnels if item not in before]
        if added:
            tunnel_id = added[0]
            print(json.dumps(result(base_url, args.target, site_name, process.pid, log_path, tunnel_id), indent=2))
            return 0
        time.sleep(0.5)

    print(
        json.dumps(
            {
                "ok": False,
                "pid": process.pid,
                "target": args.target,
                "site": site_name,
                "baseUrl": base_url,
                "logFile": str(log_path),
                "message": "Connector started, but no tunnel id was visible from /_health yet. Check the dashboard.",
            },
            indent=2,
        )
    )
    return 1


def proxy_health(base_url: str) -> dict[str, object]:
    try:
        with urllib.request.urlopen(f"{base_url.rstrip('/')}/_health", timeout=5) as response:
            return json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        return {}


def active_tunnel_ids(base_url: str) -> list[str]:
    payload = proxy_health(base_url)
    tunnels = payload.get("tunnels", [])
    return [item for item in tunnels if isinstance(item, str)]


def find_matching_tunnel(base_url: str, target: str, site_name: str) -> dict[str, object] | None:
    active = proxy_health(base_url).get("activeTunnels", [])
    if not isinstance(active, list):
        return None
    for item in active:
        if not isinstance(item, dict):
            continue
        if item.get("target") == target and item.get("site") == site_name:
            return item
    return None


def default_python() -> str:
    for candidate in (Path.cwd() / "venv" / "bin" / "python", Path.cwd() / ".venv" / "bin" / "python"):
        if candidate.exists():
            return str(candidate)
    return sys.executable


def load_env_file(path: Path) -> None:
    if not path.exists():
        return
    for raw_line in path.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def default_site_name(target: str) -> str:
    parsed = urlsplit(target)
    host = parsed.hostname or "local"
    port = f"-{parsed.port}" if parsed.port else ""
    return f"{host}{port}".replace(".", "-")


def result(base_url: str, target: str, site_name: str, pid: int, log_path: Path, tunnel_id: str) -> dict[str, object]:
    return {
        "ok": True,
        "pid": pid,
        "target": target,
        "site": site_name,
        "baseUrl": base_url.rstrip("/"),
        "tunnelId": tunnel_id,
        "publicUrl": f"{base_url.rstrip('/')}/p/{tunnel_id}/",
        "logFile": str(log_path),
    }


if __name__ == "__main__":
    raise SystemExit(main())

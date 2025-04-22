import json
import os
import requests
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "mcp_config.json"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def check_http_sse_server(name, env):
    url = env.get("SSE_URL")
    token = env.get("API_ACCESS_TOKEN")
    if not url:
        print(f"[SKIP] {name}: No SSE_URL defined.")
        return
    headers = {"Accept": "text/event-stream"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    print(f"[CHECK] {name}: {url}")
    try:
        resp = requests.get(url, headers=headers, stream=True, timeout=8)
        if resp.status_code == 200:
            print(f"  [OK] Status 200. SSE endpoint reachable.")
        else:
            print(f"  [FAIL] Status {resp.status_code}. Response: {resp.text[:100]}")
    except Exception as e:
        print(f"  [ERROR] Could not connect: {e}")


def main():
    config = load_config()
    servers = config.get("mcpServers", {})
    for name, server_cfg in servers.items():
        env = server_cfg.get("env", {})
        if env.get("SSE_URL"):
            check_http_sse_server(name, env)
        else:
            print(f"[INFO] {name}: No SSE_URL found, cannot check HTTP status (likely a local process or CLI tool).")

if __name__ == "__main__":
    main()

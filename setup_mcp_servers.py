import json
import subprocess
import os
from pathlib import Path

CONFIG_PATH = Path(__file__).parent / "mcp_config.json"


def load_config():
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)


def start_server(name, config):
    if config.get("disabled", False):
        print(f"[SKIP] {name} is disabled.")
        return None
    cmd = [config["command"]]
    if "args" in config:
        cmd += config["args"]
    env = os.environ.copy()
    if "env" in config:
        env.update(config["env"])
    try:
        proc = subprocess.Popen(cmd, env=env)
        print(f"[STARTED] {name}: PID {proc.pid}")
        return proc
    except Exception as e:
        print(f"[ERROR] Failed to start {name}: {e}")
        return None


def main():
    config = load_config()
    servers = config.get("mcpServers", {})
    procs = {}
    for name, server_cfg in servers.items():
        proc = start_server(name, server_cfg)
        if proc:
            procs[name] = proc
    print("\nAll servers attempted to start. Running in background.")
    print("Press Ctrl+C to exit (this will terminate all child processes).")
    try:
        for proc in procs.values():
            proc.wait()
    except KeyboardInterrupt:
        print("\nShutting down all servers...")
        for proc in procs.values():
            proc.terminate()

if __name__ == "__main__":
    main()

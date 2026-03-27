#!/usr/bin/env python3
"""
setup_mcp.py

Finds claude_desktop_config.json and adds or updates a Home Assistant
MCP server entry. Backs up the original file before making changes.

Default server path behavior:
    1) ./server.py from the current working directory where this script runs
    2) server.py in the same folder as this script (fallback)

Usage:
    python setup_mcp.py --ha-token YOUR_TOKEN
    python setup_mcp.py --ha-url http://192.168.1.100:8123 --ha-token abc123
    python setup_mcp.py --script-path C:/repos/homeassistant-mcp/server.py
"""

import argparse
import getpass
import glob
import json
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path


DEFAULT_HA_URL = "http://homeassistant.local:8123"


# ── Config search ─────────────────────────────────────────────────────────────

def find_claude_config() -> Path | None:
    app_data  = os.environ.get("APPDATA", "")
    local     = os.environ.get("LOCALAPPDATA", "")
    user      = os.environ.get("USERPROFILE", str(Path.home()))

    candidates: list[Path] = []

    # Packaged app path (Microsoft Store / WinGet)
    packages_dir = Path(local) / "Packages"
    if packages_dir.exists():
        for pkg in packages_dir.glob("Claude_*"):
            candidates.append(pkg / "LocalCache" / "Roaming" / "Claude" / "claude_desktop_config.json")

    # Classic AppData paths
    candidates += [
        Path(app_data)  / "Claude"           / "claude_desktop_config.json",
        Path(app_data)  / "Anthropic" / "Claude" / "claude_desktop_config.json",
        Path(local)     / "Claude"           / "claude_desktop_config.json",
        Path(local)     / "Anthropic" / "Claude" / "claude_desktop_config.json",
    ]

    # macOS paths
    home = Path.home()
    candidates += [
        home / "Library" / "Application Support" / "Claude" / "claude_desktop_config.json",
        home / "Library" / "Application Support" / "Anthropic" / "Claude" / "claude_desktop_config.json",
    ]

    for path in candidates:
        if path.exists():
            return path

    # Last resort: recursive search
    print("Searching for claude_desktop_config.json...", flush=True)
    search_roots = [p for p in [app_data, local, str(home / "Library" / "Application Support")] if p]
    for root in search_roots:
        for match in glob.iglob(f"{root}/**/claude_desktop_config.json", recursive=True):
            return Path(match)

    return None


# ── Helpers ───────────────────────────────────────────────────────────────────

def backup(config_path: Path) -> Path:
    stamp   = datetime.now().strftime("%Y%m%d_%H%M%S")
    dest    = config_path.with_suffix(f".bak_{stamp}")
    shutil.copy2(config_path, dest)
    return dest


def load_config(config_path: Path) -> dict:
    text = config_path.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        print(f"ERROR: Could not parse existing config as JSON: {e}", file=sys.stderr)
        sys.exit(1)


def write_config(config_path: Path, data: dict) -> None:
    config_path.write_text(json.dumps(data, indent=2), encoding="utf-8")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    cwd_server = Path.cwd() / "server.py"
    script_dir_server = Path(__file__).resolve().parent / "server.py"
    default_script = str(cwd_server if cwd_server.exists() else script_dir_server)

    parser = argparse.ArgumentParser(
        description=(
            "Add or update a Home Assistant MCP server entry in "
            "claude_desktop_config.json"
        )
    )
    parser.add_argument(
        "--ha-url",
        default=DEFAULT_HA_URL,
        help=f"Home Assistant base URL (default: {DEFAULT_HA_URL})",
    )
    parser.add_argument("--ha-token",    default="",
                        help="Long-Lived Access Token (prompted if omitted)")
    parser.add_argument(
        "--script-path",
        default=default_script,
        help=(
            "Full path to server.py "
            f"(default: {default_script}; prefers current working directory)"
        ),
    )
    parser.add_argument("--server-name", default="homeassistant",
                        help="Key name for this MCP server entry (default: homeassistant)")
    parser.add_argument("--dry-run",     action="store_true",
                        help="Preview changes without writing to disk")
    args = parser.parse_args()

    # ── Find config
    config_path = find_claude_config()
    if not config_path:
        print("ERROR: Could not locate claude_desktop_config.json. Is Claude Desktop installed?",
              file=sys.stderr)
        sys.exit(1)
    print(f"Found config: {config_path}")

    # ── Validate token
    ha_token = args.ha_token
    if not ha_token:
        ha_token = getpass.getpass("Enter your Home Assistant Long-Lived Access Token: ")
    if not ha_token:
        print("ERROR: HA token is required.", file=sys.stderr)
        sys.exit(1)

    # ── Validate script path
    script_path = Path(args.script_path)
    if not script_path.exists():
        print(f"WARNING: server.py not found at: {script_path}")
        override = input("Enter the full path to server.py: ").strip()
        script_path = Path(override)
        if not script_path.exists():
            print(f"ERROR: server.py still not found at: {script_path}", file=sys.stderr)
            sys.exit(1)

    # ── Load existing config
    config = load_config(config_path)

    # ── Build MCP entry
    mcp_entry = {
        "command": "python",
        "args":    [str(script_path)],
        "env": {
            "HA_URL":   args.ha_url,
            "HA_TOKEN": ha_token,
        }
    }

    # ── Merge into config
    if "mcpServers" not in config:
        config["mcpServers"] = {}

    action = "Updating existing" if args.server_name in config["mcpServers"] else "Adding new"
    print(f"{action} '{args.server_name}' MCP entry...")
    config["mcpServers"][args.server_name] = mcp_entry

    # ── Write or preview
    if args.dry_run:
        print("\n[DRY RUN] Would write the following config:\n")
        print(json.dumps(config, indent=2))
    else:
        bak = backup(config_path)
        print(f"Backup saved: {bak}")
        write_config(config_path, config)
        print("Config updated successfully.")

    # ── Summary
    print()
    print("━" * 44)
    print(f"  MCP Server : {args.server_name}")
    print(f"  HA URL     : {args.ha_url}")
    print(f"  Script     : {script_path}")
    print(f"  Config     : {config_path}")
    print("━" * 44)
    if not args.dry_run:
        print("\nRestart Claude Desktop to load the new MCP server.")


if __name__ == "__main__":
    main()

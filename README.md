# Home Assistant MCP Server

MCP server that connects Claude to a local Home Assistant instance via the REST API.

## Overview

This server exposes 12 tools covering the full Home Assistant REST API surface: reading and controlling entities, calling services, managing climate devices, querying history, firing events, and rendering Jinja2 templates. It runs as a local stdio subprocess, so no ports are opened and no cloud relay is required. Authentication uses a standard Home Assistant long-lived access token passed via environment variable.

## Tools

| Tool | Description |
|---|---|
| `ha_get_config` | Returns HA version, location name, timezone, unit system, and installed components |
| `ha_list_entities` | Lists entities with current state, filterable by domain or name search |
| `ha_get_state` | Returns full state and all attributes for a specific entity |
| `ha_turn_on` | Turns on a light or switch, with optional brightness, color temp, RGB color, and transition |
| `ha_turn_off` | Turns off any entity that supports homeassistant.turn_off |
| `ha_toggle` | Toggles any entity between on and off |
| `ha_set_temperature` | Sets target temperature and optional HVAC mode on a climate entity |
| `ha_call_service` | Calls any HA service with arbitrary data — covers media players, covers, notifications, and more |
| `ha_list_services` | Lists available services and their fields by domain |
| `ha_get_history` | Returns state change history for an entity over a configurable window up to 7 days |
| `ha_fire_event` | Fires a custom HA event with an optional data payload |
| `ha_render_template` | Renders a Jinja2 template against live HA state and returns the result |

## Repository Structure

```
homeassistant-mcp/
|-- ha_mcp_server.py    # MCP server — all 12 tools, FastMCP + httpx
|-- HA_MCP_SETUP.md     # Installation and configuration guide
|-- README.md
```

## Prerequisites

- Python 3.10+
- Home Assistant running on your local network
- Claude desktop app (Cowork mode) or any MCP-compatible client

## Installation

**1. Install dependencies**

```bash
pip3 install mcp httpx pydantic
```

**2. Get a Home Assistant long-lived access token**

In Home Assistant: Profile (bottom-left) → Long-Lived Access Tokens → Create Token. Copy the token — it is only shown once.

**3. Add the server to your Claude MCP config**

Open `~/Library/Application Support/Claude/claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "python3",
      "args": ["/absolute/path/to/ha_mcp_server.py"],
      "env": {
        "HA_URL": "http://homeassistant.local:8123",
        "HA_TOKEN": "your_token_here"
      }
    }
  }
}
```

Replace `HA_URL` with your HA address and `HA_TOKEN` with the token from step 2.

**4. Restart Claude**

The 12 HA tools will appear automatically on next launch.

## Environment Variables

| Variable | Required | Example | Description |
|---|---|---|---|
| `HA_TOKEN` | Yes | `eyJ0...` | Long-lived access token from your HA profile |
| `HA_URL` | No | `http://192.168.1.100:8123` | Base URL of your HA instance (default: `http://homeassistant.local:8123`) |

## Usage

Once connected, Claude can control your Home Assistant instance in natural language:

```
Turn off all the lights
Dim the bedroom lights to 30%
Set the thermostat to 72 in heat mode
What has the outdoor temperature been doing over the last 6 hours?
Trigger the morning routine automation
Send a notification to my phone that the garage door is open
How many lights are currently on?
```

For services not covered by the convenience tools, `ha_call_service` handles anything in your HA instance:

```
Play a radio stream on the kitchen media player
Open the garage door cover
Run the vacuum in the living room
```

## Security Notes

- Store `HA_TOKEN` in your Claude config or environment only — never commit it to the repository
- Add `claude_desktop_config.json` and `.env` to `.gitignore`
- The server binds to stdio only and does not open any network ports on the host machine

## Common Errors

| Problem | Likely Cause | Fix |
|---|---|---|
| "Cannot reach Home Assistant" | Mac and HA on different networks, or wrong URL | Try the IP address instead of `homeassistant.local` |
| "Unauthorized" | Token invalid, expired, or copied incorrectly | Create a new token in HA Profile |
| Server not appearing in Claude | Invalid JSON in config, or wrong file path | Validate the JSON and use an absolute path to `ha_mcp_server.py` |
| "Module not found" | Dependencies not installed for the Python Claude calls | Run `pip3 install mcp httpx pydantic` with the same Python binary |

## Blog

Technical posts about automation and home lab work at [mickitblog.blogspot.com](https://mickitblog.blogspot.com).

## Related Repositories

| Repo | Description |
|---|---|
| [mickpletcher/Anthropic](https://github.com/mickpletcher/Anthropic) | Claude skills library for Cowork mode |
| [mickpletcher/PiHole](https://github.com/mickpletcher/PiHole) | Curated Pi-hole blocklist repository |

## License

This project is licensed under the MIT License. See `LICENSE` for the full text.

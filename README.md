# Home Assistant MCP Server

Connects Claude to your Home Assistant instance via the REST API.

## Tools

| Tool | What it does |
|---|---|
| `ha_get_config` | HA server info (version, location, units) |
| `ha_list_states` | All entity states, filterable by domain |
| `ha_get_state` | Single entity state + attributes |
| `ha_call_service` | Call any HA service (lights, switches, climate, locks…) |
| `ha_list_services` | Browse available services by domain |
| `ha_trigger_automation` | Manually fire an automation |
| `ha_get_history` | State history for an entity (up to 7 days) |
| `ha_render_template` | Evaluate a Jinja2 template |
| `ha_check_config` | Validate configuration.yaml |

## Setup

### 1. Get a Long-Lived Access Token

Log into Home Assistant → Profile → Long-Lived Access Tokens → Create token.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

```bash one-liner
pip install "mcp[cli]>=1.0.0" "httpx>=0.27.0" "pydantic>=2.0.0"
```
### 3. Set environment variables

```bash
export HA_URL="http://homeassistant.local:8123"   # or your LAN IP
export HA_TOKEN="your_long_lived_token_here"
```

For Proxmox LXC deployments, add these to `/etc/environment` or your
systemd service file so they persist across restarts.

### 4. Run (stdio mode — default)

```bash
python server.py
```

### 5. Run (HTTP mode — for remote Claude clients)

Edit the bottom of `server.py`:

```python
mcp.run(transport="streamable_http", port=8001)
```

Then start it and expose via Cloudflare Tunnel or your existing reverse proxy.

---

## Claude Desktop config (`claude_desktop_config.json`)

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "python",
      "args": ["/path/to/homeassistant_mcp/server.py"],
      "env": {
        "HA_URL": "http://homeassistant.local:8123",
        "HA_TOKEN": "your_token_here"
      }
    }
  }
}
```

On Windows, use the full Python path:
```json
"command": "C:\\Python312\\python.exe"
```

---

## Proxmox LXC systemd service

```ini
[Unit]
Description=Home Assistant MCP Server
After=network.target

[Service]
Type=simple
User=mick
WorkingDirectory=/opt/homeassistant_mcp
ExecStart=/usr/bin/python3 server.py
Environment=HA_URL=http://homeassistant.local:8123
Environment=HA_TOKEN=your_token_here
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Save to `/etc/systemd/system/ha-mcp.service`, then:

```bash
systemctl daemon-reload
systemctl enable --now ha-mcp
```

---

## Example prompts once connected

- "Turn off all the lights in the living room"
- "What's the current temperature on sensor.outdoor_temp?"
- "Set the thermostat to 70 degrees"
- "Show me the history of the front door sensor for the last 6 hours"
- "Trigger the morning routine automation"
- "Which lights are currently on?"

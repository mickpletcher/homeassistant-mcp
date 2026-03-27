# Home Assistant MCP Server

Connect Claude Desktop to Home Assistant through the Home Assistant REST API.

This project includes:

1. An MCP server in Python.
2. A Python setup helper that updates Claude Desktop MCP config.
3. A PowerShell setup helper that does the same.

## What You Can Do

| Tool | Description |
|---|---|
| `ha_get_config` | Get Home Assistant server details such as version, location, and units. |
| `ha_list_states` | List entity states, optionally filtered by domain. |
| `ha_get_state` | Get state and attributes for one entity. |
| `ha_call_service` | Call any Home Assistant service. |
| `ha_list_services` | List service definitions, optionally filtered by domain. |
| `ha_trigger_automation` | Trigger an automation by entity id. |
| `ha_get_history` | Get state history for an entity from 1 to 168 hours. |
| `ha_render_template` | Render Jinja2 templates through Home Assistant. |
| `ha_check_config` | Run Home Assistant configuration check. |

## Requirements

1. Python 3.10 or newer.
2. Home Assistant reachable from your machine.
3. A Home Assistant Long Lived Access Token.
4. Claude Desktop installed.

Install dependencies:

**bash**
```
pip install -r requirements.txt
```
OR 
**bash one-liner**
```
pip install "mcp[cli]>=1.0.0" "httpx>=0.27.0" "pydantic>=2.0.0"
```

## Get Your Token

In Home Assistant:

1. Open Profile.
2. Go to Long Lived Access Tokens.
3. Create a token and copy it.

## Configure Claude Desktop Automatically

You can use either helper script.

### Option A: Python helper

Script: `setup_mcp.py`

```bash
python setup_mcp.py --ha-token YOUR_TOKEN
```

Override Home Assistant URL:

```bash
python setup_mcp.py --ha-url http://192.168.1.100:8123 --ha-token YOUR_TOKEN
```

Preview changes without writing:

```bash
python setup_mcp.py --ha-token YOUR_TOKEN --dry-run
```

### Option B: PowerShell helper

Script: `Set-ClaudeMcp.ps1`

```powershell
.\Set-ClaudeMcp.ps1 -HaToken "YOUR_TOKEN"
```

Override Home Assistant URL:

```powershell
.\Set-ClaudeMcp.ps1 -HaUrl "http://192.168.1.100:8123" -HaToken "YOUR_TOKEN"
```

Preview changes without writing:

```powershell
.\Set-ClaudeMcp.ps1 -HaToken "YOUR_TOKEN" -WhatIf
```

### Defaults and Path Resolution

Both setup scripts now use the same defaults:

1. `HA_URL` default is `http://homeassistant.local:8123`.
2. MCP server name default is `homeassistant`.
3. Script path selection order:
   1. `./server.py` from the current working directory where setup is executed.
   2. `server.py` in the same directory as the setup script.
4. If `server.py` is still not found, you are prompted for a full path.
5. Existing Claude config is backed up before write.

## Common Parameters

Python setup helper:

1. `--ha-url` override Home Assistant URL.
2. `--ha-token` pass token directly.
3. `--script-path` override detected server path.
4. `--server-name` set MCP server key in config.
5. `--dry-run` preview only.

PowerShell setup helper:

1. `-HaUrl` override Home Assistant URL.
2. `-HaToken` pass token directly.
3. `-ServerScriptPath` override detected server path.
4. `-McpServerName` set MCP server key in config.
5. `-WhatIf` preview only.

## Manual Claude Desktop Configuration

If you prefer to update Claude Desktop config manually:

```json
{
  "mcpServers": {
    "homeassistant": {
      "command": "python",
      "args": ["C:/path/to/homeassistant-mcp/server.py"],
      "env": {
        "HA_URL": "http://homeassistant.local:8123",
        "HA_TOKEN": "your_long_lived_token_here"
      }
    }
  }
}
```

On Windows, using a full Python executable path is also valid:

```json
"command": "C:\\Python312\\python.exe"
```

## Run The MCP Server Directly

Set environment variables first.

Bash:

```bash
export HA_URL="http://homeassistant.local:8123"
export HA_TOKEN="your_long_lived_token_here"
```

PowerShell:

```powershell
$env:HA_URL = "http://homeassistant.local:8123"
$env:HA_TOKEN = "your_long_lived_token_here"
```

Then run:

```bash
python server.py
```

## Optional HTTP Transport Mode

Default mode is stdio, which is what Claude Desktop expects.

If you need streamable HTTP transport, change the entry point in `server.py`:

```python
mcp.run(transport="streamable_http", port=8001)
```

Then expose it through your preferred reverse proxy or tunnel.

## Troubleshooting

1. Unauthorized 401:
   1. Regenerate a Home Assistant Long Lived Access Token.
   2. Make sure token value has no extra spaces.
2. Connection refused:
   1. Verify `HA_URL` points to a reachable host.
   2. Confirm Home Assistant is running on that address and port.
3. Server script not found:
   1. Run setup from repo root so `./server.py` resolves.
   2. Pass explicit path with `--script-path` or `-ServerScriptPath`.
4. Claude does not show the server:
   1. Restart Claude Desktop after setup.
   2. Confirm the config file includes `mcpServers.homeassistant`.

## Security Notes

1. Treat Home Assistant token as a secret.
2. Do not commit tokens to source control.
3. Prefer local environment variables or local config only.

## Example Prompts

1. Turn off all lights in the living room.
2. What is the current state of `sensor.outdoor_temp`.
3. Set thermostat to 70.
4. Show front door sensor history for the last 6 hours.
5. Trigger morning routine automation.

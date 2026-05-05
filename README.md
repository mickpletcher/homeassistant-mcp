# Home Assistant MCP Server

This project lets Claude Desktop talk to your Home Assistant system.

After setup, you can ask Claude things like:

```text
What lights are on?
Turn off the kitchen light.
Set the thermostat to 72.
Show me the outdoor temperature history.
Run my morning automation if it is allowed by my safety settings.
```

Claude does this by using Home Assistant's local API. Nothing in this project opens a public web server.

See [changelog.md](changelog.md) for project changes.

## Who This Is For

Use this if:

- You use Home Assistant.
- You use Claude Desktop or another app that supports MCP.
- You want Claude to read or control your smart home devices.

This works on:

- macOS
- Windows 11

## What You Need

Before you start, you need:

- Home Assistant already running.
- Python 3 installed.
- Claude Desktop installed.
- A Home Assistant long-lived access token.

If you do not know whether Python is installed, the setup steps below will help you check.

## Important Safety Note

Claude may be able to control real devices in your home, depending on what you ask it to do and what permissions your Home Assistant token has.

This project blocks sensitive actions by default.

Be careful with devices like:

- Door locks
- Garage doors
- Alarms
- Climate controls
- Heaters
- Ovens
- Irrigation systems
- Any automation that changes your home state

Use a Home Assistant token from an account with only the permissions you are comfortable giving Claude.

Sensitive actions can be allowed later, but you should only allow devices you understand and trust.

## Step 1: Download This Project

Download or clone this project to your computer.

For example, you might put it here:

macOS:

```text
/Users/yourname/homeassistant-mcp
```

Windows:

```text
C:\Users\yourname\homeassistant-mcp
```

## Step 2: Install Python Dependencies

Open a terminal in the project folder.

On macOS, use Terminal and run:

```bash
python3 -m pip install -r requirements.txt
```

On Windows 11, use PowerShell and run:

```powershell
py -3 -m pip install -r requirements.txt
```

If this step says Python is missing, install Python 3 from [python.org](https://www.python.org/downloads/) and try again.

## Step 3: Create a Home Assistant Token

In Home Assistant:

1. Open your user profile.
2. Scroll to **Long-Lived Access Tokens**.
3. Create a new token.
4. Name it something clear, like `Claude MCP`.
5. Copy the token.

You will only see the token once, so save it somewhere private until setup is complete.

Do not commit this token to GitHub. Do not share it publicly.

## Step 4: Connect It To Claude Desktop

The easiest way is to use the setup script.

### macOS

In Terminal, from this project folder, run:

```bash
python3 setup_mcp.py --ha-url http://homeassistant.local:8123 --ha-token YOUR_TOKEN_HERE
```

Replace `YOUR_TOKEN_HERE` with the token you copied from Home Assistant.

If your Home Assistant does not use `homeassistant.local`, use its IP address instead:

```bash
python3 setup_mcp.py --ha-url http://192.168.1.100:8123 --ha-token YOUR_TOKEN_HERE
```

To allow one sensitive device, add `--allowed-sensitive-entities`.

Example:

```bash
python3 setup_mcp.py --ha-url http://homeassistant.local:8123 --ha-token YOUR_TOKEN_HERE --allowed-sensitive-entities lock.front_door
```

### Windows 11

In PowerShell, from this project folder, run:

```powershell
py -3 setup_mcp.py --ha-url http://homeassistant.local:8123 --ha-token YOUR_TOKEN_HERE
```

Replace `YOUR_TOKEN_HERE` with the token you copied from Home Assistant.

If your Home Assistant does not use `homeassistant.local`, use its IP address instead:

```powershell
py -3 setup_mcp.py --ha-url http://192.168.1.100:8123 --ha-token YOUR_TOKEN_HERE
```

To allow one sensitive device, add `--allowed-sensitive-entities`.

Example:

```powershell
py -3 setup_mcp.py --ha-url http://homeassistant.local:8123 --ha-token YOUR_TOKEN_HERE --allowed-sensitive-entities lock.front_door
```

### Windows Alternative

Windows users can also use the included PowerShell script:

```powershell
.\Set-ClaudeMcp.ps1 -HaUrl "http://homeassistant.local:8123" -HaToken "YOUR_TOKEN_HERE"
```

To allow one sensitive device with the PowerShell helper:

```powershell
.\Set-ClaudeMcp.ps1 -HaUrl "http://homeassistant.local:8123" -HaToken "YOUR_TOKEN_HERE" -AllowedSensitiveEntities "lock.front_door"
```

## Step 5: Restart Claude Desktop

Close Claude Desktop completely, then open it again.

After restarting, Claude should be able to use the Home Assistant tools.

## What Tools Are Included

Claude gets tools that can:

- Read your Home Assistant configuration.
- List devices and entity states.
- Check the state of one device or sensor.
- Turn devices on, off, or toggle them.
- Set a thermostat or climate device temperature.
- Lock and unlock supported lock devices.
- Open and close supported covers, such as shades, blinds, curtains, or garage doors.
- Call Home Assistant services.
- List available Home Assistant services.
- Trigger automations.
- Read recent history for one entity.
- Render Home Assistant templates.
- Ask Home Assistant to check its configuration.

In normal use, you do not need to call these tools by name. You can usually ask Claude in plain English.

## Safety Settings

Sensitive actions are blocked unless you explicitly allow them.

Blocked by default:

- Alarms
- Automations
- Climate devices
- Covers, such as garage doors, shades, blinds, and curtains
- Door locks
- Humidifiers
- Scripts
- Sirens
- Valves
- Water heaters

You can allow sensitive actions in three ways:

| Setting | What It Does |
|---|---|
| `HA_ALLOW_SENSITIVE_ACTIONS=true` | Allows all sensitive actions |
| `HA_ALLOWED_SENSITIVE_DOMAINS=climate,cover` | Allows whole sensitive device groups |
| `HA_ALLOWED_SENSITIVE_ENTITIES=lock.front_door` | Allows only listed sensitive devices |
| `HA_SENSITIVE_DOMAINS=lock,cover,climate` | Replaces the default sensitive device group list |

You can also block devices even if they would otherwise be allowed:

| Setting | What It Does |
|---|---|
| `HA_DENIED_DOMAINS=lock` | Always blocks a whole device group |
| `HA_DENIED_ENTITIES=lock.front_door,switch.oven_*` | Always blocks listed devices or wildcard patterns |

For most users, the safest choice is to allow individual entities only.

Example:

```text
HA_ALLOWED_SENSITIVE_ENTITIES=climate.hallway,cover.living_room_shades
```

## Common Problems

### Claude cannot reach Home Assistant

Try using the IP address instead of `homeassistant.local`.

Example:

```text
http://192.168.1.100:8123
```

### Claude says unauthorized

Your token may be wrong, expired, or copied incorrectly.

Create a new long-lived access token in Home Assistant and run the setup again.

### Claude does not show the Home Assistant tools

Try these steps:

1. Restart Claude Desktop.
2. Make sure you ran the setup command from this project folder.
3. Make sure the Python dependency install step finished successfully.
4. Run the setup command again.

### A Python module is missing

The dependencies may have been installed into a different Python installation.

Run the dependency install command again from this project folder:

macOS:

```bash
python3 -m pip install -r requirements.txt
```

Windows:

```powershell
py -3 -m pip install -r requirements.txt
```

## Files In This Project

| File | What It Does |
|---|---|
| `server.py` | The actual Home Assistant MCP server |
| `setup_mcp.py` | Setup helper for macOS and Windows |
| `Set-ClaudeMcp.ps1` | Windows PowerShell setup helper |
| `requirements.txt` | Python packages this project needs |
| `README.md` | This guide |

## For Advanced Users

The setup script edits Claude Desktop's MCP configuration file and creates a backup before saving changes.

The MCP server entry points Claude to `server.py` and passes these environment variables:

| Variable | Meaning |
|---|---|
| `HA_URL` | Your Home Assistant address |
| `HA_TOKEN` | Your Home Assistant long-lived access token |
| `HA_ALLOW_SENSITIVE_ACTIONS` | Allows all sensitive actions when set to `true` |
| `HA_SENSITIVE_DOMAINS` | Custom list of domains treated as sensitive |
| `HA_ALLOWED_SENSITIVE_DOMAINS` | Sensitive domains allowed by name |
| `HA_ALLOWED_SENSITIVE_ENTITIES` | Sensitive entities allowed by name or wildcard pattern |
| `HA_DENIED_DOMAINS` | Domains that are always blocked |
| `HA_DENIED_ENTITIES` | Entities or wildcard patterns that are always blocked |

You can edit Claude Desktop's MCP config manually if you prefer, but most users should use the setup script.

## License

This project is licensed under the MIT License. See `LICENSE` for details.

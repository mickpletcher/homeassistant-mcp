# Future Upgrades

This file tracks completed and possible improvements for the Home Assistant MCP Server, grouped by priority and complexity.

## Completed Upgrades

These upgrades have already been implemented.

### Friendly Shortcut Tools

Status: Implemented.

Implemented tools:

- `ha_turn_on`
- `ha_turn_off`
- `ha_toggle`
- `ha_set_temperature`
- `ha_lock`
- `ha_unlock`
- `ha_open_cover`
- `ha_close_cover`

What this improved:

- Claude can choose clearer, purpose-built tools for common actions.
- Users do not need to rely only on the generic `ha_call_service` tool.
- Climate, lock, and cover tools now include basic domain checks to catch obvious wrong-entity mistakes.

### Safety Guardrails

Status: Implemented.

Implemented settings:

- `HA_ALLOW_SENSITIVE_ACTIONS`
- `HA_SENSITIVE_DOMAINS`
- `HA_ALLOWED_SENSITIVE_DOMAINS`
- `HA_ALLOWED_SENSITIVE_ENTITIES`
- `HA_DENIED_DOMAINS`
- `HA_DENIED_ENTITIES`

What this improved:

- Sensitive domains are blocked by default.
- Users can explicitly allow all sensitive actions, selected sensitive domains, or selected sensitive entities.
- Users can always block specific domains, entities, or wildcard entity patterns.
- The setup helpers can write these safety settings into Claude Desktop's MCP config.

## Tier 1: Best Next Upgrades

These upgrades would make the project safer and easier to use for most people.

### 1. Add Read-Only Mode

Add an environment variable that disables all write/control actions.

Example:

```text
HA_READ_ONLY=true
```

In read-only mode, Claude could still:

- Read states.
- List services.
- View history.
- Render templates.
- Check configuration.

But Claude could not:

- Turn devices on or off.
- Trigger automations.
- Call Home Assistant services that change device state.

Why this matters:

- Some users may only want Claude to inspect Home Assistant.
- It gives cautious users a safer first setup.

## Tier 2: Usability Improvements

These upgrades would make the server feel more natural and helpful.

### 2. Add Room And Area Awareness

Use Home Assistant areas so Claude can understand rooms.

Example user requests:

```text
Turn off everything in the living room.
What devices are in the bedroom?
Are any windows open upstairs?
```

Possible tools:

- `ha_list_areas`
- `ha_list_entities_by_area`
- `ha_get_area_state`

Why this matters:

- People think in rooms, not entity IDs.
- It makes smart home control feel more natural.

### 3. Improve Entity Search

Add a tool that helps Claude find entities by friendly name, area, domain, or device class.

Possible searches:

- Friendly name, like `Kitchen Light`
- Entity ID, like `light.kitchen_ceiling`
- Domain, like `light`, `switch`, or `sensor`
- Area, like `Living Room`
- Device class, like `temperature`, `motion`, or `door`

Why this matters:

- Home Assistant entity IDs can be hard to remember.
- Better search makes Claude less likely to choose the wrong device.

### 4. Add Example Prompts

Add a user-friendly section to the README with examples.

Possible examples:

```text
What lights are currently on?
Turn off all lights downstairs.
What was the lowest outdoor temperature overnight?
Is any door or window open?
Run the bedtime automation.
Show me unavailable devices.
```

Why this matters:

- New users can understand the project faster.
- It makes the first successful use easier.

## Tier 3: Setup And Reliability

These upgrades would make installation and troubleshooting smoother.

### 5. Add A Guided Setup Wizard

Create a setup flow that checks each requirement and explains what to do next.

The wizard could:

- Check Python version.
- Install dependencies.
- Ask for the Home Assistant URL.
- Ask for the Home Assistant token.
- Test the Home Assistant connection.
- Validate the token.
- Find Claude Desktop config.
- Update Claude Desktop config.
- Confirm the final setup.

Why this matters:

- Non-technical users need fewer manual steps.
- Setup problems become easier to diagnose.

### 6. Add A Connection Test

Add a simple test command or tool that verifies Home Assistant access.

Possible checks:

- Home Assistant URL is reachable.
- Token is valid.
- REST API responds correctly.
- Current Home Assistant version can be read.

Possible tool or command:

- `ha_ping`
- `python setup_mcp.py --test`

Why this matters:

- Users can quickly tell whether the problem is Python, Claude, the token, or Home Assistant.

### 7. Add Automated Tests

Add tests that mock Home Assistant API responses.

Things to test:

- URL building.
- Headers and token handling.
- Read-only mode behavior.
- Friendly shortcut tools.
- Error handling.
- History parsing.
- Template rendering responses.

Why this matters:

- The project becomes safer to change.
- Bugs are easier to catch before release.

## Tier 4: Packaging And Distribution

These upgrades would make the project easier to install and share.

### 8. Package It For Pip

Make the project installable with:

```bash
pip install homeassistant-mcp
```

Why this matters:

- Users would not need to manually manage files as much.
- Setup instructions become shorter.
- Updates become easier.

### 9. Add Versioned Releases

Publish releases with clear version numbers and notes.

Possible release notes:

- New tools added.
- Safety behavior changed.
- Setup improvements.
- Bug fixes.

Why this matters:

- Users can tell what changed.
- Troubleshooting becomes easier.

## Suggested Roadmap

Recommended order:

1. Add read-only mode.
2. Add connection testing.
3. Add entity search.
4. Add room and area awareness.
5. Add example prompts.
6. Add automated tests.
7. Add guided setup.
8. Package for pip.
9. Add versioned releases.

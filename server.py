"""
Home Assistant MCP Server
Connects Claude to a Home Assistant instance via the REST API.

Authentication:
  Set HA_URL and HA_TOKEN environment variables, or pass them at runtime.
  Generate a Long-Lived Access Token at: http://<HA_HOST>:8123/profile
"""

from __future__ import annotations

import json
import os
from typing import Any, Optional

import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, ConfigDict, Field

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────

HA_URL   = os.getenv("HA_URL", "http://homeassistant.local:8123")
HA_TOKEN = os.getenv("HA_TOKEN", "")

TIMEOUT = 15.0  # seconds

# ── MCP server ────────────────────────────────────────────────────────────────

mcp = FastMCP("homeassistant_mcp")

# ── Shared HTTP client helpers ────────────────────────────────────────────────

def _headers() -> dict[str, str]:
    """Return Authorization and Content-Type headers for HA API requests."""
    return {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }


def _url(path: str) -> str:
    """Build a full HA REST API URL from a relative path."""
    base = HA_URL.rstrip("/")
    return f"{base}/api/{path.lstrip('/')}"


async def _get(path: str, params: dict | None = None) -> Any:
    """Send an authenticated GET request to the HA API and return parsed JSON."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.get(_url(path), headers=_headers(), params=params)
        r.raise_for_status()
        return r.json()


async def _post(path: str, body: dict | None = None) -> Any:
    """Send an authenticated POST request to the HA API and return parsed JSON."""
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(_url(path), headers=_headers(), json=body or {})
        r.raise_for_status()
        try:
            return r.json()
        except Exception:
            return {"message": r.text}


def _handle_error(e: Exception) -> str:
    """Translate httpx exceptions into human-readable error strings."""
    if isinstance(e, httpx.HTTPStatusError):
        code = e.response.status_code
        if code == 401:
            return "Error 401: Unauthorized. Verify HA_TOKEN is set correctly."
        if code == 404:
            return "Error 404: Not found. Check the entity_id or service name."
        return f"Error {code}: {e.response.text}"
    if isinstance(e, httpx.ConnectError):
        return f"Connection refused. Verify HA_URL ({HA_URL}) is reachable."
    if isinstance(e, httpx.TimeoutException):
        return "Request timed out. Home Assistant may be under load."
    return f"Unexpected error: {type(e).__name__}: {e}"


# ── Pydantic input models ─────────────────────────────────────────────────────

class EntityInput(BaseModel):
    """Input model for tools that target a single entity."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    entity_id: str = Field(..., description="Entity ID, e.g. 'light.living_room'")


class DomainFilter(BaseModel):
    """Input model for tools that accept an optional domain filter."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    domain: Optional[str] = Field(
        default=None,
        description="Filter by domain, e.g. 'light', 'switch', 'sensor'. Omit for all entities."
    )


class CallServiceInput(BaseModel):
    """Input model for calling a Home Assistant service."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    domain: str = Field(..., description="Service domain, e.g. 'light', 'switch', 'climate'")
    service: str = Field(..., description="Service name, e.g. 'turn_on', 'turn_off', 'toggle'")
    entity_id: Optional[str] = Field(
        default=None,
        description="Target entity ID. Omit if service doesn't require one."
    )
    service_data: Optional[dict] = Field(
        default=None,
        description="Extra service data, e.g. {\"brightness\": 128, \"color_temp\": 300}"
    )


class AutomationInput(BaseModel):
    """Input model for automation trigger tools."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    automation_id: str = Field(..., description="Entity ID of the automation, e.g. 'automation.morning_lights'")


class HistoryInput(BaseModel):
    """Input model for entity history queries."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    entity_id: str = Field(..., description="Entity ID to query history for")
    hours: int = Field(default=24, ge=1, le=168, description="How many hours back to fetch (1–168)")


class TemplateInput(BaseModel):
    """Input model for Jinja2 template rendering."""

    model_config = ConfigDict(str_strip_whitespace=True, extra="forbid")
    template: str = Field(..., description="Jinja2 template string to render, e.g. \"{{ states('sensor.temperature') }}\"")


# ── Tools ─────────────────────────────────────────────────────────────────────

@mcp.tool(
    name="ha_get_config",
    annotations={"title": "Get HA Configuration", "readOnlyHint": True, "destructiveHint": False}
)
async def ha_get_config() -> str:
    """Return the current Home Assistant configuration (location, version, components, unit system)."""
    try:
        data = await _get("/")
        return json.dumps(data, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="ha_list_states",
    annotations={"title": "List Entity States", "readOnlyHint": True, "destructiveHint": False}
)
async def ha_list_states(params: DomainFilter) -> str:
    """
    Return all entity states, optionally filtered by domain.

    Args:
        params.domain: Optional domain filter ('light', 'switch', 'sensor', etc.)

    Returns:
        JSON array of entity objects with entity_id, state, and attributes.
    """
    try:
        states: list = await _get("states")
        if params.domain:
            states = [s for s in states if s["entity_id"].startswith(f"{params.domain}.")]
        # Trim verbose attributes to keep payload manageable
        trimmed = [
            {
                "entity_id": s["entity_id"],
                "state": s["state"],
                "attributes": s.get("attributes", {}),
                "last_changed": s.get("last_changed"),
            }
            for s in states
        ]
        return json.dumps(trimmed, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="ha_get_state",
    annotations={"title": "Get Entity State", "readOnlyHint": True, "destructiveHint": False}
)
async def ha_get_state(params: EntityInput) -> str:
    """
    Return the current state and attributes of a single entity.

    Args:
        params.entity_id: e.g. 'light.living_room', 'sensor.outdoor_temp'

    Returns:
        JSON object with state, attributes, last_changed, last_updated.
    """
    try:
        data = await _get(f"states/{params.entity_id}")
        return json.dumps(data, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="ha_call_service",
    annotations={
        "title": "Call HA Service",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
    }
)
async def ha_call_service(params: CallServiceInput) -> str:
    """
    Call any Home Assistant service (e.g. turn on/off lights, lock doors, set thermostat).

    Common examples:
      - Turn on a light:   domain=light, service=turn_on, entity_id=light.kitchen
      - Dim a light:       domain=light, service=turn_on, entity_id=light.bedroom, service_data={\"brightness\": 80}
      - Toggle a switch:   domain=switch, service=toggle, entity_id=switch.garage_fan
      - Set climate:       domain=climate, service=set_temperature, entity_id=climate.thermostat, service_data={\"temperature\": 72}
      - Lock a door:       domain=lock, service=lock, entity_id=lock.front_door

    Args:
        params.domain:       Service domain
        params.service:      Service name
        params.entity_id:    Target entity (optional for global services)
        params.service_data: Additional data dict (optional)

    Returns:
        JSON list of affected entity states after the call.
    """
    try:
        body: dict[str, Any] = {}
        if params.entity_id:
            body["entity_id"] = params.entity_id
        if params.service_data:
            body.update(params.service_data)
        result = await _post(f"services/{params.domain}/{params.service}", body)
        return json.dumps(result, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="ha_list_services",
    annotations={"title": "List Available Services", "readOnlyHint": True, "destructiveHint": False}
)
async def ha_list_services(params: DomainFilter) -> str:
    """
    List available services, optionally filtered by domain.

    Args:
        params.domain: Optional domain to filter ('light', 'climate', etc.)

    Returns:
        JSON list of service descriptors with their fields.
    """
    try:
        services = await _get("services")
        if params.domain:
            services = [s for s in services if s.get("domain") == params.domain]
        return json.dumps(services, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="ha_trigger_automation",
    annotations={
        "title": "Trigger Automation",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": False,
    }
)
async def ha_trigger_automation(params: AutomationInput) -> str:
    """
    Manually trigger a Home Assistant automation by its entity ID.

    Args:
        params.automation_id: e.g. 'automation.morning_lights'

    Returns:
        Confirmation message from Home Assistant.
    """
    try:
        result = await _post("services/automation/trigger", {"entity_id": params.automation_id})
        return json.dumps(result, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="ha_get_history",
    annotations={"title": "Get Entity History", "readOnlyHint": True, "destructiveHint": False}
)
async def ha_get_history(params: HistoryInput) -> str:
    """
    Return state history for an entity over the past N hours.

    Args:
        params.entity_id: Entity to query
        params.hours:     How many hours back (1–168, default 24)

    Returns:
        JSON array of historical state objects (timestamp + state).
    """
    try:
        from datetime import datetime, timedelta, timezone
        start = (datetime.now(timezone.utc) - timedelta(hours=params.hours)).isoformat()
        raw = await _get(
            f"history/period/{start}",
            params={
                "filter_entity_id": params.entity_id,
                "minimal_response": "true",
                "no_attributes": "false",
            }
        )
        # raw is a list-of-lists; flatten the first list
        history = raw[0] if raw else []
        return json.dumps(history, indent=2)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="ha_render_template",
    annotations={"title": "Render Template", "readOnlyHint": True, "destructiveHint": False}
)
async def ha_render_template(params: TemplateInput) -> str:
    """
    Render a Jinja2 template string via the Home Assistant template engine.
    Useful for computed values, conditionals, and multi-entity expressions.

    Example templates:
      "{{ states('sensor.outdoor_temp') }}"
      "{{ state_attr('light.living_room', 'brightness') }}"
      "{% if is_state('binary_sensor.door', 'on') %}Open{% else %}Closed{% endif %}"

    Args:
        params.template: Jinja2 template string

    Returns:
        Rendered plain-text result.
    """
    try:
        result = await _post("template", {"template": params.template})
        # HA returns plain text for this endpoint; httpx wraps it as {"message": ...}
        if isinstance(result, dict) and "message" in result:
            return result["message"]
        return str(result)
    except Exception as e:
        return _handle_error(e)


@mcp.tool(
    name="ha_check_config",
    annotations={"title": "Check HA Config", "readOnlyHint": True, "destructiveHint": False}
)
async def ha_check_config() -> str:
    """
    Trigger a configuration.yaml validity check on the Home Assistant server.
    Requires the 'config' integration to be enabled.

    Returns:
        JSON with 'result' ('valid'/'invalid') and optional 'errors'.
    """
    try:
        result = await _post("config/core/check_config")
        return json.dumps(result, indent=2)
    except Exception as e:
        return _handle_error(e)


# ── Entrypoint ────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    if not HA_TOKEN:
        raise SystemExit(
            "HA_TOKEN is not set.\n"
            "Generate a Long-Lived Access Token at http://<HA_HOST>:8123/profile\n"
            "then run:  export HA_TOKEN=your_token_here"
        )
    mcp.run()

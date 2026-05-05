# Changelog

All notable changes to this project will be documented in this file.

## Unreleased

### Added

- Added friendly shortcut tools for common Home Assistant actions:
  - `ha_turn_on`
  - `ha_turn_off`
  - `ha_toggle`
  - `ha_set_temperature`
  - `ha_lock`
  - `ha_unlock`
  - `ha_open_cover`
  - `ha_close_cover`
- Added a shared service-call helper in `server.py` so shortcut tools send consistent Home Assistant REST API requests.
- Added domain checks for climate, lock, and cover shortcut tools to help catch accidental use with the wrong entity type.
- Added safety guardrails that block sensitive Home Assistant actions by default.
- Added allowlist settings for sensitive domains and entities:
  - `HA_ALLOW_SENSITIVE_ACTIONS`
  - `HA_SENSITIVE_DOMAINS`
  - `HA_ALLOWED_SENSITIVE_DOMAINS`
  - `HA_ALLOWED_SENSITIVE_ENTITIES`
- Added denylist settings that always block selected domains or entities:
  - `HA_DENIED_DOMAINS`
  - `HA_DENIED_ENTITIES`
- Added setup-script options for configuring safety allowlists and denylists.
- Added this changelog.

### Changed

- Updated `README.md` to mention the new shortcut tools and link to this changelog.
- Updated `README.md` with plain-language safety settings.
- Updated `future-upgrades.md` to mark safety guardrails as implemented.

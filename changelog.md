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
- Added this changelog.

### Changed

- Updated `README.md` to mention the new shortcut tools and link to this changelog.

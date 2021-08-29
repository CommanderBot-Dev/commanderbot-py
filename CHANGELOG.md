# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Added `manifest` command that generate Bedrock manifests

### Changed

- Improved emoji parsing logic for the `vote` command

## [0.14.0] - 2021-08-25

### Changed

- `automod` improvements (#41):
  - Implemented role-based (per-guild) permissions
  - Added a new `log_message` action that suppresses pings by default
  - Pings are now suppressed by default in error messages
  - Added normalization to the `message_content_contains` condition
  - Added more fields to some events for string formatting

## [0.13.0] - 2021-08-22

### Added

- Added `automod` extension

### Fixed

- Fixed a race condition with `JsonFileDatabaseAdapter` (#39)

### Changed

- Updated `beet` and `lectern`
- Updated other dependencies

## [0.12.0] - 2021-05-13

## Changed

- The `pack` command no longer uses a cache
- Updated several dependencies

## [0.11.0] - 2021-05-10

## Changed

- Fix name argument for `pack` command and add custom help text
- Updated `jira` command to use `aiohttp` instead of `requests`

## [0.10.0] - 2021-05-09

## Changed

- Optional `pack` command argument for changing the name of the generated data pack or resource pack
- The `pack` command no longer shows exception tracebacks by default

## [0.9.0] - 2021-05-09

## Changed

- `invite` descriptions are now optional

## Fixed

- Fixed `kick` command not being guild-only
- Fixed an issue where `invite` descriptions weren't displayed correctly (#29)
- Fixed an issue where JSON database files weren't being initialized correctly (#28)

## [0.8.0] - 2021-05-08

### Added

- Added configurable descriptions to `invite` command
- Added `pack` command timeout and updated `beet` and `lectern`

## [0.7.0] - 2021-04-23

### Added

- Added `jira` command for checking Mojira bug reports
- Added `ping` command with bot latency
- Added `invite` command to list server invites
- Added `pack` command that runs a `beet` build and uses `lectern`
- Added `roles` command to join/leave certain roles
- Partial implementation of the new `help_chat` system

### Changed

- Merged commanderbot-lib repo with this one to simplify project structure

## [0.6.0] - 2021-01-08

### Added

- Added `quote` and `quotem` commands

### Changed

- Updated commanderbot-lib and discord.py

## [0.5.0] - 2021-01-06

### Changed

- `faq` has been extended and improved:
  - FAQs can be created and updated directly from existing messages
  - FAQs can be assigned any number of aliases
  - FAQs remember when they were created and last updated
  - FAQs keep track of how many times they're used (hits)
  - The list of FAQs is sorted by hits -> name
  - More sub-commands for managing FAQs directly

## [0.4.0] - 2021-01-03

### Changed

- Updated to commanderbot-lib version 0.5.0

## [0.3.0] - 2020-09-30

### Added

- Added `vote` command

### Changed

- Updated to discord.py version 1.5.0
- Updated to commanderbot-lib version 0.2.0

## [0.2.0] - 2020-09-24

### Changed

- Now using the PyPI version of `commanderbot-lib`

## [0.1.0] - 2020-09-24

### Added

- Implemented `status` and `faq` extensions as an exercise for developing `commanderbot-lib`

[unreleased]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.14.0...HEAD
[0.14.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.13.0...v0.14.0
[0.13.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.10.0...v0.11.0
[0.10.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/releases/tag/v0.1.0

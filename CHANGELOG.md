# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- `help_forum`:
  - A cog that acts as a wrapper around a forum channel
  - Forum threads can have two states: unresolved and resolved
  - Threads can be resolved using `/resolve` or with a configurable emoji
- `sudo`:
  - Added a way to sync slash commands globally or to a specific guild
  - Added a way to export a cog's database
  - Added a way to display info about the bot
  - Added a way to shutdown the bot
- Added a config option for `mccq` to allow certain users to run the reload command
- Added a link button under `jira` issue embeds

### Changed

- Adjusted the format of the presence status set by `mccq`
- `jira`:
  - Querying `jira` issues using a URL as the argument will now ignore the base URL stored in the `jira` cog and instead get it from the argument
  - Fixed an issue where the embed's status colors weren't being applied
- `quote`: Added descriptions to the commands
- The error handler now supports slash command errors
- `kick`: ported to slash commands
- `status`: ported to slash commands
- `ping`: ported to slash commands

## [0.19.0] - 2022-08-27

### Added

- Added support for `.env` files (to provide the bot token)
- Implemented `mccq` command (from cogbot)
- `allay`:
  - New command, turns a plaintext markdown-like format into a text component with optional indentation levels
- `automod`:
  - Added new thread fields to event metadata
  - Implemented new `ChannelTypesGuard` to account for threads
  - Implemented new triggers:
    - `thread_updated`
  - Implemented new conditions:
    - `actor_is_bot`
    - `actor_is_self`
    - `author_is_bot`
    - `author_is_self`
    - `actor_member_for`
    - `author_member_for`
    - `member_for`
    - `message_has_mentions`
    - `thread_auto_archive_duration`
  - Implemented new actions:
    - `check_messages`
    - `dm_member`
- `manifest`:
  - Added a task that requests the latest `min_engine_version`
  - Now accepts a `version_url` option in the bot config
  - Added `manifests` command with `status` and `update` subcommands
    - `status` shows the status of version requests
    - `update` manually requests the version
- `roles`:
  - Implemented new `about` subcommand

### Changed

- **Updated to the latest version of discord.py** (after it was revived from the dead)
- `faq`:
  - The list of FAQs is now separated by comma
- `manifest`:
  - Generated manifests were changed into file attachments
- `quote`:
  - Improved attachment/embed handling
- `roles`:
  - Updated the set of safe permissions to reduce unnecessary warnings
  - Duplicate roles are now filtered-out prior to joining/leaving
  - Now using difflib to help disambiguate roles

### Fixed

- Utcnow and datetime fixes (#75)

## [0.18.0] - 2021-10-04

### Added

- `automod`: Added support for JSON paths for easier configuration of rules
- `jira`: Reimplemented link support (#65)
- `roles`: Added tips for providing roles

### Changed

- `automod`: An exhaustive list of adjustments and improvements that's too long and complicated for the changelog
- `faq`:
  - Turned the shortcut prefix into a pattern
  - Consolidated FAQ update commands
  - Reimplement the list of FAQs
  - Various improvements (#72)
    - Added options in root config to limit or disable certain features
    - Reorganized and added new search commands
    - Improved how tags are used in queries
    - Allowed showing options instead of just setting them
- `invite`: Multiple invites now go in one message instead of multiple
- `jira`: Overhauled the issue requesting logic and the embed colors now reflect the status of the bug (#64)
- `roles`: Refine role searching logic

### Fixed

- Fixed instances of timezone-unaware `utcnow()`
- `jira`: Now checks that issues are in the `<project>-<id>` format and that requested issues have fields (#69)

## [0.17.0] - 2021-09-02

### Added

- Implemented a new cog `stacktracer` for error logging (#55)
- `automod`: Added a new [`mentions_removed_from_message`](https://github.com/CommanderBot-Dev/commanderbot-py/wiki/Extension:-automod#mentions_removed_from_message-trigger) trigger
- `automod`: Added `allowed_mentions` field to [`reply_to_message`](https://github.com/CommanderBot-Dev/commanderbot-py/wiki/Extension:-automod#reply_to_message-action) action

### Changed

- `status` now uses an embed (#45)

### Fixed

- `quote`: Now includes attachments and embeds on the original message
- `quote`: Now accounts for the read permissions of the person trying to quote
- `ChannelsGuard` now accounts for threads, by determining the root channel

## [0.16.0] - 2021-08-30

### Changed

- Updated to Python 3.10 (release candidate).
- Updated to the discord.py 2.0 beta.
- Updated all extensions past breaking changes.
- `commanderbot-core` has been merged into `commanderbot-ext`.
  - The repository has been renamed to `commanderbot-py`.
  - The package has been renamed to `commanderbot` (which used to belong to `commanderbot-core`).
- Exception handling logic has been reworked.
  - Fixes #53
- Reconsidered all commands to use a `ctx.reply` wrapper with pings disabled.
  - Fixes #42
- `allowed_mentions` field in root bot config is now supported.
  - Fixes #52
- `automod`:
  - Even data now includes `user` fields.
    - Fixes #43
  - Even data now includes member date fields by default.
  - `message` triggers now allow basic matching of message content.
    - Fixes #44
- `roles`:
  - Unresolved roles are now deregistered and cleaned-up automatically.
    - Fixes #47
  - Elevated commands can no longer add/remove unregistered roles to/from users.
    - Fixes #48
  - Users can now join/leave multiple roles in one command.
    - Fixes #49
  - Multiple roles can now be added/removed to/from multiple members all in one command.
  - Roles can now be targeted using a partial name match.
    - Fixes #50
  - Roles can now be configured to be able to run elevated commands.
    - Fixes #18

## [0.15.0] - 2021-08-29

### Added

- Added `manifest` command that generates Bedrock manifests (#51)

### Changed

- Improved emoji parsing logic for the `vote` command (#45)

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

[unreleased]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.19.0...HEAD
[0.19.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.18.0...v0.19.0
[0.18.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.17.0...v0.18.0
[0.17.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.16.0...v0.17.0
[0.16.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.15.0...v0.16.0
[0.15.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.14.0...v0.15.0
[0.14.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.13.0...v0.14.0
[0.13.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.12.0...v0.13.0
[0.12.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.11.0...v0.12.0
[0.11.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.10.0...v0.11.0
[0.10.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.9.0...v0.10.0
[0.9.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.8.0...v0.9.0
[0.8.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.7.0...v0.8.0
[0.7.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.6.0...v0.7.0
[0.6.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.5.0...v0.6.0
[0.5.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/CommanderBot-Dev/commanderbot-py/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/CommanderBot-Dev/commanderbot-py/releases/tag/v0.1.0

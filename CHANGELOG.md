# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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

[unreleased]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.5.0...HEAD
[0.5.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.4.0...v0.5.0
[0.4.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.3.0...v0.4.0
[0.3.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.2.0...v0.3.0
[0.2.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/CommanderBot-Dev/commanderbot-ext/releases/tag/v0.1.0

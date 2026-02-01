# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0](https://github.com/minipuft/gemini-prompts/compare/v1.3.2...v2.0.0) (2026-02-01)


### ⚠ BREAKING CHANGES

* Removed git submodule, now uses npm dependency

### Added

* add upstream sync workflow for automatic dependency updates ([2d0c5c6](https://github.com/minipuft/gemini-prompts/commit/2d0c5c69e10cc57522874d0cf3e58aa16ba46972))
* **ci:** add Release Please, commitlint, and daily dependabot ([38eee9f](https://github.com/minipuft/gemini-prompts/commit/38eee9f47ba4b0e8b06d5aac36be401cdfe2faad))
* migrate from submodule to npm dependency ([03f7799](https://github.com/minipuft/gemini-prompts/commit/03f77994b76338b925700c0bb127583cf3ac4b2e))


### Fixed

* **submodule:** point core to dist branch (956c113) for 1.3.2 ([09da3cb](https://github.com/minipuft/gemini-prompts/commit/09da3cb1927279cdd64b5300244683267a782050))


### Changed

* **hooks:** migrate to native hooks from upstream ([7899f80](https://github.com/minipuft/gemini-prompts/commit/7899f805d8871471160b0291a3300f919595e55a))


### Documentation

* add README with Diátaxis structure ([ba0eba4](https://github.com/minipuft/gemini-prompts/commit/ba0eba486aa7667c43ab9626cffc8bfb9d084d3d))

## [Unreleased]

## [1.3.2] - 2025-01-18

### Fixed

- Dependabot auto-merge workflow for patch and minor updates

## [1.3.0] - 2025-01-13

### Added

- Initial Gemini CLI extension implementation
- Hook-based integration with claude-prompts MCP server
- Dependabot configuration for claude-prompts dependency updates
- CI workflow for extension structure validation

[Unreleased]: https://github.com/minipuft/gemini-prompts/compare/v1.3.2...HEAD
[1.3.2]: https://github.com/minipuft/gemini-prompts/compare/v1.3.0...v1.3.2
[1.3.0]: https://github.com/minipuft/gemini-prompts/releases/tag/v1.3.0

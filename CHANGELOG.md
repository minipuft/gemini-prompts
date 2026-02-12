# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Hook execution environment now explicitly sets `MCP_WORKSPACE` to correctly resolve SQLite state across symlinked directories, fixing silent failures in prompt detection and tracking
- Updated hooks (`before-agent`, `after-tool`, `gate-enforce`, `pre-compact`, `ralph-context-tracker`) for compatibility with `claude-prompts` v1.7.0+ SQLite state backend

### Changed

- Aligned hook JSON output with strict Gemini CLI contract by adding explicit `decision` fields (e.g., `decision: "allow"`) to prevent ambiguous behavior


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

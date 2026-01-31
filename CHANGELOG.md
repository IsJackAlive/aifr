# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.0] - 2026-01-31

### Added
- **Multi-file Context**: Support for multiple `-f / --file` flags to inject multiple files into the context.
- **Model Aliases**: New `model_aliases` config section to map short names to full models (e.g. `gpt` -> `openai/gpt-4o`).
- **Dynamic Model Resolution**: Support for `provider/model` syntax in `--model` flag.
- **Custom Agents**: New `--agent` flag and `custom_agents` config section to define specialized agents with custom system prompts and models.
- **Smart TTY**: Automatic suppression of ANSI colors and banners when output is redirected to pipes or files.
- **Raw Mode**: New `--raw / -r` flag to force plain text output.

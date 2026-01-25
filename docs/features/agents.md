# Aifr Coding Assistant - Context for Agents

This document contains context, conventions, and instructions for AI agents modifying the Aifr codebase.

## Project Overview
Aifr (`aifr`) is a minimal, fast, and efficient Python CLI terminal assistant designed for quick, local AI invocations. It supports multiple LLM providers and focuses on simplicity and performance.

- **Core Philosophy**: Provide a fast, uncomplicated, and effective way to call AI models directly from the terminal, with a focus on local execution and privacy where possible.
- **Core Logic**: `cli.py` is the main orchestrator. It parses arguments, manages context, selects the appropriate provider and model, and handles the main request-response loop.
- **Providers**: The provider architecture in `providers.py` allows interfacing with different LLM APIs (e.g., OpenAI, OpenWebUI for local models, Brave, Sherlock).
- **State**: Session history is stored in `~/.cache/aifr/session.json` via `session_store.py`.
- **Config**: Configuration lives in `~/.config/aifr/config.json` and is managed by `config.py`.

## CLI Dependencies & Flow (`cli.py`)
The `cli.py` module integrates several components to process a user's request:
1.  **`cli_parser.py`**: Parses command-line arguments (`$ask`, `$file`, etc.).
2.  **`config.py`**: Loads application configuration, including API keys and the selected provider.
3.  **`session_store.py`**: Loads the previous conversation history to maintain context.
4.  **`file_loader.py` / `terminal_capture.py`**: Loads file content or captures shell command output to inject into the prompt.
5.  **`agent_controller.py`**: Detects the "agent type" based on the input (e.g., if a file or console output is present) and selects the appropriate system prompt.
6.  **`model_selector.py`**: Intelligently selects the best model for the job based on the query, user flags, and whether a large context is needed (e.g., for large files).
7.  **`api.py` & `providers.py`**: `api.py` acts as a facade that delegates the actual API call to the correct provider implementation in `providers.py`.
8.  **`output.py`**: Prints the response from the LLM to the terminal.
9.  **`context.py` / `session_store.py`**: The `ContextManager` updates the conversation history, which is then saved for the next turn.

## Development Environment & Build
- **Python Version**: 3.10+ required.
- **Dependency Management**: Uses `pyproject.toml`. Install in editable mode with `pip install -e .`.
- **Key Dependencies**: `requests`.

## Git & Commit Conventions
- **Commit Messages**: Follow the Conventional Commits specification.
  - `feat:` for new features.
  - `fix:` for bug fixes.
  - `docs:` for documentation changes.
  - `style:` for code style changes (formatting, etc.).
  - `refactor:` for code changes that neither fix a bug nor add a feature.
  - `test:` for adding or refactoring tests.
  - `chore:` for build process or auxiliary tool changes.
- **Example**: `feat: add support for Brave Summarizer API`

## Testing Instructions
- **Framework**: `pytest`.
- **Location**: `tests/` directory.
- **Mocking is Mandatory**: 
  - NEVER make real network calls to external APIs during tests.
  - Mock the `requests` library or the specific provider's `call` method using `unittest.mock` or `pytest-mock`.
- **Key Test Scenarios**:
  - **Providers**: Test each provider's request/response handling (`tests/test_providers.py`).
  - **Model Selection**: Verify `model_selector.py` chooses the correct model based on input.
  - **Context Management**: Ensure `ContextManager` respects token limits and correctly prunes old messages.

## Critical Implementation Details
- **Provider Architecture (`providers.py`)**:
  - All providers inherit from the `LlmProvider` abstract base class.
  - A factory function `create_provider()` instantiates the correct provider based on the configuration.
  - This makes adding new providers (e.g., Gemini, Claude) straightforward.
- **Model Selection (`model_selector.py`)**:
  - This module decouples the CLI from hardcoded model names.
  - It contains logic to automatically switch to a larger context model if the input file is large, preventing `ContextLengthError`.
- **Session Management (`session_store.py`)**:
  - Handles loading and saving the conversation history as a simple JSON file.
  - This provides the "memory" for the assistant between commands.
- **Context Injection**:
  - Files are wrapped in `===FILE_START===` and `===FILE_END===`.
  - Console output is wrapped in `===CONSOLE_START===` and `===CONSOLE_END===`.
  - The agent must preserve these delimiters when constructing the prompt.
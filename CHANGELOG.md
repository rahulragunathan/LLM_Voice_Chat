# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Security**: Environment file templates (.env.example) for safe credential management
- **Security**: Enhanced .gitignore to prevent committing API keys
- **Feature**: Chat history support for Ollama models (previously only available for OpenAI)
- **Feature**: Comprehensive configuration validation on startup with clear error messages
- **Feature**: New `config_validator` module for validating all configuration types
- **Quality**: Type hints added to function signatures in app_config.py
- **Quality**: Enhanced error handling with user-friendly messages for configuration issues
- **Testing**: Unit test suite for configuration validation
- **Testing**: Unit tests for configuration loading
- **Documentation**: Comprehensive docstrings for all Python modules and functions
- **Documentation**: Updated README with complete configuration guide and examples
- **Documentation**: CHANGELOG.md for tracking version history
- **Documentation**: Example configuration files in env/soothsayers/

### Changed
- Configuration loading now includes validation by default
- Error messages provide clearer guidance on configuration issues
- Ollama model responses now support conversation context like OpenAI models

### Fixed
- Removed exposed API keys from example environment files
- Configuration loading now exits gracefully with helpful error messages on failure

### Security
- **CRITICAL**: Removed exposed OpenAI API key from repository
- Added .env.example template files to guide users in creating secure configurations
- Updated .gitignore to prevent future API key commits

## [1.0.0] - 2024-11-19

### Added
- Initial release of LLM Voice Chat
- Support for OpenAI GPT models (GPT-4o, GPT-3.5-turbo, etc.)
- Support for local Ollama models (LLaMA 3.1, TinyLLaMA, DeepSeek, etc.)
- Text-to-speech functionality with configurable voices and speech rate
- Streaming responses with configurable typing effect
- Gradio web interface with customizable themes
- JSON-based configuration system (model, prompt, response, theme)
- Cross-platform support (Windows, macOS, Linux)
- GPU acceleration for Ollama models
- Chat history for OpenAI models
- Platform-specific voice selection for TTS
- Configurable logging levels

[Unreleased]: https://github.com/yourusername/LLM_Voice_Chat/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/yourusername/LLM_Voice_Chat/releases/tag/v1.0.0

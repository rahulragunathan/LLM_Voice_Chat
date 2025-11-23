"""
Unit tests for config_validator module.

Tests validation logic for all configuration types to ensure proper
error detection and reporting.
"""

import pytest
from config_validator import (
    validate_model_config,
    validate_prompt_config,
    validate_response_config,
    validate_theme_config,
    validate_all_configs,
    ConfigValidationError,
)


class TestModelConfigValidation:
    """Test cases for model configuration validation."""

    def test_valid_openai_config(self, monkeypatch):
        """Test that valid OpenAI configuration passes validation."""
        # Mock the OPENAI_API_KEY environment variable
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")

        config = {
            "use_remote_model": True,
            "model_source": "OpenAI",
            "model_name": "gpt-4o",
            "model_parameters": {"temperature": 1.0},
        }
        is_valid, errors = validate_model_config(config)
        assert is_valid
        assert len(errors) == 0

    def test_valid_ollama_config(self):
        """Test that valid Ollama configuration passes validation."""
        config = {
            "use_remote_model": False,
            "model_source": "Ollama",
            "model_name": "llama3.1",
            "model_parameters": {"temperature": 0.8},
            "use_gpu": True,
            "num_gpu": 1,
        }
        is_valid, errors = validate_model_config(config)
        assert is_valid
        assert len(errors) == 0

    def test_missing_required_fields(self):
        """Test that missing required fields are detected."""
        config = {"model_name": "gpt-4o"}
        is_valid, errors = validate_model_config(config)
        assert not is_valid
        assert "Missing required field: 'use_remote_model'" in errors
        assert "Missing required field: 'model_source'" in errors

    def test_invalid_model_source(self):
        """Test that invalid model source is detected."""
        config = {
            "use_remote_model": True,
            "model_source": "InvalidSource",
            "model_name": "model",
            "model_parameters": {},
        }
        is_valid, errors = validate_model_config(config)
        assert not is_valid
        assert any("Invalid 'model_source'" in err for err in errors)

    def test_invalid_type_use_remote_model(self):
        """Test that non-boolean use_remote_model is detected."""
        config = {
            "use_remote_model": "yes",
            "model_source": "OpenAI",
            "model_name": "gpt-4o",
            "model_parameters": {},
        }
        is_valid, errors = validate_model_config(config)
        assert not is_valid
        assert any("must be a boolean" in err for err in errors)


class TestPromptConfigValidation:
    """Test cases for prompt configuration validation."""

    def test_valid_prompt_config(self):
        """Test that valid prompt configuration passes validation."""
        config = {
            "input_variables": ["question"],
            "template": "Answer this: {question}",
        }
        is_valid, errors = validate_prompt_config(config)
        assert is_valid
        assert len(errors) == 0

    def test_missing_input_variables(self):
        """Test that missing input_variables is detected."""
        config = {"template": "Hello world"}
        is_valid, errors = validate_prompt_config(config)
        assert not is_valid
        assert "Missing required field: 'input_variables'" in errors

    def test_missing_template(self):
        """Test that missing template is detected."""
        config = {"input_variables": ["question"]}
        is_valid, errors = validate_prompt_config(config)
        assert not is_valid
        assert "Missing required field: 'template'" in errors

    def test_variable_not_in_template(self):
        """Test that input variables not referenced in template are detected."""
        config = {
            "input_variables": ["question", "context"],
            "template": "Answer: {question}",
        }
        is_valid, errors = validate_prompt_config(config)
        assert not is_valid
        assert any("not found in template" in err for err in errors)


class TestResponseConfigValidation:
    """Test cases for response configuration validation."""

    def test_valid_response_config(self):
        """Test that valid response configuration passes validation."""
        config = {
            "speak_responses": True,
            "response_delay_time": 3,
            "response_stream_lag_time": 0.04,
            "speech_rate_wpm": 140,
            "voice_name": "Samantha",
        }
        is_valid, errors = validate_response_config(config)
        assert is_valid
        assert len(errors) == 0

    def test_empty_config_is_valid(self):
        """Test that empty response config is valid (all fields optional)."""
        config = {}
        is_valid, errors = validate_response_config(config)
        assert is_valid
        assert len(errors) == 0

    def test_invalid_speak_responses_type(self):
        """Test that non-boolean speak_responses is detected."""
        config = {"speak_responses": "yes"}
        is_valid, errors = validate_response_config(config)
        assert not is_valid
        assert any("must be a boolean" in err for err in errors)

    def test_invalid_speech_rate_type(self):
        """Test that non-numeric speech_rate_wpm is detected."""
        config = {"speech_rate_wpm": "fast"}
        is_valid, errors = validate_response_config(config)
        assert not is_valid
        assert any("must be a number" in err for err in errors)


class TestThemeConfigValidation:
    """Test cases for theme configuration validation."""

    def test_valid_theme_config(self):
        """Test that valid theme configuration passes validation."""
        config = {
            "app_name": "My App",
            "source_theme": "soft",
            "load_theme_from_hf_hub": False,
            "font": ["Arial", "sans-serif"],
        }
        is_valid, errors = validate_theme_config(config)
        assert is_valid
        assert len(errors) == 0

    def test_empty_config_is_valid(self):
        """Test that empty theme config is valid (all fields optional)."""
        config = {}
        is_valid, errors = validate_theme_config(config)
        assert is_valid
        assert len(errors) == 0

    def test_invalid_font_type(self):
        """Test that non-list font is detected."""
        config = {"font": "Arial"}
        is_valid, errors = validate_theme_config(config)
        assert not is_valid
        assert any("must be a list" in err for err in errors)


class TestValidateAllConfigs:
    """Test cases for validate_all_configs function."""

    def test_all_valid_configs(self, monkeypatch):
        """Test that all valid configurations pass validation."""
        # Mock the OPENAI_API_KEY environment variable
        monkeypatch.setenv("OPENAI_API_KEY", "test-api-key")

        model_config = {
            "use_remote_model": True,
            "model_source": "OpenAI",
            "model_name": "gpt-4o",
            "model_parameters": {},
        }
        prompt_config = {
            "input_variables": ["question"],
            "template": "{question}",
        }
        response_config = {"speak_responses": False}
        theme_config = {"app_name": "Test"}

        # Should not raise any exception
        validate_all_configs(
            model_config, prompt_config, response_config, theme_config
        )

    def test_multiple_invalid_configs(self):
        """Test that errors from multiple configs are collected."""
        model_config = {"use_remote_model": "invalid"}  # Invalid type
        prompt_config = {}  # Missing required fields
        response_config = {"speak_responses": "invalid"}  # Invalid type
        theme_config = {"font": "invalid"}  # Invalid type

        with pytest.raises(ConfigValidationError) as exc_info:
            validate_all_configs(
                model_config, prompt_config, response_config, theme_config
            )

        error_message = str(exc_info.value)
        assert "Model Configuration Errors" in error_message
        assert "Prompt Configuration Errors" in error_message
        assert "Response Configuration Errors" in error_message
        assert "Theme Configuration Errors" in error_message

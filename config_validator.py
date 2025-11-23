"""
Configuration Validation Module

Provides validation functions for all configuration dictionaries used in the
LLM Voice Chat application. Validates structure, required fields, and data types
to catch configuration errors early at startup.

Features:
- Comprehensive validation for model, prompt, response, and theme configurations
- Clear error messages indicating what's wrong and where
- Type checking for configuration values
- Default value suggestions for missing optional fields
"""

import os
from typing import Dict, Any, List, Tuple, Optional
import logging


class ConfigValidationError(Exception):
    """Exception raised when configuration validation fails."""

    pass


def validate_model_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate model configuration dictionary.

    Args:
        config: Model configuration dictionary to validate

    Returns:
        Tuple of (is_valid, error_messages)
            - is_valid: Boolean indicating if configuration is valid
            - error_messages: List of validation error messages (empty if valid)

    Example:
        >>> config = {"use_remote_model": True, "model_source": "OpenAI", ...}
        >>> is_valid, errors = validate_model_config(config)
        >>> if not is_valid:
        ...     print(f"Errors: {errors}")
    """
    errors = []

    # Required fields
    if "use_remote_model" not in config:
        errors.append("Missing required field: 'use_remote_model'")
    elif not isinstance(config["use_remote_model"], bool):
        errors.append("'use_remote_model' must be a boolean (true/false)")

    if "model_source" not in config:
        errors.append("Missing required field: 'model_source'")
    elif config["model_source"] not in ["OpenAI", "Ollama"]:
        errors.append(
            f"Invalid 'model_source': '{config['model_source']}'. Must be 'OpenAI' or 'Ollama'"
        )

    if "model_name" not in config:
        errors.append("Missing required field: 'model_name'")
    elif not isinstance(config["model_name"], str):
        errors.append("'model_name' must be a string")

    if "model_parameters" not in config:
        errors.append("Missing required field: 'model_parameters'")
    elif not isinstance(config["model_parameters"], dict):
        errors.append("'model_parameters' must be a dictionary")

    # Validate OpenAI specific configuration
    if (
        config.get("use_remote_model")
        and config.get("model_source") == "OpenAI"
    ):
        # Check for API key in environment
        if not os.getenv("OPENAI_API_KEY"):
            errors.append(
                "OPENAI_API_KEY environment variable is required for OpenAI models"
            )

    # Validate Ollama specific configuration
    if (
        not config.get("use_remote_model", True)
        and config.get("model_source") == "Ollama"
    ):
        if "use_gpu" in config and not isinstance(config["use_gpu"], bool):
            errors.append("'use_gpu' must be a boolean if specified")
        if "num_gpu" in config and not isinstance(config["num_gpu"], int):
            errors.append("'num_gpu' must be an integer if specified")

    return (len(errors) == 0, errors)


def validate_prompt_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate prompt configuration dictionary.

    Args:
        config: Prompt configuration dictionary to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    if "input_variables" not in config:
        errors.append("Missing required field: 'input_variables'")
    elif not isinstance(config["input_variables"], list):
        errors.append("'input_variables' must be a list")

    if "template" not in config:
        errors.append("Missing required field: 'template'")
    elif not isinstance(config["template"], str):
        errors.append("'template' must be a string")

    # Verify input variables are referenced in template
    if "input_variables" in config and "template" in config:
        for var in config["input_variables"]:
            if f"{{{var}}}" not in config["template"]:
                errors.append(
                    f"Input variable '{var}' not found in template string"
                )

    return (len(errors) == 0, errors)


def validate_response_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate response configuration dictionary.

    Args:
        config: Response configuration dictionary to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Optional fields with type validation
    if "speak_responses" in config and not isinstance(
        config["speak_responses"], bool
    ):
        errors.append("'speak_responses' must be a boolean if specified")

    if "response_delay_time" in config and not isinstance(
        config["response_delay_time"], (int, float)
    ):
        errors.append(
            "'response_delay_time' must be a number if specified"
        )

    if "response_stream_lag_time" in config and not isinstance(
        config["response_stream_lag_time"], (int, float)
    ):
        errors.append(
            "'response_stream_lag_time' must be a number if specified"
        )

    if "speech_rate_wpm" in config and not isinstance(
        config["speech_rate_wpm"], (int, float)
    ):
        errors.append("'speech_rate_wpm' must be a number if specified")

    if "voice_name" in config and not isinstance(config["voice_name"], str):
        errors.append("'voice_name' must be a string if specified")

    return (len(errors) == 0, errors)


def validate_theme_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate theme configuration dictionary.

    Args:
        config: Theme configuration dictionary to validate

    Returns:
        Tuple of (is_valid, error_messages)
    """
    errors = []

    # Optional fields with type validation
    if "app_name" in config and not isinstance(config["app_name"], str):
        errors.append("'app_name' must be a string if specified")

    if "source_theme" in config and not isinstance(
        config["source_theme"], str
    ):
        errors.append("'source_theme' must be a string if specified")

    if "load_theme_from_hf_hub" in config and not isinstance(
        config["load_theme_from_hf_hub"], bool
    ):
        errors.append(
            "'load_theme_from_hf_hub' must be a boolean if specified"
        )

    if "font" in config and not isinstance(config["font"], list):
        errors.append("'font' must be a list if specified")

    return (len(errors) == 0, errors)


def validate_all_configs(
    model_config: Dict[str, Any],
    prompt_config: Dict[str, Any],
    response_config: Dict[str, Any],
    theme_config: Dict[str, Any],
) -> None:
    """Validate all configuration dictionaries and raise exception if any are invalid.

    Args:
        model_config: Model configuration dictionary
        prompt_config: Prompt configuration dictionary
        response_config: Response configuration dictionary
        theme_config: Theme configuration dictionary

    Raises:
        ConfigValidationError: If any configuration is invalid, with details
            about all validation errors found

    Example:
        >>> try:
        ...     validate_all_configs(model, prompt, response, theme)
        ... except ConfigValidationError as e:
        ...     print(f"Configuration errors: {e}")
        ...     sys.exit(1)
    """
    all_errors = []

    # Validate each configuration
    is_valid, errors = validate_model_config(model_config)
    if not is_valid:
        all_errors.append("Model Configuration Errors:")
        all_errors.extend([f"  - {err}" for err in errors])

    is_valid, errors = validate_prompt_config(prompt_config)
    if not is_valid:
        all_errors.append("Prompt Configuration Errors:")
        all_errors.extend([f"  - {err}" for err in errors])

    is_valid, errors = validate_response_config(response_config)
    if not is_valid:
        all_errors.append("Response Configuration Errors:")
        all_errors.extend([f"  - {err}" for err in errors])

    is_valid, errors = validate_theme_config(theme_config)
    if not is_valid:
        all_errors.append("Theme Configuration Errors:")
        all_errors.extend([f"  - {err}" for err in errors])

    # Raise exception if any errors found
    if all_errors:
        error_message = "\n".join(all_errors)
        raise ConfigValidationError(
            f"Configuration validation failed:\n\n{error_message}"
        )

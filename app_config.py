"""
Application Configuration Module

Handles loading and management of unified JSON configuration file for the LLM Voice Chat
application. All settings (model, prompt, response, theme) are in a single JSON file.

Configuration file is specified via CONFIG_PATH environment variable.
Default: ./config/unified_config_example.json
"""

import json
import os
import sys
from typing import Dict, Any

import config_validator


def load_config(filepath: str) -> Dict[str, Any]:
    """Load a JSON configuration file and return it as a dictionary.

    Args:
        filepath (str): Absolute or relative path to the JSON configuration file

    Returns:
        Dict[str, Any]: The JSON configuration file contents as a Python dictionary

    Raises:
        FileNotFoundError: If the specified file does not exist
        json.JSONDecodeError: If the file is not valid JSON format
        SystemExit: If the file cannot be read or parsed, with helpful error message
    """
    try:
        with open(filepath) as f:
            data = json.load(f)
        return data
    except FileNotFoundError:
        print(f"\nERROR: Configuration file not found: {filepath}")
        print(f"Please ensure the file exists or check your CONFIG_PATH environment variable.\n")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"\nERROR: Invalid JSON in configuration file: {filepath}")
        print(f"JSON Error: {e}")
        print(f"Please check the file for syntax errors.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\nERROR: Failed to load configuration file: {filepath}")
        print(f"Error: {e}\n")
        sys.exit(1)


class AppConfig:
    """Application configuration manager for LLM Voice Chat.

    Uses a unified configuration format where all settings are in a single JSON file
    organized in sections: model, prompt, response, theme.

    Configuration Path:
        Set CONFIG_PATH environment variable to specify your config file.
        Defaults to ./config/unified_config_example.json

    Configuration Structure:
        {
            "app_name": "Your App Name",
            "version": "1.0.0",
            "model": { ... model settings ... },
            "prompt": { ... prompt template ... },
            "response": { ... response behavior ... },
            "theme": { ... UI theme settings ... }
        }

    Attributes:
        model_config (dict): Model configuration including model source, name,
            and hyperparameters (temperature, top_p, etc.)
        prompt_config (dict): LangChain PromptTemplate configuration with
            template text and input variables
        response_config (dict): Response behavior settings including TTS options,
            streaming delays, and voice selection
        theme_config (dict): Gradio UI theme configuration including colors,
            fonts, and placeholder text
        app_name (str): Application name from config
        version (str): Application version from config

    Example:
        >>> os.environ['CONFIG_PATH'] = './config/my_config.json'
        >>> config = AppConfig()
        >>> print(config.model_config['model_name'])
        'gpt-4o'
        >>> print(config.app_name)
        'My LLM Chat App'
    """

    _DEFAULT_CONFIG_PATH = "./config/unified_config_example.json"

    def __init__(self, validate: bool = True) -> None:
        """Initialize AppConfig by loading the unified configuration file.

        Loads configuration from a single JSON file containing all settings
        organized in sections: model, prompt, response, theme.

        Configuration path is determined by:
        1. CONFIG_PATH environment variable
        2. Default path: ./config/unified_config_example.json

        Args:
            validate (bool): Whether to validate configurations after loading.
                Defaults to True. Set to False only for testing.

        Raises:
            FileNotFoundError: If configuration file cannot be found
            json.JSONDecodeError: If configuration file contains invalid JSON
            ConfigValidationError: If validation is enabled and configuration
                is invalid
            SystemExit: If configuration loading or validation fails
        """
        config_path = os.getenv("CONFIG_PATH", AppConfig._DEFAULT_CONFIG_PATH)

        # Load the unified configuration
        config = load_config(config_path)

        # Extract app-level settings
        self.app_name = config.get("app_name", "LLM Voice Chat")
        self.version = config.get("version", "1.0.0")

        # Extract required sections
        if "model" not in config:
            print(
                f"\nERROR: Configuration file missing 'model' section: {config_path}\n"
            )
            sys.exit(1)
        if "prompt" not in config:
            print(
                f"\nERROR: Configuration file missing 'prompt' section: {config_path}\n"
            )
            sys.exit(1)

        self.model_config = config["model"]
        self.prompt_config = config["prompt"]
        self.response_config = config.get("response", {})
        self.theme_config = config.get("theme", {})

        # Add app_name to theme config if not already there
        if "app_name" not in self.theme_config:
            self.theme_config["app_name"] = self.app_name

        # Validate configurations if requested
        if validate:
            try:
                config_validator.validate_all_configs(
                    self.model_config,
                    self.prompt_config,
                    self.response_config,
                    self.theme_config,
                )
            except config_validator.ConfigValidationError as e:
                print(f"\n{e}\n")
                sys.exit(1)

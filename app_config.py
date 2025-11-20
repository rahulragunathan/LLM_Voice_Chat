"""
Application Configuration Module

Handles loading and management of JSON configuration files for the LLM Voice Chat
application. Configurations include model settings, prompt templates, response
behavior, and UI theme customization.

Configuration files are specified via environment variables:
- MODEL_CONFIG_PATH: Path to model configuration JSON
- PROMPT_CONFIG_PATH: Path to prompt template configuration JSON
- RESPONSE_CONFIG_PATH: Path to response behavior configuration JSON
- THEME_CONFIG_PATH: Path to UI theme configuration JSON
"""

import json
import os


def load_config(filepath: str) -> dict:
    """Load a JSON configuration file and return it as a dictionary.

    Args:
        filepath (str): Absolute or relative path to the JSON configuration file

    Returns:
        dict: The JSON configuration file contents as a Python dictionary

    Raises:
        FileNotFoundError: If the specified file does not exist
        json.JSONDecodeError: If the file is not valid JSON format
    """
    with open(filepath) as f:
        data = json.load(f)
    return data


class AppConfig:
    """Application configuration manager for LLM Voice Chat.

    Loads all application configurations from JSON files specified by environment
    variables. Falls back to default configuration files if environment variables
    are not set.

    Default Configuration Paths:
        - Model: ./config/model_config_chatgpt_default.json
        - Prompt: ./config/prompt_config_default.json
        - Response: ./config/response_config_default.json
        - Theme: ./config/theme_config_default.json

    Environment Variables:
        - MODEL_CONFIG_PATH: Path to custom model configuration JSON
        - PROMPT_CONFIG_PATH: Path to custom prompt template JSON
        - RESPONSE_CONFIG_PATH: Path to custom response behavior JSON
        - THEME_CONFIG_PATH: Path to custom theme configuration JSON

    Attributes:
        model_config (dict): Model configuration including model source, name,
            and hyperparameters (temperature, top_p, etc.)
        prompt_config (dict): LangChain PromptTemplate configuration with
            template text and input variables
        response_config (dict): Response behavior settings including TTS options,
            streaming delays, and voice selection
        theme_config (dict): Gradio UI theme configuration including colors,
            fonts, and placeholder text

    Example:
        >>> config = AppConfig()
        >>> print(config.model_config['model_name'])
        'gpt-4o'
        >>> print(config.response_config['speak_responses'])
        True
    """

    _DEFAULT_MODEL_CONFIG_PATH = "./config/model_config_chatgpt_default.json"
    _DEFAULT_PROMPT_CONFIG_PATH = "./config/prompt_config_default.json"
    _DEFAULT_RESPONSE_CONFIG_PATH = "./config/response_config_default.json"
    _DEFAULT_THEME_CONFIG_PATH = "./config/theme_config_default.json"

    def __init__(self) -> None:
        """Initialize AppConfig by loading all configuration files.

        Loads configurations from paths specified by environment variables,
        falling back to default paths if environment variables are not set.

        The following configurations are loaded:
            - model_config: From MODEL_CONFIG_PATH environment variable
            - prompt_config: From PROMPT_CONFIG_PATH environment variable
            - response_config: From RESPONSE_CONFIG_PATH environment variable
            - theme_config: From THEME_CONFIG_PATH environment variable

        Raises:
            FileNotFoundError: If any configuration file cannot be found
            json.JSONDecodeError: If any configuration file contains invalid JSON
        """

        model_config_path = os.getenv(
            "MODEL_CONFIG_PATH", AppConfig._DEFAULT_MODEL_CONFIG_PATH
        )
        self.model_config = load_config(model_config_path)

        prompt_config_path = os.getenv(
            "PROMPT_CONFIG_PATH", AppConfig._DEFAULT_PROMPT_CONFIG_PATH
        )
        self.prompt_config = load_config(prompt_config_path)

        response_config_path = os.getenv(
            "RESPONSE_CONFIG_PATH", AppConfig._DEFAULT_RESPONSE_CONFIG_PATH
        )
        self.response_config = load_config(response_config_path)

        theme_config_path = os.getenv(
            "THEME_CONFIG_PATH", AppConfig._DEFAULT_THEME_CONFIG_PATH
        )
        self.theme_config = load_config(theme_config_path)

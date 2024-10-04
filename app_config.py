import json
import os


def load_config(filepath: str) -> dict:
    """
    Read file path and load using json. Assumes filepath points
    to a json formatted input file.

    Args:
        filepath (str): the file path to the configuration file

    Returns:
        dict: the JSON configuration file loaded as a Python dictionary
    """
    with open(filepath) as f:
        data = json.load(f)
    return data


class AppConfig:
    _DEFAULT_MODEL_CONFIG_PATH = "./config/model_config_chatgpt_default.json"
    _DEFAULT_PROMPT_CONFIG_PATH = "./config/prompt_config_default.json"
    _DEFAULT_RESPONSE_CONFIG_PATH = "./config/response_config_default.json"
    _DEFAULT_THEME_CONFIG_PATH = "./config/theme_config_default.json"

    def __init__(self) -> None:
        """
        App config is loaded based on environment variables set at runtime. Default values
        are used if an environment variable is not set.

        Loads the following configurations:
            * model_config: from the environmental variable MODEL_CONFIG_PATH
            * prompt_config: from the environmental variable PROMPT_CONFIG_PATH
            * response_config: from the environmental variable RESPONSE_CONFIG_PATH
            * theme_config: from the environmental variable THEME_CONFIG_PATH

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

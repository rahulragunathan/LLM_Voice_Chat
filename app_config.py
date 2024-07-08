import json
import os


def load_config(filepath: str):
    """
    Import filepath and load using json. Assumes filepath points
    to a json formatted input file
    """
    with open(filepath) as f:
        data = json.load(f)
    return data


class AppConfig:
    _DEFAULT_INSTALL_MODELS_CONFIG_PATH = None
    _DEFAULT_MODEL_CONFIG_PATH = "./config/model_config_tinyllama.json"
    _DEFAULT_PROMPT_CONFIG_PATH = "./config/prompt_config_tinyllama_default.json"

    def __init__(self):
        """_summary_

        App config is loaded based on environment variables set at runtime. Default values
        are used if an environment variable is not set.

        """

        install_models_config_path = os.getenv(
            "INSTALL_MODELS_CONFIG_PATH",
            AppConfig._DEFAULT_INSTALL_MODELS_CONFIG_PATH,
        )
        if install_models_config_path is not None:
            self.install_models_config = load_config(install_models_config_path)
        else:
            self.install_models_config = None

        model_config_path = os.getenv(
            "MODEL_CONFIG_PATH", AppConfig._DEFAULT_MODEL_CONFIG_PATH
        )
        self.model_config = load_config(model_config_path)

        prompt_config_path = os.getenv(
            "PROMPT_CONFIG_PATH", AppConfig._DEFAULT_PROMPT_CONFIG_PATH
        )
        self.prompt_config = load_config(prompt_config_path)
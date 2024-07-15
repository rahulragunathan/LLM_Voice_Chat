import os

import logging
from logger import AppLogger

from huggingface_hub import snapshot_download

logger = AppLogger(os.path.splitext(os.path.basename(__file__))[0]).get_logger()


def install_models(config) -> None:
    """Downloads an LLM from Huggingface

    Args:
        config (json): Configuration file that contains all relevant information for downloading file from HuggingFace
    """
    logger.info(f"Loading config from file {config}")

    for model in config["models"]:
        download_args = {}
        download_args["repo_id"] = model["model"]
        download_args["local_dir"] = model["download_path"]
        download_args["force_download"] = True
        download_args["local_dir_use_symlinks"] = False
        if "model_file" in model.keys():
            download_args["allow_patterns"] = model["model_file"]

        snapshot_download(**download_args)

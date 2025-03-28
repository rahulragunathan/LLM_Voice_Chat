import os
from time import sleep
from threading import Thread
from typing import Generator

import gradio as gr

import app_config
import model_utils as mu
import text_to_speech as ts
from logger import AppLogger

logger = AppLogger(os.path.splitext(os.path.basename(__file__))[0]).get_logger()

_DEFAULT_APP_NAME = "LLM Chat"
_DEFAULT_CHAT_PLACEHOLDER_TEXT = "Please ask me a question."
_DEFAULT_TEXTBOX_PLACEHOLDER_TEXT = "Please ask me a question."
_DEFAULT_APP_THEME = "Soft"
_DEFAULT_RESPONSE_STREAM_LAG_TIME = 0.1
_DEFAULT_RESPONSE_DELAY_TIME = 0


def load_app_theme(theme_config: dict) -> gr.themes.ThemeClass:
    """Load the application theme from the theme configuration.
        The `source_theme` property of the theme_config can be used to specify the base underlying theme, ex. 'soft', 'monochrome', etc.
        If the `source_theme` is a reference to themes available on HuggingFace, set `load_theme_from_hf_hub` to True in the theme_config.
        If the theme is being loaded from a private HuggingFace repository, you will need to set the HF_TOKEN environmental variable.

    Args:
        theme_config (dict): configuration for the Gradio app theme. Will load the "Soft" theme by default.

    Returns:
        gr.themes.ThemeClass: the theme object
    """
    source_theme_name = theme_config.get("source_theme", _DEFAULT_APP_THEME).title()
    if theme_config.get("load_theme_from_hf_hub", False):

        return gr.themes.ThemeClass.from_hub(
            repo_name=source_theme_name, hf_token=os.getenv("HF_TOKEN", None)
        )
    else:
        custom_theme_config = theme_config.copy()
        if "app_name" in custom_theme_config.keys():
            del custom_theme_config["app_name"]
        if "chat_placeholder_text" in custom_theme_config.keys():
            del custom_theme_config["chat_placeholder_text"]
        if "textbox_placeholder_text" in custom_theme_config.keys():
            del custom_theme_config["textbox_placeholder_text"]
        if "source_theme" in custom_theme_config.keys():
            del custom_theme_config["source_theme"]
        if "load_theme_from_hf_hub" in custom_theme_config.keys():
            del custom_theme_config["load_theme_from_hf_hub"]
        source_theme_class = getattr(gr.themes, source_theme_name)
        return source_theme_class(**custom_theme_config)


def get_response(
    message,
    history,
) -> Generator:
    """Get a response for the user's prompt. The response can also streamed by
    setting the following two parameters in the response configuration:
        1. response_delay_time: the number of seconds to wait before starting streaming.
        2.response_stream_lag_time: the number of seconds to lag while streaming.
        3. speech_rate_wpm: The number of words per minutes for the text-to-speech engine


    Args:
        message (str): the message to be streamed
        response_config (dict): configurations for the response

    Returns:
        Generator: the streamed response
    """

    logger.debug(f"User asked the following:\n{message}")
    response = mu.get_llm_response(
        message, history, chat_app_config.model_config, llm, system_prompt_template
    )
    logger.debug(f"Received the following response from the model:\n{response}")

    sleep(
        chat_app_config.response_config.get(
            "response_delay_time", _DEFAULT_RESPONSE_DELAY_TIME
        )
    )

    if chat_app_config.response_config.get("speak_responses", True):
        logger.debug(f"Speaking message")
        speech_thread = Thread(
            target=ts.speak_message,
            args=(response, speech_engine),
        )
        speech_thread.start()

    logger.debug(f"Streaming message")
    for i in range(len(response)):
        sleep(
            chat_app_config.response_config.get(
                "response_stream_lag_time", _DEFAULT_RESPONSE_STREAM_LAG_TIME
            )
        )
        yield response[: i + 1]


### START OF APPLICATION ###
logger.info("Initiated LLM Chat application")

# Load configurations

logger.info("Creating application configuration based on environment variables")
chat_app_config = app_config.AppConfig()
logger.info("Loaded application configuration")

logger.debug(f"Model Config:\n {chat_app_config.model_config}")
logger.debug(f"Prompt Config:\n {chat_app_config.prompt_config}")
logger.debug(f"Response Config:\n {chat_app_config.response_config}")
logger.debug(f"Theme Config:\n {chat_app_config.theme_config}")

# Load Models

logger.info("Loading model")
llm = mu.load_model(chat_app_config.model_config)
system_prompt_template = mu.load_prompt_from_config(chat_app_config.prompt_config)

if chat_app_config.response_config.get("speak_responses", True):
    logger.info("Loading text to speech engine")
    chat_app_config.response_config, speech_engine = ts.initialize_text_to_speech(
        chat_app_config.response_config
    )

gr.ChatInterface(
    get_response,
    chatbot=gr.Chatbot(
        placeholder=f"<strong>{chat_app_config.theme_config.get('chat_placeholder_text', _DEFAULT_CHAT_PLACEHOLDER_TEXT)}</strong>",
        scale=8,
    ),
    textbox=gr.Textbox(
        placeholder=f"{chat_app_config.theme_config.get('textbox_placeholder_text', _DEFAULT_TEXTBOX_PLACEHOLDER_TEXT)}",
        container=False,
        scale=2,
    ),
    title=chat_app_config.theme_config.get("app_name", _DEFAULT_APP_NAME),
    theme=load_app_theme(chat_app_config.theme_config),
    fill_height=True,
    analytics_enabled=False,
    type="messages",
).launch()

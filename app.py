import os
import time
from threading import Thread

import gradio as gr

import app_config
from logger import AppLogger

import model_utils as mu
import text_to_speech as ts

logger = AppLogger(os.path.splitext(os.path.basename(__file__))[0]).get_logger()

_DEFAULT_RESPONSE_PAUSE_TIME = 0
_DEFAULT_RESPONSE_STREAM_LAG_TIME = 0.1

# Program Start

logger.info("Initiated LLM Chat application")


# Load configurations
logger.info("Creating application configuration based on environment variables")
chat_app_config = app_config.AppConfig()
logger.info("Loaded application configuration")

logger.info("Loading model")
llm = mu.load_model(chat_app_config.model_config)
system_prompt_template = mu.load_prompt_from_config(chat_app_config.prompt_config)

logger.info("Loading text to speech engine")
chat_app_config.response_config, speech_engine = ts.initialize_text_to_speech(
    chat_app_config.response_config
)

# Display configurations
logger.debug(f"Model Config:\n {chat_app_config.model_config}")
logger.debug(f"Prompt Config:\n {chat_app_config.prompt_config}")
logger.debug(f"Response Config:\n {chat_app_config.response_config}")
logger.debug(f"Theme Config:\n {chat_app_config.theme_config}")


# Create chatbot interface


def get_response(
    message,
    history,
):
    """Get a response for the user's prompt. The response can also streamed by
    setting the following two parameters in the response configuration:
        1. response_pause_time: the number of seconds to wait before starting streaming.
        2.response_stream_lag_time: the number of seconds to lag while streaming.

    Args:
        message (str): the message to be streamed
        response_config (dict): configurations for the response

    Returns:
        str: the streamed response
    """

    logger.debug(f"User asked the following:\n{message}")
    response = mu.get_llm_response(
        message, history, chat_app_config.model_config, llm, system_prompt_template
    )
    logger.debug(f"Received the following response:\n{response}")

    sleep_time = chat_app_config.response_config.get(
        "response_pause_time", _DEFAULT_RESPONSE_PAUSE_TIME
    )

    logger.debug(f"Sleeping for {sleep_time} seconds")
    time.sleep(sleep_time)

    if chat_app_config.response_config.get("speak_responses", True):
        logger.debug(f"Speaking message")
        speech_thread = Thread(
            target=ts.speak_message,
            args=(response, chat_app_config.response_config, speech_engine),
        )
        speech_thread.start()

    logger.debug(f"Streaming message")
    for i in range(len(response)):
        time.sleep(
            chat_app_config.response_config.get(
                "response_stream_lag_time", _DEFAULT_RESPONSE_STREAM_LAG_TIME
            )
        )
        yield response[: i + 1]


gr.ChatInterface(
    get_response,
    chatbot=gr.Chatbot(
        placeholder=f"<strong>{os.getenv('CHAT_PLACEHOLDER_TEXT', 'Please ask me a question.')}</strong>",
        scale=8,
    ),
    textbox=gr.Textbox(
        placeholder=f"{os.getenv('TEXTBOX_PLACEHOLDER_TEXT', 'Please ask me a question.')}",
        container=False,
        scale=2,
    ),
    title=os.getenv("APP_NAME", "LLM Chat"),
    theme="soft",
    retry_btn=None,
    undo_btn=None,
    clear_btn=None,
    fill_height=True,
    analytics_enabled=False,
).launch()

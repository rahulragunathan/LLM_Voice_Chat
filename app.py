"""
LLM Voice Chat Application

A Gradio-based web interface for conversing with large language models (LLMs)
from OpenAI or local Ollama models. Features streaming responses with optional
text-to-speech output and customizable UI themes.

This is the main application entry point that:
- Loads configuration from JSON files (model, prompt, response, theme)
- Initializes the LLM and text-to-speech engine
- Creates and launches the Gradio chat interface
"""

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
    """Load and configure the Gradio application theme.

    Supports both built-in Gradio themes and custom themes from HuggingFace Hub.
    The theme can be customized with properties like primary_hue, font, etc.

    Theme Configuration Options:
        - source_theme: Base theme name (e.g., 'soft', 'monochrome', 'default')
        - load_theme_from_hf_hub: If True, loads theme from HuggingFace Hub
        - hf_hub_theme_name: Name of the HuggingFace Hub theme to load
        - primary_hue: Primary color hue for the theme
        - font: Font family stack for the UI
        - app_name: Application title (removed from theme config before applying)
        - chat_placeholder_text: Chat area placeholder (removed from theme config)
        - textbox_placeholder_text: Input box placeholder (removed from theme config)

    Environment Variables:
        HF_TOKEN: Required for loading themes from private HuggingFace repositories

    Args:
        theme_config (dict): Configuration dictionary for the Gradio app theme.
            Will load the "Soft" theme by default if source_theme is not specified.

    Returns:
        gr.themes.ThemeClass: Configured Gradio theme object ready to be applied
            to the ChatInterface.
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
    """Generate a streaming response from the LLM with optional text-to-speech.

    This function is the main callback for the Gradio ChatInterface. It:
    1. Sends the user's message to the LLM along with optional chat history
    2. Waits for the configured response delay time
    3. Optionally speaks the response in a separate thread using TTS
    4. Streams the response character-by-character with configurable lag time

    Response Configuration Parameters (from response_config):
        - response_delay_time: Seconds to wait before starting the response stream
        - response_stream_lag_time: Seconds to pause between each character
        - speak_responses: Boolean to enable/disable text-to-speech
        - speech_rate_wpm: Words per minute for the text-to-speech engine
        - voice_name: System voice name for text-to-speech

    The text-to-speech runs in a separate thread to avoid blocking the
    streaming UI response, allowing users to see and hear the response
    simultaneously.

    Args:
        message (str): The user's current message/question to the LLM
        history (list): Chat history in Gradio format - list of message dictionaries
            with 'role' and 'content' keys

    Yields:
        str: Progressively longer substrings of the complete response, creating
            a character-by-character streaming effect in the UI

    Returns:
        Generator: Generator that yields the streaming response text
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

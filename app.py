import os
import time

import gradio as gr

import app_config
from logger import AppLogger
import model_utils as mu
import text_to_speech as ts

logger = AppLogger(os.path.splitext(os.path.basename(__file__))[0]).get_logger()


logger.info("Initiated LLM Chat application")

logger.info("Creating application configuration based on environment variables")
chat_app_config = app_config.AppConfig()
logger.info("Loaded application configuration")
logger.debug(f"Model Config:\n {chat_app_config.model_config}")
logger.debug(f"Prompt Config:\n {chat_app_config.prompt_config}")
logger.debug(f"Theme Config:\n {chat_app_config.theme_config}")


logger.info("Loading model")
llm = mu.load_model(chat_app_config.model_config)
system_prompt_template = mu.load_prompt_from_config(chat_app_config.prompt_config)

logger.info("Loading text to speech engine")
use_mac_os_speech, speech_engine = ts.initialize_text_to_speech()


def get_response(
    message,
    history,
):

    response = mu.get_llm_response(
        message, history, chat_app_config.model_config, llm, system_prompt_template
    )
    ts.speak(
        message=response,
        use_mac_os_speech=use_mac_os_speech,
        speech_engine=speech_engine,
    )

    mu.stream_message(response)


gr.ChatInterface(
    get_response,
    chatbot=gr.Chatbot(
        placeholder=f"<strong>{os.getenv('CHAT_PLACEHOLDER_TEXT', 'Please ask me a question.')}</strong>",
    ),
    textbox=gr.Textbox(
        placeholder=f"{os.getenv('TEXTBOX_PLACEHOLDER_TEXT', 'Please ask me a question.')}",
        container=False,
        scale=7,
    ),
    title=os.getenv("APP_NAME", "Gradio Chat"),
    theme="soft",
    retry_btn=None,
    undo_btn=None,
    clear_btn=None,
).launch()

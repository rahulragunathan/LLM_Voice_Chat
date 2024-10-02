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

logger.info("Loading model")
llm = mu.load_model(chat_app_config.model_config)
system_prompt_template = mu.load_prompt_from_config(chat_app_config.prompt_config)

logger.info("Loading text to speech engine")
chat_app_config.response_config, speech_engine = ts.initialize_text_to_speech(
    chat_app_config.response_config
)


logger.debug(f"Model Config:\n {chat_app_config.model_config}")
logger.debug(f"Prompt Config:\n {chat_app_config.prompt_config}")
logger.debug(f"Response Config:\n {chat_app_config.response_config}")
logger.debug(f"Theme Config:\n {chat_app_config.theme_config}")


def get_response(
    message,
    history,
) -> None:
    """Get a response for the user's prompt.

    Args:
        message (str): the user's most recent prompt
        history (list[(str, str)]): the chat history between the user and the application
    """

    logger.debug(f"User asked the following:\n{message}")
    response = mu.get_llm_response(
        message, history, chat_app_config.model_config, llm, system_prompt_template
    )
    logger.debug(f"Received the following response:\n{response}")
    mu.stream_response(response, response_config=chat_app_config.response_config)
    ts.speak_message(
        message=response,
        speech_config=chat_app_config.response_config,
        speech_engine=speech_engine,
    )


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

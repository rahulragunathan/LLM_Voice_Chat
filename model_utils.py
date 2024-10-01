import os
import time
import openai

from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from langchain.prompts import PromptTemplate

import text_to_speech as ts


def load_prompt_from_config(prompt_config: dict) -> PromptTemplate:
    """Load prompts from config files

    Args:
        prompt_config (dict): prompt config field in config file

    Returns:
        PromptTemplate: this is the input to the LLM
    """
    return PromptTemplate(**prompt_config)


def load_model(model_config: dict):
    if (
        model_config.get("use_remote_model", False)
        and model_config["model_source"] == "OpenAI"
    ):
        return load_open_ai_model(model_config=model_config)
    else:
        raise ValueError("Model configuration not yet supported.")


def load_open_ai_model(model_config: dict) -> ChatOpenAI:
    return ChatOpenAI(
        model=model_config["model_name"], **model_config["model_parameters"]
    )


def stream_message(message):
    time.sleep(int(os.getenv("MESSAGE_PAUSE_TIME", "0")))

    message_lag = float(os.getenv("MESSAGE_LAG_TIME", "0.3"))

    for i in range(len(message)):
        time.sleep(message_lag)
        yield message[: i + 1]


def get_llm_response(message, history, model_config, llm, system_prompt_template):
    if (
        model_config.get("use_remote_model", False)
        and model_config["model_source"] == "OpenAI"
    ):

        return predict_open_ai(
            message=message,
            history=history,
            llm=llm,
            system_prompt_template=system_prompt_template,
        )
    else:
        raise ValueError("Model configuration not yet supported.")


def predict_open_ai(message, history, llm, system_prompt_template):
    history_langchain_format = []

    prompt_text = system_prompt_template.format(question=message)

    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))

    history_langchain_format.append(HumanMessage(content=prompt_text))

    gpt_response = llm(history_langchain_format)
    return gpt_response.content

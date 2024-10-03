import os
import time
import openai

from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from langchain.prompts import PromptTemplate


def load_prompt_from_config(prompt_config: dict) -> PromptTemplate:
    """Creates LangChain PromptTemplate object from dictionary

    Args:
        prompt_config (dict): dictionary containing the prompt template configuration

    Returns:
        PromptTemplate: LangChain prompt template
    """
    return PromptTemplate(**prompt_config)


def load_model(model_config: dict):
    """Load the large language model.
    Currently supported model sources: OpenAI

    Args:
        model_config (dict): a dictionary describing properties and hyperparameters for the model

    Raises:
        ValueError: if model configuration is not supported

    Returns:
        model: an instance of a loaded large language model (either remote or local)
    """
    if (
        model_config.get("use_remote_model", False)
        and model_config["model_source"] == "OpenAI"
    ):
        return _load_open_ai_model(model_config=model_config)
    else:
        raise ValueError("Model configuration not yet supported.")


def _load_open_ai_model(model_config: dict) -> ChatOpenAI:
    """Load the large language model from Open AI.

    Args:
        model_config (dict): a dictionary describing properties and hyperparameters for the model

    Returns:
        ChatOpenAI: the model from Open AI
    """
    return ChatOpenAI(
        model=model_config["model_name"], **model_config["model_parameters"]
    )


def get_llm_response(
    message: str,
    history,
    model_config: dict,
    llm,
    system_prompt_template: PromptTemplate,
) -> str:
    """Get the response from the large language model

    Args:
        message (str): the user's most recent prompt
        history (list[(str, str)]): the chat history between the user and the application
        model_config (dict): the configuration for the model
        llm: the large language model
        system_prompt_template (PromptTemplate): the system prompt template for the chat

    Raises:
        ValueError: if model configuration is not supported

    Returns:
        str: the response from the model
    """
    if (
        model_config.get("use_remote_model", False)
        and model_config["model_source"] == "OpenAI"
    ):

        return _get_open_ai_response(
            message=message,
            history=history,
            llm=llm,
            system_prompt_template=system_prompt_template,
        )
    else:
        raise ValueError("Model configuration not yet supported.")


def _get_open_ai_response(
    message: str, history, llm, system_prompt_template: PromptTemplate
) -> str:
    """Get the response from the large language model from Open AI

    Args:
        message (str): the user's most recent prompt
        history (list[(str, str)]): the chat history between the user and the application
        llm: the large language model
        system_prompt_template (PromptTemplate): the system prompt template for the chat

    Returns:
        str: the response from the OpenAI model
    """
    history_langchain_format = []

    prompt_text = system_prompt_template.format(question=message)

    for human, ai in history:
        history_langchain_format.append(HumanMessage(content=human))
        history_langchain_format.append(AIMessage(content=ai))

    history_langchain_format.append(HumanMessage(content=prompt_text))

    gpt_response = llm(history_langchain_format)
    return gpt_response.content

import subprocess
import os

from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate

from logger import AppLogger

logger = AppLogger(os.path.splitext(os.path.basename(__file__))[0]).get_logger()


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
    Currently supported model sources: OpenAI, Ollama

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
    elif (
        not model_config.get("use_remote_model", False)
        and model_config["model_source"] == "Ollama"
    ):
        _pull_ollama_model(model_config=model_config)
        return _load_ollama_model(model_config=model_config)
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


def _pull_ollama_model(model_config: dict) -> None:
    """Pull the Ollama model specified to the local repository. Ollama should already be installed.

    Args:
        model_config (dict): model configuration that includes the name of the model, e.g. tinyllama, llama3.1, etc.
    """
    subprocess.run(f"ollama pull {model_config['model_name']}", shell=True)


def _load_ollama_model(model_config: dict) -> OllamaLLM:
    """Load the Ollama model

    Args:
        model_config (dict): model configuration

    Returns:
        OllamaLLM: OllamaLLM object pointing to the model
    """
    num_gpu = (
        model_config.get("num_gpu", 1) if model_config.get("use_gpu", False) else 0
    )

    return OllamaLLM(
        model=model_config["model_name"],
        num_gpu=num_gpu,
        **model_config["model_parameters"],
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

    use_remote_model = model_config.get("use_remote_model", False)
    model_source = model_config["model_source"]
    send_chat_history = model_config.get("send_chat_history", True)

    if use_remote_model and model_source == "OpenAI":

        return _get_open_ai_response(
            message=message,
            message_history=history,
            llm=llm,
            system_prompt_template=system_prompt_template,
            send_chat_history=send_chat_history,
        )
    elif not use_remote_model and model_source == "Ollama":

        return _get_ollama_response(
            message=message,
            history=history,
            llm=llm,
            system_prompt_template=system_prompt_template,
            send_chat_history=send_chat_history,
        )
    else:
        raise ValueError("Model configuration not yet supported.")


def _get_open_ai_response(
    message: str,
    message_history,
    llm,
    system_prompt_template: PromptTemplate,
    send_chat_history: bool,
) -> str:
    """Get the response from the large language model from Open AI

    Args:
        message (str): the user's most recent prompt
        message_history (list[(str, str)]): the chat history between the user and the application
        llm: the large language model
        system_prompt_template (PromptTemplate): the system prompt template for the chat
        send_chat_history: whether to send the chat history for generating the response

    Returns:
        str: the response from the OpenAI model
    """
    message_history_list = []

    prompt_text = system_prompt_template.format(question=message)

    if send_chat_history and message_history is not None and len(message_history) > 0:
        logger.debug(
            f"Sending chat history to model. Received the following: {message_history}"
        )
        for history_message in message_history:
            message_container = (
                HumanMessage if history_message["role"] == "user" else AIMessage
            )
            message_history_list.append(
                message_container(content=history_message["content"])
            )
    message_history_list.append(HumanMessage(content=prompt_text))

    gpt_response = llm.invoke(message_history_list)
    return gpt_response.content


def _get_ollama_response(
    message: str,
    history,
    llm,
    system_prompt_template: PromptTemplate,
    send_chat_history: bool,
) -> str:
    """Get the response from the large language model from Ollama

    Args:
        message (str): the user's most recent prompt
        history (list[(str, str)]): the chat history between the user and the application
        llm: the large language model
        system_prompt_template (PromptTemplate): the system prompt template for the chat
        send_chat_history: whether to send the chat history for generating the response

    Returns:
        str: the response from the Ollama model
    """

    chain = system_prompt_template | llm
    return chain.invoke(message)

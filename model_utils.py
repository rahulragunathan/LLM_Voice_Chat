"""
Model Utilities Module

Provides utilities for loading and interacting with large language models (LLMs)
from various sources including OpenAI's GPT models and local Ollama models.

Supports:
- OpenAI models (GPT-4o, GPT-3.5-turbo, etc.) via LangChain's ChatOpenAI
- Local Ollama models (LLaMA 3.1, TinyLLaMA, DeepSeek, etc.) with GPU support
- LangChain PromptTemplate configuration and loading
- Chat history management for context-aware conversations
- Model-specific parameter configuration (temperature, top_p, etc.)
"""

import subprocess
import os

from langchain_openai import ChatOpenAI
from langchain.schema import AIMessage, HumanMessage
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate

from logger import AppLogger

logger = AppLogger(os.path.splitext(os.path.basename(__file__))[0]).get_logger()


def load_prompt_from_config(prompt_config: dict) -> PromptTemplate:
    """Create a LangChain PromptTemplate object from a configuration dictionary.

    The prompt configuration should follow LangChain's PromptTemplate format with
    keys like 'template', 'input_variables', 'template_format', etc.

    Args:
        prompt_config (dict): Dictionary containing the prompt template configuration.
            Required keys: 'template', 'input_variables'
            Optional keys: 'template_format', 'validate_template', 'output_parser', etc.

    Returns:
        PromptTemplate: Configured LangChain PromptTemplate object ready for use
            with LLM chains

    Example:
        >>> config = {
        ...     "input_variables": ["question"],
        ...     "template": "Answer this question: {question}",
        ...     "template_format": "f-string"
        ... }
        >>> prompt = load_prompt_from_config(config)
    """
    return PromptTemplate(**prompt_config)


def load_model(model_config: dict):
    """Load and initialize a large language model based on the configuration.

    Supports two model sources:
    1. OpenAI: Remote GPT models (GPT-4o, GPT-3.5-turbo, etc.)
    2. Ollama: Local open-source models (LLaMA 3.1, TinyLLaMA, DeepSeek, etc.)

    For Ollama models, this function will automatically pull the model from the
    Ollama registry if it's not already available locally.

    Configuration Parameters:
        - use_remote_model: True for OpenAI, False for Ollama
        - model_source: "OpenAI" or "Ollama"
        - model_name: Model identifier (e.g., "gpt-4o", "llama3.1")
        - model_parameters: Dict of model-specific parameters (temperature, top_p, etc.)
        - use_gpu: (Ollama only) Enable GPU acceleration
        - num_gpu: (Ollama only) Number of GPUs to use

    Args:
        model_config (dict): Dictionary describing model properties and hyperparameters.
            Must include 'use_remote_model', 'model_source', 'model_name', and
            'model_parameters' keys.

    Raises:
        ValueError: If the model configuration specifies an unsupported combination
            of use_remote_model and model_source

    Returns:
        ChatOpenAI | OllamaLLM: An initialized LLM instance ready for inference

    Example:
        >>> config = {
        ...     "use_remote_model": True,
        ...     "model_source": "OpenAI",
        ...     "model_name": "gpt-4o",
        ...     "model_parameters": {"temperature": 1.0}
        ... }
        >>> llm = load_model(config)
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
    """Load a large language model from OpenAI's API.

    Requires the OPENAI_API_KEY environment variable to be set with a valid API key.

    Args:
        model_config (dict): Dictionary containing:
            - model_name: OpenAI model identifier (e.g., "gpt-4o", "gpt-3.5-turbo")
            - model_parameters: Dict with parameters like temperature, max_tokens, etc.

    Returns:
        ChatOpenAI: Initialized OpenAI model instance configured with the specified
            model name and parameters

    Environment Variables:
        OPENAI_API_KEY: Your OpenAI API key (required)
    """
    return ChatOpenAI(
        model=model_config["model_name"], **model_config["model_parameters"]
    )


def _pull_ollama_model(model_config: dict) -> None:
    """Pull an Ollama model to the local repository if not already present.

    This function executes the 'ollama pull' command to download the specified
    model from the Ollama registry. If the model is already present locally,
    Ollama will skip the download.

    Prerequisites:
        - Ollama must be installed and accessible via the command line
        - Ollama service should be running (typically at localhost:11434)

    Args:
        model_config (dict): Model configuration containing:
            - model_name: Name of the Ollama model (e.g., "tinyllama", "llama3.1",
              "deepseek-coder", "phi", etc.)

    Note:
        This function runs synchronously and may take several minutes for large
        models. The model is downloaded to Ollama's local model storage.
    """
    subprocess.run(f"ollama pull {model_config['model_name']}", shell=True)


def _load_ollama_model(model_config: dict) -> OllamaLLM:
    """Load and configure a local Ollama model with optional GPU acceleration.

    GPU support is automatically configured based on the model configuration:
    - If use_gpu is True, num_gpu defaults to 1
    - If use_gpu is False or not specified, GPU is disabled (num_gpu=0)

    Args:
        model_config (dict): Model configuration containing:
            - model_name: Ollama model identifier (e.g., "llama3.1", "tinyllama")
            - model_parameters: Dict of model parameters (top_k, top_p, temperature, etc.)
            - use_gpu: Boolean to enable/disable GPU acceleration (optional)
            - num_gpu: Number of GPUs to use (optional, defaults to 1 if use_gpu is True)

    Returns:
        OllamaLLM: Initialized Ollama LLM instance configured with the specified
            model and parameters, ready for local inference

    Example:
        >>> config = {
        ...     "model_name": "llama3.1",
        ...     "use_gpu": True,
        ...     "num_gpu": 1,
        ...     "model_parameters": {"temperature": 0.8, "top_p": 0.9}
        ... }
        >>> llm = _load_ollama_model(config)
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
    """Get a response from the LLM for the user's message.

    Routes the request to the appropriate handler based on the model configuration.
    Supports optional chat history for context-aware conversations.

    The function formats the user's message using the system prompt template and
    optionally includes previous conversation history before sending to the model.

    Supported Model Sources:
        - OpenAI (use_remote_model=True, model_source="OpenAI")
        - Ollama (use_remote_model=False, model_source="Ollama")

    Args:
        message (str): The user's current message/question
        history (list): Chat history in Gradio format - list of message dictionaries
            with 'role' and 'content' keys. Can be None or empty.
        model_config (dict): Model configuration containing:
            - use_remote_model: Boolean indicating remote (True) or local (False)
            - model_source: "OpenAI" or "Ollama"
            - send_chat_history: Whether to include conversation history
        llm (ChatOpenAI | OllamaLLM): Initialized LLM instance
        system_prompt_template (PromptTemplate): LangChain template for formatting
            the user's message with any system instructions

    Raises:
        ValueError: If the model configuration specifies an unsupported combination
            of use_remote_model and model_source

    Returns:
        str: The complete text response from the LLM

    Example:
        >>> response = get_llm_response(
        ...     message="What is Python?",
        ...     history=[],
        ...     model_config={"use_remote_model": True, "model_source": "OpenAI"},
        ...     llm=openai_model,
        ...     system_prompt_template=prompt
        ... )
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
    """Get a response from an OpenAI model with optional chat history.

    Formats the conversation history into LangChain message objects (HumanMessage
    and AIMessage) and sends them to the OpenAI model. The system prompt template
    is applied to the current user message.

    Args:
        message (str): The user's current message/question
        message_history (list): Chat history in Gradio format - list of message
            dictionaries with 'role' ('user' or 'assistant') and 'content' keys.
            Can be None or empty.
        llm (ChatOpenAI): Initialized OpenAI model instance
        system_prompt_template (PromptTemplate): Template for formatting the user's
            message with system instructions
        send_chat_history (bool): If True, includes full conversation history in
            the request. If False, only sends the current message.

    Returns:
        str: The text response from the OpenAI model (extracted from AIMessage.content)

    Note:
        Chat history is converted from Gradio's message format to LangChain's
        message schema (HumanMessage for user, AIMessage for assistant) before
        being sent to the model.
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
    """Get a response from a local Ollama model with optional chat history.

    Creates a LangChain chain by composing the prompt template with the Ollama LLM.
    If chat history is enabled, it formats the conversation history into a
    single context string and includes it with the current message.

    Args:
        message (str): The user's current message/question
        history (list): Chat history in Gradio format - list of message
            dictionaries with 'role' ('user' or 'assistant') and 'content' keys.
            Can be None or empty.
        llm (OllamaLLM): Initialized Ollama model instance
        system_prompt_template (PromptTemplate): Template for formatting the user's
            message with system instructions
        send_chat_history (bool): If True, includes full conversation history in
            the request. If False, only sends the current message.

    Returns:
        str: The text response from the Ollama model

    Note:
        Chat history is formatted as a conversation context string that is
        prepended to the current question in the template. This provides
        context-aware responses similar to the OpenAI implementation.
    """
    # Build conversation context if history is enabled
    conversation_context = ""
    if send_chat_history and history is not None and len(history) > 0:
        logger.debug(
            f"Sending chat history to model. Received the following: {history}"
        )
        conversation_parts = []
        for history_message in history:
            role = (
                "User" if history_message["role"] == "user" else "Assistant"
            )
            content = history_message["content"]
            conversation_parts.append(f"{role}: {content}")

        conversation_context = (
            "Previous conversation:\n" + "\n".join(conversation_parts) + "\n\n"
        )

    # Combine conversation context with current message
    full_message = conversation_context + message

    chain = system_prompt_template | llm
    return chain.invoke(full_message)

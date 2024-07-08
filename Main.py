import os
import streamlit as st
import time

import app_config
import install_models as im
import model_utils as mu
from logger import AppLogger

logger = AppLogger(os.path.splitext(os.path.basename(__file__))[0]).get_logger()

def setup_app():

    # read configs from the environment
    if "model_config" not in st.session_state.keys() or "prompt_config" not in st.session_state.keys() or "install_models_config" not in st.session_state.keys():

        logger.info("Creating app config from environment")
        chat_app_config = app_config.AppConfig()

        model_config = chat_app_config.model_config
        prompt_config = chat_app_config.prompt_config
        install_models_config = chat_app_config.install_models_config

        logger.info("Loaded application config")
        logger.debug(f"Install Models Config:\n {install_models_config}")
        logger.debug(f"Model Config:\n {model_config}")
        logger.debug(f"Prompt Config:\n {prompt_config}")

        # install models (if applicable)
        if install_models_config is not None:
            # im.install_models(install_models_config)
            logger.info("Downloaded and installed models")

    else:
        logger.debug("Using previously loaded config")
        model_config = st.session_state.model_config
        prompt_config = st.session_state.prompt_config

    # initialize or connect to model
    # build llm query chain from prompt config
    if "llm_prompt" not in st.session_state.keys():
        logger.info("Loading prompt")
        # st.session_state.llm_prompt = mu.load_prompt_from_config(prompt_config)

    if "llm_pipeline" not in st.session_state.keys():
        logger.info("Creating LLM pipelines")
        # st.session_state.llm_pipeline = mu.create_pipelines(model_config)

    # initialize chat history
    if "messages" not in st.session_state.keys():
        st.session_state.messages = []


def generate_response(query: str):
    response = f"RESPONSE: {query}" 
    # response = mu.query_llm_pipeline(query, st.session_state.llm_pipeline, st.session_state.model_config, st.session_state.llm_prompt)
    return response


def stream_response(response: str, delay_time:float = 0.05):
    # stream response with delay
    for word in response.split():
        yield word + " "
        time.sleep(delay_time)


def display_response(response: str):
    st.write_stream(stream_response(response))


def speak_response(response: str):

    # check is 'say' command available (built in to MacOS)
    # os.system(f"say -v Fred {response}")
    
    st.markdown(f"SPEAK: {response}")


logger.info("Initiated LLM Chat application")
setup_app()

st.title(os.getenv("APP_NAME", "LLM Chat"))

# display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# react to user input
if prompt := st.chat_input(os.getenv("INITIAL_CHAT_PROMPT", "How can I assist you?")):

    # display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    # add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

    # on input:
    # 1. generate response from our LLM
    # 2. in parallel threads:
    # - i. stream the response to user with delay
    # - ii. speak the response
    response = generate_response(prompt)
    with st.chat_message("assistant"):
        display_response(response)
        speak_response(response)

    # add the response to chat history
    st.session_state.messages.append({"role": "assistant", "content": response})
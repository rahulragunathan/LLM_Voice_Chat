import os
import streamlit as st
from pathlib import Path
import torch
from openai import OpenAI
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
)
from auto_gptq import AutoGPTQForCausalLM, BaseQuantizeConfig
from langchain.prompts import PromptTemplate
from langchain.llms import HuggingFacePipeline, LlamaCpp
from langchain.prompts import PromptTemplate

from logger import AppLogger

logger = AppLogger(os.path.splitext(os.path.basename(__file__))[0]).get_logger()

_SUPPORTED_REMOTE_MODELS = ["chatgpt"]


@st.cache_resource
def load_prompt_from_config(prompt_config: dict) -> PromptTemplate:
    """Load prompts from config files

    Args:
        prompt_config (dict): prompt config field in config file

    Returns:
        PromptTemplate: this is the input to the LLM
    """    
    return PromptTemplate(**prompt_config)


@st.cache_resource
def create_pipelines(model_config: dict):
    """Generate a HuggingFace LLM pipeline from config files. 

    Args:
        model_config (dict): model config file

    Returns:
        llm_pipeline: Returns an instance from the build_llm_ppeline function
    """    

    if model_config.get("load_w_llama_cpp", False):

        logger.info("Loading LLM using Llama CPP")
        llm_pipeline = load_llama_cpp_model(model_config["model_path"], model_config["llm_pipeline_kwargs"])
        logger.info("Finished loading LLM using Llama CPP")

    elif not model_config.get("load_w_llama_cpp", False) and model_config.get("use_gpu", False):

        logger.info("Loading LLM using GPU")

        logger.info("Loading Tokenizer")
        llm_tokenizer = load_tokenizer(model_config["tokenizer_dir"])

        logger.info("Loading LLM")
        llm_model = load_llm_model(
            model_config["model_dir"],
            model_config["use_gpu"],
        )

        logger.info("Building LLM Pipeline")
        llm_pipeline = build_llm_pipeline(
            llm_model, llm_tokenizer, model_config["llm_pipeline_kwargs"]
        )
        logger.info("Finished Loading LLM using GPU")

    elif model_config.get("use_remote_model", False) and model_config.get("remote_model_source", "").lower() in _SUPPORTED_REMOTE_MODELS:

        logger.info("Connecting to remote model")
        load_remote_model(model_config)
        llm_pipeline = None
        logger.info("Loaded remote model")

    else:
        raise ValueError("Model not currently supported. Exiting.")

    return llm_pipeline

@st.cache_resource
def load_tokenizer(tokenizer_path):
    """Loads and returns model Autotokenizer 

    Args:
        tokenizer_path (str): Path to tokenizer

    Returns:
        Autotokenizer: LLM tokenizer
    """    
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    logger.info(f"Loading tokenizer from path {tokenizer_path}")
    tokenizer = AutoTokenizer.from_pretrained(tokenizer_path)

    if tokenizer.pad_token is None:
        tokenizer.add_special_tokens({"pad_token": "[PAD]"})
    
    return tokenizer

@st.cache_resource
def load_llm_model(model_path: str, use_gpu: bool = False):
    """Generate instancce of a model from config files. Built in test for detecting if model is quantized or reduced in size (8-bit).

    Args:
        model_path (str): path to model
        use_gpu (bool, optional): Variable to use GPU or CPU. Defaults to False.

    Returns:
        Hugging Face LAnguage Model: An instance of the Huggingface Model from Config file
    """    
    eight_bit = False
    quantized = False

    if "GPTQ" in model_path:
        quantized = True

    if "-HF" in model_path:
        eight_bit = True

    if not quantized:
        logger.info("Acquiring Non-Quantized Model")
        try:
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                load_in_8bit=eight_bit,
                device_map="auto",
                torch_dtype=torch.float16 if eight_bit else torch.float32,
            )
        # model=AutoModelForCausalLM.from_pretrained(model_path)
        except OSError:
            model = AutoModelForCausalLM.from_pretrained(model_path, from_tf=True)

        if use_gpu and not eight_bit:
            logger.info("model halved")
            model.half().cuda()

    else:
        logger.info("Acquired Quantized Model")
        ## Get quant model config settings
        quantize_config = BaseQuantizeConfig().from_pretrained(model_path)
        ## Get model file and dependent config
        model_file_config = get_quant_file(model_path, use_gpu=use_gpu)
        # Combine configs
        model_config = model_file_config | quantize_config.to_dict()
        # Load model
        model_config["model_name_or_path"] = model_path
        model = AutoGPTQForCausalLM.from_quantized(**model_config)
        if use_gpu:
            model.cuda()

    return model


@st.cache_resource
def get_quant_file(
    model_dir: str,
    safetensors: bool = False,
    use_gpu: bool = False,
    run_strict: bool = False,
):
    """Function to return the parameters of a quantized model

    Args:
        model_dir (str): Path to model
        safetensors (bool, optional): Format of tensors to use, Safetensors if True. Defaults to False.
        use_gpu (bool, optional): Device to use, GPU if True else CPU. Defaults to False.
        run_strict (bool, optional): Paramet . Defaults to False.

    Returns:
        dict: Parameters of model
    """    
    weight_path = None
    for ext in [".safetensors", ".pt", ".bin"]:
        path_to_model = Path(model_dir)
        found = list(path_to_model.glob(f"*{ext}"))
        if len(found) > 0:
            if len(found) > 1:
                logger.info("More than one quant file found, choosing last.")
            weight_path = found[-1]
            break
    if weight_path is None:
        logger.warning("No weights found")
        return
    logger.info(f"Model File Path: {weight_path}")
    if weight_path.suffix == ".safetensors":
        logger.info("Safetensor model found, setting use_safetensors to True in config")
        safetensors = True
    if weight_path.suffix.split(".")[-1] == "act-order":
        logger.info("Act order found setting strict to False")
        run_strict = False

    params = {
        "model_basename": weight_path.stem,
        "use_safetensors": safetensors,
        "device": "cuda:0" if use_gpu else "cpu",
        "strict": run_strict,
    }

    return params


@st.cache_resource
def load_llama_cpp_model(model_path: dict, model_kwargs):
    """Loads an instance of a Llamma CPP mdel

    Args:
        model_path (dict): Path to model
        model_kwargs (_type_): Key word arguments

    Returns:
        LlamaCpp: instance of a LlamaCpp model
    """    
    llm_model = LlamaCpp(model_path=model_path, **model_kwargs)

    return llm_model


@st.cache_resource
def build_llm_pipeline(
    llm_model, llm_tokenizer, model_kwargs, pipeline_type="text-generation"
):
    """_summary_

    Args:
        llm_model (model): Large Language model
        llm_tokenizer (Autotokenizer): Large language Autotokenizer instance
        model_kwargs (_type_): key word arguments for LLM
        pipeline_type (str, optional): Pipeline type. Defaults to "text-generation".

    Returns:
        model: instance of the large language model.
    """    

    """pipe = pipeline(
    model=model,
    tokenizer=tokenizer,
    max_length=3000,
    temperature=0,
    top_p=0.95,
    repetition_penalty=1.15)
    """

    pipe = pipeline(
        pipeline_type, model=llm_model, tokenizer=llm_tokenizer, **model_kwargs
    )
    local_llm = HuggingFacePipeline(pipeline=pipe)

    return local_llm


@st.cache_resource
def get_openai_client(api_key):
    return OpenAI(api_key)


def load_remote_model(model_config: dict):

    if model_config.get("remote_model_source").lower() == "chatgpt":
        st.session_state.openai_client = get_openai_client(os.getenv("OPENAI_API_KEY"), None)
        st.session_state.openai_model = "gpt-3.5-turbo"


def get_remote_model_response(prompt, model_config):
    
    if model_config.get("remote_model_source").lower() == "chatgpt":     
        # TODO: FOR NOW, NOT USING MEMORY FOR CHATGPT
        client = st.session_state.openai_client
        response = client.chat.completions.create(
                    model=st.session_state.openai_model,
                    messages=[{"role": "user", "content": prompt}],
                    stream=False,
                )
    
    return response

def query_llm_pipeline(query, llm_pipeline, model_config, model_prompt):
    """Function to send prompt to llm pipeline and return an llm response.

    Args:
        query_text (str): Text of the users query
        llm_pipeline (pipeline): Huggingface llm pipeline
        model_config (dict): config for the LLM
        model_prompt (str): prompt for the LLM from the prompt config file

    Returns:
        dict: response from the llm given a query
    """    
    prompt_text = model_prompt.format(input_text=query)

    if model_config.get("use_remote_model", False):
        llm_response = get_remote_model_response(prompt_text, model_config)
    else:
        llm_response = llm_pipeline(prompt_text)

    return llm_response
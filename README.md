# LLM Voice Chat

A Python frontend (built using Gradio and LangChain) for talking to ChatGPT or any local model of your choosing. Features a web-based chat interface with optional text-to-speech to hear responses out loud in a robot voice!

## Features

- **Multiple LLM Sources**: Support for OpenAI models (GPT-4o, GPT-3.5-turbo, etc.) and local models via Ollama (LLaMA 3.1, TinyLLaMA, DeepSeek, etc.)
- **Text-to-Speech**: Optional voice output with configurable speech rate and platform-specific voice selection
- **Streaming Responses**: Real-time streaming of LLM responses with configurable typing effect
- **Customizable UI**: Gradio-based interface with theme customization and branding options
- **Flexible Configuration**: JSON-based configuration system for models, prompts, responses, and themes
- **Chat History**: Optional conversation history for context-aware responses
- **GPU Support**: Accelerated inference for local Ollama models

## Prerequisites

### LLM Providers

You can use LLMs from the following sources:

- **[Ollama](https://ollama.com/)** - For running local open-source models
- **OpenAI** - For cloud-based GPT models

To use OpenAI models, you will need to create an [OpenAI API Key](https://platform.openai.com/api-keys) and have credits to access your model of choice.
**Note: This is NOT the same as upgrading to a ChatGPT paid plan (ChatGPT Plus, Pro, etc.).**

### Python Environment

Python 3.11+ is recommended. Using a Python virtual environment is strongly recommended.

Install the required libraries in your Python environment:

```bash
pip install -r requirements.txt
```

**Dependencies:**
- gradio==5.31.0
- openai==1.56.1
- langchain==0.3.9
- langchain-openai==0.2.10
- langchain-community==0.3.27
- langchain-ollama==0.2.1
- pyttsx3==2.98

## Project Structure

```
LLM_Voice_Chat/
├── app.py                          # Main application entry point
├── app_config.py                   # Configuration loader
├── model_utils.py                  # LLM loading and response logic
├── text_to_speech.py              # Text-to-speech engine
├── logger.py                       # Logging utility
├── requirements.txt                # Python dependencies
├── start_app.sh                    # Bash startup script
├── start_app.bat                   # Windows startup script
├── config/                         # Default configuration templates
│   ├── model_config_chatgpt_default.json
│   ├── model_config_ollama_llama3.1.json
│   ├── model_config_ollama_tinyllama.json
│   ├── prompt_config_default.json
│   ├── response_config_default.json
│   └── theme_config_default.json
└── test/
    └── check_voices.ipynb          # Utility to check available TTS voices
```

## Configuration

The application uses four JSON configuration files controlled via environment variables:

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required
MODEL_CONFIG_PATH=./config/model_config_chatgpt_default.json
PROMPT_CONFIG_PATH=./config/prompt_config_default.json
RESPONSE_CONFIG_PATH=./config/response_config_default.json
THEME_CONFIG_PATH=./config/theme_config_default.json

# Required for OpenAI models only
OPENAI_API_KEY=your-api-key-here

# Optional (defaults to INFO)
APP_LOG_LEVEL=DEBUG
```

### Configuration Files

#### 1. Model Configuration

Controls which LLM to use and its parameters.

**OpenAI Example** (`model_config_chatgpt_default.json`):
```json
{
    "use_remote_model": true,
    "model_source": "OpenAI",
    "model_name": "gpt-4o",
    "model_parameters": {
        "temperature": 1.0
    },
    "send_chat_history": true
}
```

**Ollama Example** (`model_config_ollama_llama3.1.json`):
```json
{
    "use_remote_model": false,
    "model_source": "Ollama",
    "model_name": "llama3.1",
    "use_gpu": true,
    "num_gpu": 1,
    "model_parameters": {
        "top_k": 40,
        "top_p": 0.9,
        "temperature": 0.8,
        "min_p": 0.0,
        "repeat_penalty": 1.18
    },
    "send_chat_history": true
}
```

**Available Parameters:**
- `use_remote_model`: `true` for OpenAI, `false` for Ollama
- `model_source`: `"OpenAI"` or `"Ollama"`
- `model_name`: Model identifier (e.g., `"gpt-4o"`, `"llama3.1"`)
- `model_parameters`: Model-specific parameters (temperature, top_p, etc.)
- `send_chat_history`: Whether to send conversation history for context
- `use_gpu`: Enable GPU acceleration (Ollama only)
- `num_gpu`: Number of GPUs to use (Ollama only)

#### 2. Prompt Configuration

Defines the system prompt template using LangChain's PromptTemplate format.

**Example** (`prompt_config_default.json`):
```json
{
    "input_variables": ["question"],
    "output_parser": null,
    "partial_variables": {},
    "template": "{question}",
    "template_format": "f-string",
    "validate_template": true
}
```

You can customize the template to add system instructions:
```json
{
    "input_variables": ["question"],
    "template": "You are a helpful assistant. Answer the following question: {question}",
    "template_format": "f-string"
}
```

#### 3. Response Configuration

Controls text-to-speech and response streaming behavior.

**Example** (`response_config_default.json`):
```json
{
    "speak_responses": true,
    "response_delay_time": 3,
    "response_stream_lag_time": 0.04,
    "voice_name": "Fred",
    "speech_rate_wpm": 140
}
```

**Parameters:**
- `speak_responses`: Enable/disable text-to-speech (`true`/`false`)
- `response_delay_time`: Delay in seconds before starting response
- `response_stream_lag_time`: Delay between characters for typing effect (seconds)
- `voice_name`: System voice name (platform-specific)
- `speech_rate_wpm`: Speech rate in words per minute

**Platform-specific default voices:**
- macOS: `"Samantha"`
- Windows: `"Microsoft David Desktop"`
- Linux: First available voice

To check available voices on your system, see [test/check_voices.ipynb](test/check_voices.ipynb).

#### 4. Theme Configuration

Customizes the Gradio UI appearance.

**Example** (`theme_config_default.json`):
```json
{
    "app_name": "LLM Chat",
    "chat_placeholder_text": "Please ask me a question.",
    "textbox_placeholder_text": "Please ask me a question.",
    "source_theme": "soft",
    "load_theme_from_hf_hub": false,
    "hf_hub_theme_name": null,
    "primary_hue": "red",
    "font": ["IBM Plex Mono", "ui-monospace", "Consolas", "monospace"]
}
```

**Parameters:**
- `app_name`: Application title displayed in the UI
- `chat_placeholder_text`: Placeholder for chat history area
- `textbox_placeholder_text`: Placeholder for input textbox
- `source_theme`: Built-in Gradio theme (e.g., `"soft"`, `"default"`, `"monochrome"`)
- `load_theme_from_hf_hub`: Load custom theme from HuggingFace Hub
- `hf_hub_theme_name`: HuggingFace Hub theme name (if loading from hub)
- `primary_hue`: Primary color hue
- `font`: Font family stack for the UI

## Starting the Application

Use the provided startup script for your operating system:

**On macOS and Linux:**
```bash
./start_app.sh path/to/env/file
```

**On Windows:**
```cmd
.\start_app.bat path/to/env/file
```

**Example:**
```bash
./start_app.sh env/soothsayers/soothsayers_chatgpt.env
```

The script will:
1. Load environment variables from the specified `.env` file
2. Launch the Gradio web interface
3. Open the application in your default browser

## Usage

1. Once the application starts, a browser window will open with the chat interface
2. Type your question or message in the input textbox
3. Press Enter or click Submit
4. The LLM response will stream in real-time
5. If text-to-speech is enabled, the response will be spoken aloud
6. Chat history is maintained during the session (if enabled in model config)

## Troubleshooting

### OpenAI API Issues
- Ensure your API key is valid and has available credits
- Check that `OPENAI_API_KEY` is correctly set in your `.env` file

### Ollama Connection Issues
- Verify Ollama is installed and running: `ollama list`
- Pull the desired model: `ollama pull llama3.1`
- Check Ollama is accessible at `http://localhost:11434`

### Text-to-Speech Issues
- On Linux, you may need to install espeak: `sudo apt-get install espeak`
- On macOS/Windows, TTS should work out of the box
- Check available voices using the notebook in [test/check_voices.ipynb](test/check_voices.ipynb)

### Logging
Set `APP_LOG_LEVEL=DEBUG` in your `.env` file for detailed logging output.

## License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2024 Rahul Ragunathan
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
├── config_validator.py             # Configuration validation
├── model_utils.py                  # LLM loading and response logic
├── text_to_speech.py              # Text-to-speech engine
├── logger.py                       # Logging utility
├── requirements.txt                # Python dependencies
├── start_app.sh                    # Bash startup script
├── start_app.bat                   # Windows startup script
├── config/                         # Configuration files
│   ├── unified_config_example.json       # OpenAI example config
│   └── unified_config_ollama_example.json # Ollama example config
├── tests/                          # Test suite
│   ├── test_config_validator.py
│   └── test_app_config.py
└── test/
    └── check_voices.ipynb          # Utility to check available TTS voices
```

## Configuration

The application uses a unified JSON configuration file that contains all settings organized in sections: model, prompt, response, and theme.

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Required: Path to unified configuration file
CONFIG_PATH=./config/unified_config_example.json

# Required for OpenAI models only
OPENAI_API_KEY=your-api-key-here

# Optional (defaults to INFO)
APP_LOG_LEVEL=DEBUG
```

### Unified Configuration File

All application settings are stored in a single JSON file with the following structure:

```json
{
  "app_name": "LLM Voice Chat",
  "version": "1.0.0",
  "model": { ... },
  "prompt": { ... },
  "response": { ... },
  "theme": { ... }
}
```

#### OpenAI Example

See [config/unified_config_example.json](config/unified_config_example.json):

```json
{
  "app_name": "LLM Voice Chat",
  "version": "1.0.0",
  "model": {
    "use_remote_model": true,
    "model_source": "OpenAI",
    "model_name": "gpt-4o",
    "model_parameters": {
      "temperature": 1.0
    },
    "send_chat_history": true
  },
  "prompt": {
    "input_variables": ["question"],
    "template": "{question}",
    "template_format": "f-string"
  },
  "response": {
    "speak_responses": true,
    "response_delay_time": 3,
    "response_stream_lag_time": 0.04,
    "voice_name": "Samantha",
    "speech_rate_wpm": 140
  },
  "theme": {
    "chat_placeholder_text": "Please ask me a question.",
    "textbox_placeholder_text": "Please ask me a question.",
    "source_theme": "soft",
    "load_theme_from_hf_hub": false,
    "primary_hue": "red",
    "font": ["IBM Plex Mono", "ui-monospace", "Consolas", "monospace"]
  }
}
```

#### Ollama Example

See [config/unified_config_ollama_example.json](config/unified_config_ollama_example.json):

```json
{
  "app_name": "LLM Voice Chat - Ollama",
  "version": "1.0.0",
  "model": {
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
  },
  "prompt": {
    "input_variables": ["question"],
    "template": "{question}",
    "template_format": "f-string"
  },
  "response": {
    "speak_responses": false,
    "response_delay_time": 0,
    "response_stream_lag_time": 0.02
  },
  "theme": {
    "chat_placeholder_text": "Ask me anything...",
    "textbox_placeholder_text": "Type your question here...",
    "source_theme": "soft",
    "load_theme_from_hf_hub": false
  }
}
```

### Configuration Sections

#### Model Configuration

Controls which LLM to use and its parameters.

**Available Parameters:**
- `use_remote_model`: `true` for OpenAI, `false` for Ollama
- `model_source`: `"OpenAI"` or `"Ollama"`
- `model_name`: Model identifier (e.g., `"gpt-4o"`, `"llama3.1"`)
- `model_parameters`: Model-specific parameters (temperature, top_p, etc.)
- `send_chat_history`: Whether to send conversation history for context
- `use_gpu`: Enable GPU acceleration (Ollama only)
- `num_gpu`: Number of GPUs to use (Ollama only)

#### Prompt Configuration

Defines the system prompt template using LangChain's PromptTemplate format.

**Available Parameters:**
- `input_variables`: List of variable names used in template
- `template`: Prompt template string with placeholders
- `template_format`: Template format (usually `"f-string"`)
- `output_parser`: Optional output parser (usually `null`)
- `partial_variables`: Optional partial variable substitutions
- `validate_template`: Whether to validate template variables

**Customization Example:**
```json
"prompt": {
  "input_variables": ["question"],
  "template": "You are a helpful assistant. Answer the following question: {question}",
  "template_format": "f-string"
}
```

#### Response Configuration

Controls text-to-speech and response streaming behavior.

**Available Parameters:**
- `speak_responses`: Enable/disable text-to-speech (`true`/`false`)
- `response_delay_time`: Delay in seconds before starting response
- `response_stream_lag_time`: Delay between characters for typing effect (seconds)
- `voice_name`: System voice name (platform-specific, optional)
- `speech_rate_wpm`: Speech rate in words per minute (optional)

**Platform-specific default voices:**
- macOS: `"Samantha"`
- Windows: `"Microsoft David Desktop"`
- Linux: First available voice

To check available voices on your system, see [test/check_voices.ipynb](test/check_voices.ipynb).

#### Theme Configuration

Customizes the Gradio UI appearance.

**Available Parameters:**
- `app_name`: Application title displayed in the UI (optional, defaults to top-level app_name)
- `chat_placeholder_text`: Placeholder for chat history area
- `textbox_placeholder_text`: Placeholder for input textbox
- `source_theme`: Built-in Gradio theme (e.g., `"soft"`, `"default"`, `"monochrome"`)
- `load_theme_from_hf_hub`: Load custom theme from HuggingFace Hub
- `hf_hub_theme_name`: HuggingFace Hub theme name (if loading from hub, optional)
- `primary_hue`: Primary color hue (optional)
- `font`: Font family stack for the UI (optional)

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

## Testing

Run the test suite to verify your installation:

```bash
pytest
```

Or with verbose output:

```bash
pytest -v
```

Tests cover:
- Configuration validation
- Configuration loading
- Error handling

## Recent Improvements

- **Security**: Removed exposed API keys and added .env.example templates
- **Feature**: Chat history now works for both OpenAI and Ollama models
- **Feature**: Unified configuration format for simpler setup
- **Quality**: Automatic configuration validation on startup with clear error messages
- **Quality**: Comprehensive error handling throughout the application
- **Testing**: Unit test suite for core functionality
- **Documentation**: Complete docstrings for all modules and functions

See [CHANGELOG.md](CHANGELOG.md) for full version history.

## License

MIT License - see [LICENSE](LICENSE) for details.

Copyright (c) 2024 Rahul Ragunathan

## Contributing

Contributions are welcome! Please feel free to submit issues or pull requests.

### Setup for Development

1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate the virtual environment
4. Install dependencies: `pip install -r requirements.txt`
5. Copy `.env.example` to `.env` and configure
6. Run tests: `pytest`
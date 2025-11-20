"""
Text-to-Speech Module

Provides text-to-speech functionality using the pyttsx3 library for speaking
LLM responses aloud. Supports platform-specific voice selection and configurable
speech rate.

Features:
- Cross-platform TTS support (Windows, macOS, Linux)
- Configurable voice selection by name
- Adjustable speech rate in words per minute (WPM)
- Platform-aware default voice selection
- Thread-safe speech engine management

Platform-specific defaults:
- Windows: "Microsoft David Desktop - English (United States)"
- macOS: "Samantha"
- Linux: First available system voice
"""

import pyttsx3
import os
import subprocess
import platform

from logger import AppLogger

logger = AppLogger(os.path.splitext(os.path.basename(__file__))[0]).get_logger()

_DEFAULT_SPEECH_RATE_WPM = 180
_DEFAULT_WINDOWS_VOICE = "Microsoft David Desktop - English (United States)"
_DEFAULT_MAC_OS_VOICE = "Samantha"


def initialize_text_to_speech(
    speech_config: dict,
) -> tuple[dict, pyttsx3.Engine]:
    """Initialize the pyttsx3 text-to-speech engine with platform-specific configuration.

    Creates and configures a pyttsx3 TTS engine with the specified voice and speech
    rate. Automatically selects platform-appropriate default voices if not specified
    in the configuration.

    Configuration Parameters:
        - voice_name: Name of the system voice to use (optional, platform-dependent)
        - speech_rate_wpm: Speech rate in words per minute (optional, defaults to 180)

    Platform-specific behavior:
        - Windows: Uses "Microsoft David Desktop" voice by default
        - macOS: Uses "Samantha" voice by default
        - Linux: Uses first available voice by default

    Args:
        speech_config (dict): Configuration dictionary for text-to-speech containing:
            - voice_name (str, optional): System voice name
            - speech_rate_wpm (int, optional): Words per minute for speech rate

    Returns:
        tuple[dict, pyttsx3.Engine]: A tuple containing:
            - The updated speech configuration dictionary
            - Initialized and configured pyttsx3 Engine instance

    Note:
        On Linux systems, espeak must be installed for TTS to work:
        sudo apt-get install espeak

    Example:
        >>> config = {"voice_name": "Samantha", "speech_rate_wpm": 150}
        >>> updated_config, engine = initialize_text_to_speech(config)
    """
    if running_on_windows():
        logger.debug("Using pystxx3 speech on Windows")
        voice_name = speech_config.get("voice_name", _DEFAULT_WINDOWS_VOICE)
    elif running_on_mac_os():
        logger.debug("Using pystxx3 speech on Mac")
        voice_name = speech_config.get("voice_name", _DEFAULT_MAC_OS_VOICE)
    else:
        logger.debug("Using pystxx3 speech on Unix")
        voice_name = speech_config.get("voice_name", None)

    # create engine
    speech_engine = pyttsx3.init()

    # set voice
    if voice_name is not None:
        voice_id = get_voice_id(speech_engine, voice_name)
        logger.debug(f"Using voice ID {voice_id} for voice {voice_name}")
        speech_engine.setProperty("voice", voice_id)

    # set speech rate
    speech_engine.setProperty(
        "rate", speech_config.get("speech_rate_wpm", _DEFAULT_SPEECH_RATE_WPM)
    )

    return speech_config, speech_engine


def running_on_mac_os() -> bool:
    """Check if the current platform is macOS.

    Uses platform.platform() to detect the operating system.

    Returns:
        bool: True if running on macOS, False otherwise
    """
    return "mac" in platform.platform().lower()


def running_on_windows() -> bool:
    """Check if the current platform is Windows.

    Uses platform.platform() to detect the operating system.

    Returns:
        bool: True if running on Windows, False otherwise
    """
    return "windows" in platform.platform().lower()


def get_voice_id(speech_engine: pyttsx3.Engine, voice_name: str) -> str | None:
    """Look up the voice ID for a given voice name in the pyttsx3 engine.

    Searches through all available voices in the TTS engine to find a voice
    matching the specified name and returns its ID.

    Args:
        speech_engine (pyttsx3.Engine): Initialized pyttsx3 TTS engine instance
        voice_name (str): The name of the voice to search for (e.g., "Samantha",
            "Microsoft David Desktop - English (United States)")

    Returns:
        str | None: The voice ID if found, None if no matching voice exists.
            The ID can be used with speech_engine.setProperty('voice', voice_id)

    Note:
        To see all available voices and their names, use:
        voices = speech_engine.getProperty('voices')
        for voice in voices:
            print(voice.name, voice.id)
    """
    voices = speech_engine.getProperty("voices")
    for voice in voices:
        if voice.name == voice_name:
            return voice.id
    return None


def speak_message(message: str, speech_engine: pyttsx3.Engine) -> None:
    """Speak a text message using the pyttsx3 speech engine.

    This function handles a known pyttsx3 bug where the run loop doesn't properly
    close after the queue is finished. It explicitly ends any active loop before
    speaking to prevent RuntimeError.

    The function blocks until the message is fully spoken (runAndWait), making it
    suitable for use in a separate thread to avoid blocking the main application.

    Args:
        message (str): The text message to be spoken aloud
        speech_engine (pyttsx3.Engine): An initialized pyttsx3 Engine instance with
            configured voice and speech rate

    Note:
        This function works around a pyttsx3 bug (issue #193) where the event loop
        doesn't close properly. The workaround checks if the engine is in a loop
        (_inLoop) and explicitly ends it before speaking.

    See Also:
        - pyttsx3 issue: https://github.com/nateshmbhat/pyttsx3/issues/193
        - pyttsx3 event loop docs: https://pyttsx3.readthedocs.io/en/latest/engine.html
    """
    # This is an open bug in pyttsx3; without this, raises RuntimeError: run loop already started
    # The loop doesn't seem to get closed properly when the queue is finished
    # see this fix suggestion from https://github.com/nateshmbhat/pyttsx3/issues/193
    # See also event loop reference: https://pyttsx3.readthedocs.io/en/latest/engine.html#using-an-external-event-loop
    if speech_engine._inLoop:
        speech_engine.endLoop()

    speech_engine.say(message)
    speech_engine.runAndWait()

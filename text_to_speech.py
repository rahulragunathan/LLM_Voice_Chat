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
    """Initializes the pyttsx3 text-to-speech engine.

    Args:
        speech_config (dict): configuration for the text-to-speech

    Returns:
        tuple[dict, pyttsx3.Engine | None]: the updated speech configuration and the speech engine
    """
    if running_on_windows():
        logger.debug("Using pystxx3 speech on Windows")
        voice_name = speech_config.get("voice_name", _DEFAULT_WINDOWS_VOICE)
    elif running_on_mac_os:
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
    """Check whether running on MacOS

    Returns:
        bool: whether true or false
    """
    return "mac" in platform.platform().lower()


def running_on_windows() -> bool:
    """Check whether running on Windows

    Returns:
        bool: whether true or false
    """
    return "windows" in platform.platform().lower()


def get_voice_id(speech_engine: pyttsx3.Engine, voice_name: str) -> str | None:
    """Get the the ID for a given voice in pyttsx3

    Args:
        speech_engine (pyttsx3.Engine): the pyttsx3 engine
        voice_name (str): the name of the voice

    Returns:
        str | None: the ID associated with the voice name. If voice is not found, return None.
    """
    voices = speech_engine.getProperty("voices")
    for voice in voices:
        if voice.name == voice_name:
            return voice.id
    return None


def speak_message(message: str, speech_engine: pyttsx3.Engine) -> None:
    """Speak the message provided using the pyttsx3 speech engine.

    Args:
        message (str): the message to be spoken
        speech_engine (pyttsx3.Engine | None): the initialized speech engine.
    """
    # This is an open bug in pyttsx3; without this, raises RuntimeError: run loop already started
    # The loop doesn't seem to get closed properly when the queue is finished
    # see this fix suggestion from https://github.com/nateshmbhat/pyttsx3/issues/193
    # See also event loop reference: https://pyttsx3.readthedocs.io/en/latest/engine.html#using-an-external-event-loop
    if speech_engine._inLoop:
        speech_engine.endLoop()

    speech_engine.say(message)
    speech_engine.runAndWait()

import pyttsx3
import os
import subprocess
import platform


_DEFAULT_SPEECH_RATE_WPM = 180


def initialize_text_to_speech(
    speech_config: dict,
) -> tuple[dict, pyttsx3.Engine | None]:
    """Initializes the text to speech. If not running on Mac OS, configuration is
    reset to use pyttsx3 for speech. If using pyttsx3, speech engine is initialized.

    Args:
        speech_config (dict): configuration for the text-to-speech

    Returns:
        tuple[dict, pyttsx3.Engine | None]: the updated speech configuration and the speech engine
    """
    speech_engine = None
    use_mac_os_speech = speech_config.get("use_mac_os_speech", False)

    # reset flag if not running on mac os
    if not running_on_mac_os() and use_mac_os_speech:
        use_mac_os_speech = False
        speech_config["use_mac_os_speech"] = False

    # create engine if using Python text-to-speech
    if not use_mac_os_speech:
        speech_engine = pyttsx3.init()
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


def speak_message(
    message: str, speech_config: dict, speech_engine: pyttsx3.Engine | None
) -> None:
    """Speak the message provided.

    Args:
        message (str): the message to be spoken
        speech_config (dict): the configuration for the spoken message
        speech_engine (pyttsx3.Engine | None): if using pyttsx3, the initialized speech engine. Else, None
    """
    if speech_config.get("use_mac_os_speech", False):
        mac_os_speak(
            message=message,
            speech_rate_wpm=speech_config.get(
                "speech_rate_wpm", _DEFAULT_SPEECH_RATE_WPM
            ),
        )
    else:
        pyttsx3_speak(message=message, speech_engine=speech_engine)


def pyttsx3_speak(message: str, speech_engine: pyttsx3.Engine) -> None:
    """Speak the message using the Python pyttsx3 package.

    Args:
        message (str): the message to be spoken
        speech_engine (pyttsx3.Engine): initialized speech engine
    """
    speech_engine.say(message)
    speech_engine.runAndWait()


def mac_os_speak(message: str, speech_rate_wpm: int) -> None:
    """Speak the message using the MacOS 'say' command.

    Args:
        message (str): the message to be spoken
        speech_rate_wpm (int): the speed at which the message should be spoken
    """
    subprocess.run(["say", message, "-r", str(speech_rate_wpm)])

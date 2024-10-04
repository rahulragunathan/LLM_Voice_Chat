import pyttsx3
import os
import subprocess
import platform

from logger import AppLogger

logger = AppLogger(os.path.splitext(os.path.basename(__file__))[0]).get_logger()

_DEFAULT_SPEECH_RATE_WPM = 180
# TODO: figure out why it always uses this defa8lt voice when it is supposed to be overriden in the config
_DEFAULT_PYTTSX3_WINDOWS_VOICE = "Microsoft David Desktop - English (United States)"
_DEFAULT_MAC_OS_VOICE = "Fred"


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
        logger.debug("Not running on Mac OS. Switching to Python text-to-speech.")

    if not use_mac_os_speech and running_on_windows():
        logger.debug("Using pystxx3 speech on Windows")
        pyttsx3_voice_name = speech_config.get(
            "voice_name", _DEFAULT_PYTTSX3_WINDOWS_VOICE
        )
    elif not use_mac_os_speech:
        logger.debug("Using pystxx3 speech on Linux")
        pyttsx3_voice_name = speech_config.get("voice_name", None)

    # create engine if using Python text-to-speech
    if not use_mac_os_speech:
        speech_engine = pyttsx3.init()
        speech_engine.setProperty(
            "rate", speech_config.get("speech_rate_wpm", _DEFAULT_SPEECH_RATE_WPM)
        )

        if pyttsx3_voice_name is not None:
            speech_engine.setProperty(
                "voice", get_pyttsx3_voice_id(speech_engine, pyttsx3_voice_name)
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


def get_pyttsx3_voice_id(speech_engine: pyttsx3.Engine, voice_name: str):
    """Get the the ID for a given voice in pyttsx3

    Args:
        speech_engine (pyttsx3.Engine): the pyttsx3 engine
        voice_name (str): the name of the voice

    Returns:
        int: the ID associated with the voice name
    """
    return (
        voice.id
        for voice in speech_engine.getProperty("voices")
        if voice.name == voice_name
    )


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
            voice_name=speech_config.get("voice_name", _DEFAULT_MAC_OS_VOICE),
        )
    else:
        pyttsx3_speak(message=message, speech_engine=speech_engine)


def pyttsx3_speak(message: str, speech_engine: pyttsx3.Engine) -> None:
    """Speak the message using the Python pyttsx3 package.

    Args:
        message (str): the message to be spoken
        speech_engine (pyttsx3.Engine): initialized speech engine
    """

    # This is an open bug in pyttsx3; without this, raises RuntimeError: run loop already started
    # The loop doesn't seem to get closed properly when the queue is finished
    # see this fix suggestion from https://github.com/nateshmbhat/pyttsx3/issues/193
    # See also event loop reference: https://pyttsx3.readthedocs.io/en/latest/engine.html#using-an-external-event-loop
    if speech_engine._inLoop:
        speech_engine.endLoop()

    speech_engine.say(message)
    speech_engine.runAndWait()


def mac_os_speak(
    message: str, speech_rate_wpm: int, voice_name: str = _DEFAULT_MAC_OS_VOICE
) -> None:
    """Speak the message using the MacOS 'say' command.

    Args:
        message (str): the message to be spoken
        speech_rate_wpm (int): the speed at which the message should be spoken
        voice_name (str): the Mac OS voice to use. Default is "Fred".
    """
    subprocess.run(["say", message, "-r", str(speech_rate_wpm), "-v", voice_name])

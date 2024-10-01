import pyttsx3
import os
import subprocess
import platform


_DEFAULT_SPEECH_RATE = "180"


def initialize_text_to_speech():
    if check_if_mac_os() and os.getenv("USE_MAC_OS_SPEECH", "False").lower() != "false":
        use_mac_os_speech = True
        speech_engine = None
    else:
        use_mac_os_speech = False
        speech_engine = get_pyttsx3_engine()
        speech_engine.setProperty("rate", get_speech_rate())

    return use_mac_os_speech, speech_engine


def get_speech_rate():
    return int(os.getenv("SPEECH_RATE", _DEFAULT_SPEECH_RATE))


def check_if_mac_os():
    return "mac" in platform.platform().lower()


def get_pyttsx3_engine():
    return pyttsx3.init()


def speak(message: str, use_mac_os_speech: bool, speech_engine):
    if use_mac_os_speech:
        mac_os_speak(message=message)
    else:
        pyttsx3_speak(message=message, speech_engine=speech_engine)


def pyttsx3_speak(message: str, speech_engine):
    speech_engine.say(message)
    speech_engine.runAndWait()


def mac_os_speak(message: str):
    subprocess.run(["say", message, "-r", str(get_speech_rate())])

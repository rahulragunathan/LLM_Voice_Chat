import pyttsx3

def main():
    engine = pyttsx3.init()
    engine.say("Hello world, this is my text to speech program")
    engine.runAndWait()

if __name__ == "__main__":
    main()
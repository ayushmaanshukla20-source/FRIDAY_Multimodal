import pyttsx3


def speak(text: str):
    engine = pyttsx3.init()
    engine.setProperty("rate", 175)
    voices = engine.getProperty("voices")
    if len(voices) > 1:
        engine.setProperty("voice", voices[1].id)
    engine.say(text)
    engine.runAndWait()


def startup_greeting():
    intro_message = (
        "Systems initialized. I am Friday, created by Ayushmaan Shukla. "
        "Chrome automation and Spotify controls are active. How can I assist you?"
    )
    speak(intro_message)


if __name__ == "__main__":
    startup_greeting()


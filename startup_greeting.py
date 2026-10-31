"""
FRIDAY Multimodal Voice Assistant
Author: Ayushmaan Shukla
Roll / Enrollment No.: 202510101240164
Department: Computer Science & Engineering (AI & ML)
Institution: Shri Ramswaroop Memorial University
Notice: This project is strictly for academic evaluation. 
        Unauthorized reproduction or submission is a violation of academic integrity.
"""
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



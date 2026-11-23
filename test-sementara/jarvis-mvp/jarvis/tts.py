"""Windows speech output; called from the dedicated worker thread."""
import pyttsx3


def speak(text: str) -> None:
    engine = pyttsx3.init(driverName="sapi5")
    engine.setProperty("rate", 165)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

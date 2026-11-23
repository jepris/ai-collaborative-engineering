import re


def handle_command(text: str) -> str:
    command = re.sub(r"[^\w\s]", " ", text.casefold())
    command = " ".join(command.split())
    if any(phrase in command for phrase in ("siapa gua", "siapa gue", "siapa saya", "siapa aku")):
        return "Anda adalah Ibnu, Master."
    if "halo jarvis" in command or "hai jarvis" in command:
        return "Halo Master, saya siap membantu."
    if "siapa kamu" in command or "siapa jarvis" in command:
        return "Saya Jarvis, asisten pribadi Anda."
    return "Maaf Master, perintah belum dikenali."

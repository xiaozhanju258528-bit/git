import asyncio
import speech_recognition as sr
import edge_tts

CHINESE_VOICE = "zh-CN-XiaoxiaoMultilingualNeural"
ENGLISH_VOICE = "en-US-AriaNeural"
RATE = "-15%"
PITCH = "+5Hz"

recognizer = sr.Recognizer()

async def speak(text: str, lang: str = "zh"):
    voice = CHINESE_VOICE if lang == "zh" else ENGLISH_VOICE
    tts = edge_tts.Communicate(text, voice=voice, rate=RATE, pitch=PITCH)
    await tts.save("output.mp3")
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load("output.mp3")
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def listen(timeout: int = 5, phrase_time_limit: int = 5):
    with sr.Microphone() as source:
        print("Adjusting for ambient noise...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        print("Listening...")
        try:
            audio = recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            return None, None
    return audio

def recognize(audio) -> tuple[str, str]:
    if audio is None:
        return None, None
    for lang_code, lang_name in [("zh-CN", "zh"), ("en-US", "en")]:
        try:
            text = recognizer.recognize_google(audio, language=lang_code)
            print(f"[{lang_name}] {text}")
            return text, lang_name
        except sr.UnknownValueError:
            continue
        except sr.RequestError:
            return None, None
    return None, None

async def get_voice_input() -> tuple[str, str]:
    audio = listen()
    return recognize(audio)

def get_voice_input_sync() -> tuple[str, str]:
    return asyncio.run(get_voice_input())

def speak_sync(text: str, lang: str = "zh"):
    asyncio.run(speak(text, lang))
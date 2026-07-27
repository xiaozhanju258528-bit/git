from voice_module import get_voice_input_sync, speak_sync

def main():
    speak_sync("你好，请说话", lang="zh")
    text, lang = get_voice_input_sync()
    if text:
        print(f"Recognized: {text} ({lang})")
        reply = f"你说的是 {text}" if lang == "zh" else f"You said: {text}"
        speak_sync(reply, lang=lang)
    else:
        speak_sync("我没有听到声音", lang="zh")

if __name__ == "__main__":
    main()

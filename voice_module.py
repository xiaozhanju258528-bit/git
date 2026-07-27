import asyncio
import os
import tempfile
import logging
from typing import Optional, Tuple
from pathlib import Path
import speech_recognition as sr
import edge_tts
from pygame import mixer

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# TTS 配置
CHINESE_VOICE = "zh-CN-XiaoxiaoMultilingualNeural"
ENGLISH_VOICE = "en-US-AriaNeural"
RATE = "-15%"
PITCH = "+5Hz"

# 语音识别配置
DEFAULT_TIMEOUT = 5
DEFAULT_PHRASE_TIME_LIMIT = 5
AMBIENT_NOISE_DURATION = 0.5

# 输出配置
OUTPUT_DIR = Path(tempfile.gettempdir()) / "voice_module"
OUTPUT_DIR.mkdir(exist_ok=True)

recognizer = sr.Recognizer()
mixer.init()

async def speak(
    text: str, 
    lang: str = "zh",
    output_file: Optional[str] = None,
    play: bool = True,
    rate: str = RATE,
    pitch: str = PITCH
) -> str:
    """
    文本转语音并播放
    
    Args:
        text: 要朗读的文本
        lang: 语言 ("zh" 或 "en")
        output_file: 输出文件路径，默认使用临时文件
        play: 是否播放音频
        rate: 语速，默认 "-15%"
        pitch: 音调，默认 "+5Hz"
    
    Returns:
        生成的音频文件路径
    
    Raises:
        ValueError: 文本为空
        RuntimeError: TTS 生成失败
    """
    if not text or not text.strip():
        raise ValueError("Text cannot be empty")
    
    voice = CHINESE_VOICE if lang == "zh" else ENGLISH_VOICE
    
    # 生成输出文件路径
    if output_file is None:
        output_file = str(OUTPUT_DIR / f"tts_{asyncio.get_event_loop().time():.0f}.mp3")
    
    try:
        logger.info(f"Generating TTS: {text[:50]}{'...' if len(text) > 50 else ''}")
        tts = edge_tts.Communicate(text, voice=voice, rate=rate, pitch=pitch)
        await tts.save(output_file)
        logger.info(f"TTS saved to: {output_file}")
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise RuntimeError(f"Failed to generate TTS: {e}") from e
    
    if play:
        _play_audio(output_file)
    
    return output_file


def _play_audio(file_path: str, blocking: bool = True) -> None:
    """
    播放音频文件
    
    Args:
        file_path: 音频文件路径
        blocking: 是否阻塞直到播放完成
    """
    try:
        mixer.music.load(file_path)
        mixer.music.play()
        logger.info(f"Playing audio: {file_path}")
        
        if blocking:
            while mixer.music.get_busy():
                mixer.time.Clock().tick(10)
                
    except Exception as e:
        logger.error(f"Audio playback failed: {e}")
        raise RuntimeError(f"Failed to play audio: {e}") from e


def stop_speaking() -> None:
    """停止当前正在播放的音频"""
    if mixer.music.get_busy():
        mixer.music.stop()
        logger.info("Audio playback stopped")

def listen(
    timeout: int = DEFAULT_TIMEOUT,
    phrase_time_limit: int = DEFAULT_PHRASE_TIME_LIMIT,
    ambient_duration: float = AMBIENT_NOISE_DURATION
) -> Optional[sr.AudioData]:
    """
    从麦克风监听音频
    
    Args:
        timeout: 超时时间（秒）
        phrase_time_limit: 短语时间限制（秒）
        ambient_duration: 环境噪音校准时长（秒）
    
    Returns:
        音频数据，超时返回 None
    """
    try:
        with sr.Microphone() as source:
            logger.info("Adjusting for ambient noise...")
            recognizer.adjust_for_ambient_noise(source, duration=ambient_duration)
            logger.info("Listening...")
            
            audio = recognizer.listen(
                source,
                timeout=timeout,
                phrase_time_limit=phrase_time_limit
            )
            return audio
            
    except sr.WaitTimeoutError:
        logger.warning("Listening timeout - no speech detected")
        return None
    except sr.RequestError as e:
        logger.error(f"Microphone access error: {e}")
        return None
    except OSError as e:
        logger.error(f"Audio device error: {e}")
        return None

def recognize(
    audio: Optional[sr.AudioData],
    languages: list = None
) -> Tuple[Optional[str], Optional[str]]:
    """
    识别语音为文本
    
    Args:
        audio: 音频数据
        languages: 语言列表，默认 ["zh-CN", "en-US"]
    
    Returns:
        (识别文本, 语言代码)，失败返回 (None, None)
    """
    if audio is None:
        return None, None
    
    if languages is None:
        languages = [("zh-CN", "zh"), ("en-US", "en")]
    
    for lang_code, lang_name in languages:
        try:
            text = recognizer.recognize_google(audio, language=lang_code)
            logger.info(f"[{lang_name}] Recognized: {text}")
            return text, lang_name
            
        except sr.UnknownValueError:
            logger.debug(f"Could not understand audio in {lang_code}")
            continue
            
        except sr.RequestError as e:
            logger.error(f"Speech recognition service error: {e}")
            return None, None
    
    logger.warning("Could not recognize speech in any language")
    return None, None

async def get_voice_input(
    timeout: int = DEFAULT_TIMEOUT,
    phrase_time_limit: int = DEFAULT_PHRASE_TIME_LIMIT
) -> Tuple[Optional[str], Optional[str]]:
    """
    异步获取语音输入
    
    Args:
        timeout: 监听超时时间（秒）
        phrase_time_limit: 短语时间限制（秒）
    
    Returns:
        (识别文本, 语言代码)
    """
    audio = listen(timeout=timeout, phrase_time_limit=phrase_time_limit)
    return recognize(audio)


def get_voice_input_sync(
    timeout: int = DEFAULT_TIMEOUT,
    phrase_time_limit: int = DEFAULT_PHRASE_TIME_LIMIT
) -> Tuple[Optional[str], Optional[str]]:
    """
    同步包装：获取语音输入
    
    Args:
        timeout: 监听超时时间（秒）
        phrase_time_limit: 短语时间限制（秒）
    
    Returns:
        (识别文本, 语言代码)
    """
    return asyncio.run(get_voice_input(timeout, phrase_time_limit))


def speak_sync(
    text: str,
    lang: str = "zh",
    output_file: Optional[str] = None,
    play: bool = True,
    rate: str = RATE,
    pitch: str = PITCH
) -> str:
    """
    同步包装：文本转语音
    
    Args:
        text: 要朗读的文本
        lang: 语言 ("zh" 或 "en")
        output_file: 输出文件路径
        play: 是否播放
        rate: 语速
        pitch: 音调
    
    Returns:
        生成的音频文件路径
    """
    return asyncio.run(speak(text, lang, output_file, play, rate, pitch))


def cleanup_old_files(max_age_hours: int = 24) -> int:
    """
    清理旧的临时音频文件
    
    Args:
        max_age_hours: 最大文件年龄（小时）
    
    Returns:
        删除的文件数量
    """
    import time
    
    deleted_count = 0
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    try:
        for file_path in OUTPUT_DIR.glob("*.mp3"):
            if current_time - file_path.stat().st_mtime > max_age_seconds:
                file_path.unlink()
                deleted_count += 1
                logger.debug(f"Deleted old file: {file_path}")
        
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} old audio files")
            
    except Exception as e:
        logger.error(f"Cleanup failed: {e}")
    
    return deleted_count


# 模块清理
def __del__():
    """模块卸载时清理资源"""
    try:
        mixer.quit()
    except:
        pass

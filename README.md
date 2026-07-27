# Voice Module

一个简单的 Python 语音交互模块，支持语音识别和文本转语音功能。

## 功能

- 🎤 语音识别（支持中英文）
- 🔊 文本转语音（TTS）
- 🚀 异步和同步接口
- 📝 完整的日志系统
- 🔧 灵活的配置选项

## 安装

```bash
pip install -r requirements.txt
```

## 使用示例

```python
from voice_module import get_voice_input_sync, speak_sync

# 语音输入
text, lang = get_voice_input_sync()
print(f"识别结果: {text}, 语言: {lang}")

# 文本转语音
speak_sync("你好，世界！", lang="zh")
```

## 配置

编辑 `voice_module.py` 中的常量：

- `CHINESE_VOICE`: 中文语音
- `ENGLISH_VOICE`: 英文语音
- `RATE`: 语速
- `PITCH`: 音调

## 测试

```bash
pytest
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件
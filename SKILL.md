---
name: feishu-voice-sync
description: |
  飞书文字转语音同步插件。每次回复时自动生成对应语音，文字和音频内容完全一致。
  支持 Windows / Mac / Linux 全平台。开车、双手不便时开启此技能实现文字+语音同步发送。
---

# feishu-voice-sync

飞书文字转语音同步技能。每次发文字消息后自动生成对应音频，**文字和音频内容100%一致**。

## 🔴 核心铁律（必须写入 SOUL.md）

每次回复文字后，**必须立即**执行以下步骤：

1. 发送文字消息（用户看到）
2. **紧接着**生成并发送音频（用户听到）
3. 文字内容 = 音频内容（逐字复制，不得删减）

### 禁止事项
- ❌ 先发文字，等一下再发音频（会乱序）
- ❌ 文字和音频内容不一致
- ❌ 音频内容截断或简化
- ❌ 用 file 类型代替 audio 类型发送

## 依赖安装

### macOS
```bash
brew install ffmpeg
pip install edge-tts
```

### Linux (Ubuntu/Debian)
```bash
sudo apt install ffmpeg
pip install edge-tts
```

### Windows
```powershell
winget install ffmpeg
pip install edge-tts
```

## 配置

修改 `scripts/send_voice.py` 中的三个配置：
```python
APP_ID = "cli_你的飞书应用ID"
APP_SECRET = "你的飞书应用密钥"
RECEIVE_ID = "接收者的Open ID"
```

## 安装方式

### 方式一：从 ClawhHub 安装
```bash
openclaw skills install feishu-voice-sync
```

### 方式二：手动安装
```bash
unzip feishu-voice-sync.zip
cd feishu-voice-sync
openclaw skills install .
```

## 🔧 集成到 SOUL.md

在 AI 的 SOUL.md 中添加以下完整规则：

```markdown
## 语音附带规则（feishu-voice-sync 2026-05-07确立）

### 核心要求
**每次回复文字后，必须立即发送对应音频，文字和音频内容必须完全一致。**

### 执行步骤（顺序不能乱）
1. 发送文字消息
2. 立即生成语音：`edge-tts -t "刚才发送的文字" -v "zh-CN-XiaoxiaoNeural" --write-media /tmp/audio.mp3`
3. 转为opus格式：`ffmpeg -y -i /tmp/audio.mp3 -c:a libopus -b:a 128k /tmp/audio.opus`
4. 上传到飞书获取 file_key
5. 发送audio消息（不是file消息）

### 关键：调用 send_voice.sh 或 send_voice.py
```bash
# 传入刚才发送的文字内容
bash scripts/send_voice.sh "刚才发送的完整文字内容"
```

### 禁止事项
- ❌ 文字和音频分开发送（必须紧接着发）
- ❌ 音频内容与文字不一致
- ❌ 音频内容截断或简化
- ❌ 用file类型代替audio类型发送
```

## 技术细节

- TTS：微软 edge-tts（免费，无次数限制）
- 格式转换：ffmpeg（mp3 → opus）
- 发送：飞书 IM API (audio类型)

## 发布信息

- 版本：1.0.1
- 日期：2026-05-07
- 更新：完善 SOUL.md 集成规则，明确禁止乱序行为

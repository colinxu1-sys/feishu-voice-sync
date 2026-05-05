# feishu-voice-sync

飞书文字转语音同步技能。AI发文字时自动带上语音，文字和音频内容100%一致。

## 功能
- 将文字转为中文语音（edge-tts）
- 自动发送语音消息到飞书
- **文字和音频内容完全一致**，不简化、不摘要、不改变任何措辞
- 支持多用户配置

## 支持平台
Windows / Mac / Linux

## 安装步骤

### 1. 安装依赖

**macOS:**
```bash
brew install ffmpeg && pip install edge-tts
```

**Linux:**
```bash
sudo apt install ffmpeg && pip install edge-tts
```

**Windows:**
```powershell
winget install ffmpeg && pip install edge-tts
```

### 2. 安装 Skill

```bash
openclaw skills install github:colinxu1-sys/feishu-voice-sync
```

如果VirusTotal报警，加 `--force` 强行安装：
```bash
openclaw skills install github:colinxu1-sys/feishu-voice-sync --force
```

### 3. 配置多用户

**复制以下内容发给AI：**

```
请帮我配置 feishu-voice-sync，需要添加用户：
- 用户名（用于标识，如 user1）
- APP_ID（cli_ 开头）
- APP_SECRET
- RECEIVE_ID（ou_ 开头）
```

AI会自动将配置写入 `scripts/config.py`。

如果需要添加多个用户，告诉AI：
```
添加另一个用户：用户名=xxx，APP_ID=xxx，APP_SECRET=xxx，RECEIVE_ID=xxx
```

### 4. 激活语音发送

告诉AI：
```
请在 SOUL.md 里加入以下规则：

## 语音附带规则（2026-05-05确立）

### 核心要求
**每次回复文字后，必须立即发送对应音频，文字和音频内容必须完全一致。**

### 执行步骤
1. 对每个已配置的用户的飞书执行：python3 scripts/send_voice.py "文字内容"
2. 确保音频与文字100%一致
```

## 验证安装

```bash
python3 scripts/send_voice.py "测试消息"
```

收到语音即表示安装成功。

## 多用户说明

- 每个用户独立配置 APP_ID、APP_SECRET、RECEIVE_ID
- 发送时会根据上下文自动选择对应用户
- 如需指定用户发送：`python3 scripts/send_voice.py "文字内容" 用户名`

## 问题
联系发给你这个包的人。

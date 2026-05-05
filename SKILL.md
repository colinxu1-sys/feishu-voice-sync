---
name: feishu-voice-sync
description: 飞书文字转语音同步技能。当AI发文字时，自动生成对应语音并发送到飞书，文字和音频内容100%一致。支持多用户配置。
---

# feishu-voice-sync

飞书文字转语音同步技能。AI发文字时自动带上语音。

## 核心规则

**每次回复文字后，必须立即发送对应音频，文字和音频内容必须完全一致。**

不得：
- 简化文字内容
- 摘要文字内容  
- 改变任何措辞

## 配置

安装后告诉AI：
```
请帮我配置 feishu-voice-sync，需要添加用户：
- 用户名/标识
- APP_ID（cli_开头）
- APP_SECRET
- RECEIVE_ID（ou_开头）
```

AI会自动将配置写入 `scripts/config.py`。

## 执行逻辑

当发送文字消息时，对每个已配置的用户的飞书：
1. 用相同的文字内容调用 send_voice.py
2. 确认音频与文字100%一致

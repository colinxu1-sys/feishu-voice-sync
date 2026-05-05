#!/bin/bash
# feishu-voice-sync: 跨平台Shell版本 (Linux / macOS / Windows Git Bash)

APP_ID="cli_a962d05d60f91cd4"
APP_SECRET="CebvVorcQzS6EVG2RXk9fx8ZNsvyxqVM"
RECEIVE_ID="ou_efda6ac0694ee9dfa21494b17178d6cd"

TEXT="$1"
if [ -z "$TEXT" ]; then
    echo "用法: $0 \"文字内容\""
    exit 1
fi

TOKEN=$(curl -s -X POST "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal" \
    -H "Content-Type: application/json" \
    -d "{\"app_id\": \"$APP_ID\", \"app_secret\": \"$APP_SECRET\"}" \
    --max-time 30 | python3 -c "import sys,json; print(json.load(sys.stdin).get('tenant_access_token',''))")

if [ -z "$TOKEN" ]; then
    echo "Token获取失败"
    exit 1
fi

TMP_DIR=$(mktemp -d)
TMP_MP3="$TMP_DIR/voice.mp3"
TMP_OPUS="$TMP_DIR/voice.opus"

edge-tts -t "$TEXT" -v "zh-CN-XiaoxiaoNeural" --write-media "$TMP_MP3" 2>/dev/null && \
ffmpeg -y -i "$TMP_MP3" -c:a libopus -b:a 128k "$TMP_OPUS" 2>/dev/null && \
FILE_KEY=$(curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/files" \
    -H "Authorization: Bearer $TOKEN" \
    -F "file_type=opus" \
    -F "file_name=voice.opus" \
    -F "file=@$TMP_OPUS" --max-time 30 | python3 -c "import sys,json; print(json.load(sys.stdin).get('data',{}).get('file_key',''))") && \
curl -s -X POST "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "{\"receive_id\": \"$RECEIVE_ID\", \"msg_type\": \"audio\", \"content\": \"{\\\"file_key\\\": \\\"$FILE_KEY\\\"}\"}" \
    --max-time 30 | python3 -c "import sys,json; sys.exit(0 if json.load(sys.stdin).get('code')==0 else 1)"

RESULT=$?
rm -rf "$TMP_DIR"
[ $RESULT -eq 0 ] && echo "发送成功" || echo "发送失败"
exit $RESULT

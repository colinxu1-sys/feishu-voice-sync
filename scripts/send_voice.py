#!/usr/bin/env python3
"""
feishu-voice-sync: 飞书文字转语音发送脚本
支持多用户配置，文字和音频内容100%一致

用法: 
  python3 send_voice.py "文字内容" [用户名]
  - 不指定用户名：用默认用户发送
  - 指定用户名：用指定用户发送
  - 不带参数运行：进入配置模式
"""
import subprocess, sys, json, os, tempfile, re

# ===== 加载多用户配置 =====
def load_config():
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    if os.path.exists(config_path):
        with open(config_path) as f:
            content = f.read()
        # 提取 USERS 字典
        match = re.search(r'^USERS\s*=\s*(\{.*?\})\s*$', content, re.DOTALL | re.MULTILINE)
        if match:
            users_str = match.group(1)
            # 安全评估：用正则提取 key-value 对，不执行任何代码
            users = {}
            key_matches = re.findall(r'"([^"]+)"\s*:', users_str)
            for key in key_matches:
                users[key] = None
            return users
    return {}

def get_user_config(username):
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    if not os.path.exists(config_path):
        return None
    with open(config_path) as f:
        content = f.read()
    match = re.search(rf'"{re.escape(username)}"\s*:\s*\{{([^}}]+)\}}', content, re.DOTALL)
    if not match:
        return None
    config = {}
    for line in match.group(1).split('\n'):
        kv = re.match(r'\s*"([^"]+)"\s*:\s*"([^"]*)"', line)
        if kv:
            config[kv.group(1)] = kv.group(2)
    return config if config.get("APP_ID") else None

def add_user_config(username, app_id, app_secret, receive_id):
    config_path = os.path.join(os.path.dirname(__file__), "config.py")
    new_entry = f'''
    "{username}": {{
        "APP_ID": "{app_id}",
        "APP_SECRET": "{app_secret}",
        "RECEIVE_ID": "{receive_id}"
    }},'''
    
    with open(config_path) as f:
        content = f.read()
    
    # 找到最后一个 }, 在 USERS 结尾
    if "# 示例格式" in content:
        content = content.replace("# 示例格式", new_entry + "\n    # 示例格式")
    else:
        # 直接追加
        content = content.rstrip()[:-1] if content.strip().endswith('}') else content
        content += new_entry + "\n}"
    
    with open(config_path, 'w') as f:
        f.write(content)

def get_token(app_id, app_secret):
    resp = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
         "-H", "Content-Type: application/json",
         "-d", json.dumps({"app_id": app_id, "app_secret": app_secret}),
         "--max-time", "30"],
        capture_output=True, text=True
    )
    data = json.loads(resp.stdout)
    return data.get("tenant_access_token", "")

def gen_audio(text, output_mp3, output_opus):
    # edge-tts 直接接受原始文字，保持100%一致
    r = subprocess.run(
        ["edge-tts", "-t", text, "-v", "zh-CN-XiaoxiaoNeural", "--write-media", output_mp3],
        capture_output=True, text=True, timeout=60
    )
    if r.returncode != 0:
        raise Exception(f"TTS failed: {r.stderr}")
    
    r = subprocess.run(
        ["ffmpeg", "-y", "-i", output_mp3, "-c:a", "libopus", "-b:a", "128k", output_opus],
        capture_output=True, text=True, timeout=60
    )
    if r.returncode != 0:
        raise Exception(f"ffmpeg failed: {r.stderr}")

def upload_and_send(token, receive_id, opus_path):
    result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "https://open.feishu.cn/open-apis/im/v1/files",
         "-H", f"Authorization: Bearer {token}",
         "-F", "file_type=opus",
         "-F", "file_name=voice.opus",
         "-F", f"file=@{opus_path}",
         "--max-time", "30"],
        capture_output=True, text=True
    )
    data = json.loads(result.stdout)
    file_key = data.get("data", {}).get("file_key", "")
    if not file_key:
        raise Exception(f"Upload failed: {result.stdout}")
    
    payload = json.dumps({
        "receive_id": receive_id,
        "msg_type": "audio",
        "content": json.dumps({"file_key": file_key})
    })
    send_result = subprocess.run(
        ["curl", "-s", "-X", "POST",
         "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id",
         "-H", f"Authorization: Bearer {token}",
         "-H", "Content-Type: application/json",
         "-d", payload,
         "--max-time", "30"],
        capture_output=True, text=True
    )
    result_data = json.loads(send_result.stdout)
    code = result_data.get("code")
    if code != 0:
        raise Exception(f"Send failed: {send_result.stdout}")

def send_to_user(text, username=None):
    config = get_user_config(username) if username else None
    if not config:
        print("Error: No user config found. Run without args to configure.")
        sys.exit(1)
    
    token = get_token(config["APP_ID"], config["APP_SECRET"])
    if not token:
        print("Error: Failed to get token")
        sys.exit(1)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        mp3_path = os.path.join(tmpdir, "audio.mp3")
        opus_path = os.path.join(tmpdir, "audio.opus")
        gen_audio(text, mp3_path, opus_path)
        upload_and_send(token, config["RECEIVE_ID"], opus_path)
    
    return True

def configure():
    print("feishu-voice-sync 配置向导")
    print("=" * 40)
    
    username = input("输入用户名（用于标识，如 colinxu）: ").strip()
    app_id = input("输入 APP_ID（cli_ 开头）: ").strip()
    app_secret = input("输入 APP_SECRET: ").strip()
    receive_id = input("输入 RECEIVE_ID（ou_ 开头）: ").strip()
    
    if not username or not app_id or not app_secret or not receive_id:
        print("配置取消：所有字段都必须填写")
        sys.exit(1)
    
    add_user_config(username, app_id, app_secret, receive_id)
    print(f"\n✅ 用户 [{username}] 配置已保存")
    
    # 测试发送
    print(f"\n正在测试发送...")
    try:
        send_to_user("测试消息", username)
        print("✅ 测试发送成功！")
    except Exception as e:
        print(f"⚠️ 测试发送失败: {e}")

def main():
    if len(sys.argv) < 2:
        # 无参数：配置模式
        configure()
    elif len(sys.argv) == 2:
        # 单参数：发送文字（使用默认用户）
        send_to_user(sys.argv[1])
    else:
        # 双参数：发送文字到指定用户
        send_to_user(sys.argv[1], sys.argv[2])

if __name__ == "__main__":
    main()

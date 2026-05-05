# feishu-voice-sync 多用户配置
# 安装时自动写入，格式：用户名 -> {app_id, app_secret, receive_id}

USERS = {
    # 示例格式（安装时会被替换）：
    # "colinxu": {
    #     "APP_ID": "cli_xxxxxxxxxxxxxx",
    #     "APP_SECRET": "xxxxxxxxxxxxxxxx",
    #     "RECEIVE_ID": "ou_xxxxxxxxxxxxxxxx"
    # },
}

def get_default_user():
    """获取默认用户（第一个配置的）"""
    if USERS:
        return list(USERS.keys())[0]
    return None

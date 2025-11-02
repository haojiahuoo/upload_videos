import os

# 配置参数
# =======================
# 登录账号配置
# ACCOUNT_NAME = "17306358585"  # 全球美食
ACCOUNT_NAME = "13869586968"  # 荒野达人
# 萌宠搞笑


# 单个视频最大下载时长（秒）—— 超过这个就自动分段
MAX_SEGMENT_DURATION = 30 * 60  # 30 分钟

# 下载主目录
DOWNLOAD_ROOT = r"E:\Videos"
os.makedirs(DOWNLOAD_ROOT, exist_ok=True)  # 确保主目录存在

UPLOAD_ROOT = r"E:\Videos"
os.makedirs(UPLOAD_ROOT, exist_ok=True)  # 确保主目录存在

# Cookie 来源（可改为 "chrome" 或 "firefox"）
COOKIES_BROWSER = "firefox"

# 输出模板
# =======================
video_outtmpl = os.path.join(DOWNLOAD_ROOT, "%(playlist_title)s", "%(playlist_index)s - %(title)s.%(ext)s")
subs_outtmpl = os.path.join(DOWNLOAD_ROOT, "%(playlist_title)s", "%(playlist_index)s - %(title)s.%(lang)s.vtt")
desc_outtmpl = os.path.join(DOWNLOAD_ROOT, "%(playlist_title)s", "%(playlist_index)s - %(title)s.description")
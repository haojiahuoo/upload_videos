from download.youtube import *
from logger.logger import *
from upload.upload_main import upload_main

def download_video(platform, play_url, index=1, list=True):
    """
    下载视频函数，可处理单个或多个URL。
    支持 YouTube 平台，自动判断是否为播放列表或单视频。
    """
    if isinstance(play_url, list):  # ✅ 如果传入的是列表，逐个处理
        for i, url in enumerate(play_url, start=1):
            print(f"\n========== 🎬 开始下载第 {i} 个视频 ==========")
            download_video(platform, url, index=i, list=("list=" in url))
        return

    if platform == "youtube":
        print(f"🎉 {platform}: 开始工作 -> {play_url}")
        if list:
            youtube_playlist_url(play_url, platform)
        else:
            youtube_video_url(play_url, platform, index)

# =======================
# 主程序入口
# =======================
if __name__ == "__main__":
    # # ✅ 示例 1：下载单个视频
    # url_single = "https://www.youtube.com/watch?v=gV4AmREmjzk"

    # # ✅ 示例 2：下载播放列表
    # url_playlist = "https://www.youtube.com/watch?v=DFp3PbLkxho&list=PLdzd-EKM3IdFvGcw-DKMCPQGgo_1UKS0F"

    # ✅ 示例 3：多个 URL 自动识别
    urls = [
        "https://www.youtube.com/watch?v=DFp3PbLkxho&list=PLdzd-EKM3IdFvGcw-DKMCPQGgo_1UKS0F"
    ]

    download_video("youtube", urls)

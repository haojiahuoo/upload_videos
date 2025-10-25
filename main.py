from download.youtube import *
from logger.logger import *
from upload.upload_main import upload_main

def download_video(platform, play_url, index=1, is_playlist=True):
    if isinstance(play_url, list):  # ✅ 不冲突
        for i, url in enumerate(play_url, start=1):
            print(f"\n========== 🎬 开始下载第 {i} 个视频 ==========")
            download_video(platform, url, index=i, is_playlist=("list=" in url))
        return

    if platform == "youtube":
        print(f"🎉 {platform}: 开始工作 -> {play_url}")
        if is_playlist:
            youtube_playlist_url(play_url, platform)
        else:
            youtube_video_url(play_url, platform, index)


# =======================
# 主程序入口
# =======================
if __name__ == "__main__":
    
    urls = [
        "https://www.youtube.com/watch?v=zoZ5xzVffXQ&list=PLPff6vlxBmBHk-6D9_Cgk9qZidooDZoHQ"
    ]

    download_video("youtube", urls)

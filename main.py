from download.youtube import *
from upload.upload_main import upload_main

def download_video(platform, play_url, index=1, is_playlist=True):
    if isinstance(play_url, list):  # ✅ 不冲突
        for i, url in enumerate(play_url, start=1):
            print(f"\n========== 🎬 开始下载第 {i} 个视频 ==========")
            download_video(platform, url, index=i, is_playlist=("list=" in url))
            upload_main(platform)
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
        "https://www.youtube.com/watch?v=TS5PX9n6QfA",
        "https://www.youtube.com/watch?v=VzBbH6Yum50",
        "https://www.youtube.com/watch?v=0XhivXeWgsc",
        "https://www.youtube.com/watch?v=96g6m9JPWw4",
        "https://www.youtube.com/watch?v=Z3kFmqY_h9U",
        "https://www.youtube.com/watch?v=dGf9ao_QlFE",
        "https://www.youtube.com/watch?v=5369tcuJltc",
        "https://www.youtube.com/watch?v=-oK736-Qufo",
        "https://www.youtube.com/watch?v=-oH20xjQYI8",
        "https://www.youtube.com/watch?v=ypUHRJeZIS8",
        "https://www.youtube.com/watch?v=6nBd_q3GVGU"
    ]

    platform = "youtube"
    download_video(platform, urls)
    # upload_main(platform)

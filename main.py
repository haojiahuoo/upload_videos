from download.youtube import *
from upload.upload_main import upload_main

def download_video(platform_choice, platform, play_urls, is_playlist=False):
    """下载视频
    :param platform: 平台名称
    :param play_urls: 可以是单个URL或URL列表
    :param is_playlist: 是否为播放列表
    """
    # isinstance用于检查一个对象是否属于某个特定的类型
    # isinstance(对象, 类型)
    if not isinstance(play_urls, list):
        play_urls = [play_urls]
        
    if platform_choice == "1":
        # enumerate给可迭代对象（如列表、字符串等）添加索引，返回一个包含索引和值的枚举对象。
        # enumerate(可迭代对象, start=0) 可迭代对象：列表、元组、字符串等,start：索引的起始值（默认为0)
        for i, url in enumerate(play_urls, start=1):
            if platform == "youtube":
                print(f"🎉 {platform}: 开始工作 -> {url}")
                if is_playlist or "list=" in url:
                    youtube_playlist_url(url, platform)
                else:
                    print(f"\n========== 🎬 开始下载第 {i} 个视频 ==========")
                    youtube_video_url(url, platform, i)
        
        # 下载完成再上传           
        upload_main(platform)
    
    if platform_choice == "2":
        # enumerate给可迭代对象（如列表、字符串等）添加索引，返回一个包含索引和值的枚举对象。
        # enumerate(可迭代对象, start=0) 可迭代对象：列表、元组、字符串等,start：索引的起始值（默认为0)
        for i, url in enumerate(play_urls, start=1):
            if platform == "youtube":
                print(f"🎉 {platform}: 开始工作 -> {url}")
                if is_playlist or "list=" in url:
                    youtube_playlist_url(url, platform, upload=True)
                else:
                    print(f"\n========== 🎬 开始下载第 {i} 个视频 ==========")
                    youtube_video_url(url, platform, i)
                    # 下载完成再上传           
                    upload_main(platform)
    
    if platform_choice == "3":
        # enumerate给可迭代对象（如列表、字符串等）添加索引，返回一个包含索引和值的枚举对象。
        # enumerate(可迭代对象, start=0) 可迭代对象：列表、元组、字符串等,start：索引的起始值（默认为0)
        for i, url in enumerate(play_urls, start=1):
            if platform == "youtube":
                print(f"🎉 {platform}: 开始工作 -> {url}")
                if is_playlist or "list=" in url:
                    youtube_playlist_url(url, platform)
                else:
                    print(f"\n========== 🎬 开始下载第 {i} 个视频 ==========")
                    youtube_video_url(url, platform, i)
                    
    if platform_choice == "4":
        upload_main(platform)
        
def show_platform_menu():
    """显示平台选择菜单"""
    print("\n" + "="*60)
    print("🎯 请选择下载和上传的方式:")
    print("="*60)
    print("1. 全部下载完再上传")
    print("2. 下载一个上传一个") 
    print("3. 只下载")
    print("4. 只上传")
    print("="*60)

# =======================
# 主程序入口
# =======================
if __name__ == "__main__":
    
    platform = "youtube"
    # urls = [
    #     "https://www.youtube.com/watch?v=TS5PX9n6QfA",
    #     "https://www.youtube.com/watch?v=VzBbH6Yum50",
    #     "https://www.youtube.com/watch?v=0XhivXeWgsc",
    #     "https://www.youtube.com/watch?v=96g6m9JPWw4",
    #     "https://www.youtube.com/watch?v=Z3kFmqY_h9U",
    #     "https://www.youtube.com/watch?v=dGf9ao_QlFE",
    #     "https://www.youtube.com/watch?v=5369tcuJltc",
    #     "https://www.youtube.com/watch?v=-oK736-Qufo",
    #     "https://www.youtube.com/watch?v=-oH20xjQYI8",
    #     "https://www.youtube.com/watch?v=ypUHRJeZIS8",
    #     "https://www.youtube.com/watch?v=6nBd_q3GVGU"
    # ]
    urls = ["https://www.youtube.com/watch?v=MLnE2lS5zr8&list=PL-szjqIBRvM9OhOnaG7wdUo2hhFmBXCPu"]
    
    show_platform_menu()
    platform_choice = input("请输入平台选择 (1/2/3/4/5): ").strip()
    
    if platform_choice in ["1", "2", "3", "4"]:
        download_video(platform_choice, platform, urls)


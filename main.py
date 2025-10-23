from download.youtube import *
from logger.logger import *

def download_video(platform, play_url, list=True):
    if  platform == "youtube" and list == True:
        print(f"🎉 {platform}: 开始工作")
        youtube_playlist_url(play_url)
        

    elif platform == "youtube" and list == False:
        print(f"🎉 {platform}: 开始工作")
        youtube_video_url(play_url)
        
# 主程序入口
# =======================
if __name__ == "__main__":
    
    url = "https://www.youtube.com/watch?v=9ebyooYKBRg&list=PL4l-k0vRpXbfwhxbJN50O00xgnwajYx1K"       
    download_video("youtube", url)
    # url = "https://www.youtube.com/watch?v=qP-7GNoDJ5c"       
    # download_video("youtube", url, list=False)
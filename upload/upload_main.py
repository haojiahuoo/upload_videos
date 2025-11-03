# main.py
# --- download.py 顶部添加 ---
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from upload.douyin import DouyinUploader
from upload.kuaishou import KuaishouUploader
from upload.bibi import BibiUploader
from upload.weixin import WeixinUploader
import os, time, threading
from pathlib import Path
from config import DOWNLOAD_ROOT, UPLOAD_ROOT, ACCOUNT_NAME
from utils.common_utils import *

bilibili_upload = BibiUploader()
kuaishou_upload = KuaishouUploader()
douyin_upload = DouyinUploader()
weixin_upload = WeixinUploader()

def list_media_files(directory, platform, site_name):
    """列出目录中的所有视频和图片文件"""
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.m4v', '.flv', '.wmv', '.webm']
    image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.gif']

    videos, images = [], []

    # 遍历文件夹
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        if not os.path.isfile(file_path):
            continue  # 跳过子目录

        file_title = Path(filename).stem
        file_size = os.path.getsize(file_path) // (1024 * 1024)
        ext = Path(filename).suffix.lower()

        # 判断类型
        if ext in video_extensions:
            upload_done = get_record(platform, "upload", file_path, site_name)
            if not upload_done or not upload_done.get("done"):
                videos.append({
                    'path': file_path,
                    'title': file_title,
                    'filename': filename,
                    'size': file_size
                })
        elif ext in image_extensions:
            images.append({
                'path': file_path,
                'title': file_title,
                'filename': filename,
                'size': file_size
            })

    # 按文件名排序
    videos.sort(key=lambda x: x['filename'])
    images.sort(key=lambda x: x['filename'])

    # 打印视频
    print(f"🎥 找到 {len(videos)} 个视频文件:")
    for v in videos:
        print(f"🎬 标题: {v['title']}")
        print(f"📁 文件名: {v['filename']}")
        print(f"📍 路径: {v['path']}")
        print(f"📊 大小: {v['size']} MB")
        print("-" * 50)

    # # 打印图片
    # print(f"\n🖼️ 找到 {len(images)} 张图片:")
    # for img in images:
    #     print(f"🖼️ 标题: {img['title']}")
    #     print(f"📁 文件名: {img['filename']}")
    #     print(f"📍 路径: {img['path']}")
    #     print(f"📊 大小: {img['size']} MB")
    #     print("-" * 50)

    return {
        'videos': videos,
        'images': images
    }

def upload_single_platform(platform_choice, platform):
    """上传到单个指定平台"""
    
    folder_path = UPLOAD_ROOT
    if not os.path.exists(folder_path):
        print(f"❌ 目录不存在: {folder_path}")
        return
    
    browsers = []
    try:
        if platform_choice == "1":
            # 上传到抖音
            media_files = list_media_files(folder_path, platform, "douyin")
            if not media_files:  
                print(f"❌ 抖音：没有找到视频文件")
            elif media_files["videos"] == []:
                print(f"✅ 抖音：视频文件已经上传")
            else:
                douyin = douyin_upload.upload_to_douyin(media_files, platform)
                browsers.append(douyin)
                    
        elif platform_choice == "2":
            # 上传到快手
            media_files = list_media_files(folder_path, platform, "kuaishou")
            if not media_files:  
                print(f"❌ 快手：没有找到视频文件")
            elif media_files["videos"] == []:
                print(f"✅ 快手：视频文件已经上传")
            else:
                kuaishou = kuaishou_upload.upload_to_kuaishou(media_files, platform)
                browsers.append(kuaishou)  
                    
        elif platform_choice == "3":
            # 上传到B站   
            media_files = list_media_files(folder_path, platform, "bilibili")
            if not media_files:  
                print(f"❌ B站：没有找到视频文件")
            elif media_files["videos"] == []:
                print(f"✅ B站：视频文件已经上传")
            else:
                bili = bilibili_upload.upload_to_bibi(media_files, platform)
                browsers.append(bili)
        
        elif platform_choice == "4":
            # 上传到微信视频号   
            media_files = list_media_files(folder_path, platform, "weixin")
            if not media_files:  
                print(f"❌ 微信视频号：没有找到视频文件")
            elif media_files["videos"] == []:
                print(f"✅ 微信视频号：视频文件已经上传")
            else:
                weixin = weixin_upload.upload_to_weixin(media_files, platform)
                browsers.append(weixin)
        
        else:
            print("❌ 无效的平台选择")
            return

        # ✅ 如果没有异常，自动关闭浏览器
        print("\n🎉 上传完成！浏览器即将自动关闭...")
        for browser in browsers:
            if browser:
                browser.quit()

    except Exception as e:
        # ⚠️ 如果出错，提示手动关闭
        print(f"\n❌ 上传过程中出现错误：{e}")
        input("按回车键手动关闭浏览器...")
        for browser in browsers:
            if browser:
                try:
                    browser.quit()
                except:
                    pass

def upload_sequential(platform):
    """顺序上传到所有平台（一个平台完成后开始下一个）"""
    folder_path = UPLOAD_ROOT
    if not os.path.exists(folder_path):
        print(f"❌ 目录不存在: {folder_path}")
        return

    # 存储浏览器实例，最后统一关闭
    browsers = []
    
    try:
        # 上传到抖音
        media_files = list_media_files(folder_path, platform, "douyin")
        if not media_files:  
            print(f"❌ 抖音：没有找到视频文件")
        elif media_files["videos"] == []:
            print(f"✅ 抖音：视频文件已经上传")
        else:
            douyin = douyin_upload.upload_to_douyin(media_files, platform)
            browsers.append(douyin)
        
        # 上传到快手
        media_files = list_media_files(folder_path, platform, "kuaishou")
        if not media_files:  
            print(f"❌ 快手：没有找到视频文件")
        elif media_files["videos"] == []:
            print(f"✅ 快手：视频文件已经上传")
        else:
            kuaishou = kuaishou_upload.upload_to_kuaishou(media_files, platform)
            browsers.append(kuaishou)
        
        # 上传到B站
        media_files = list_media_files(folder_path, platform, "bilibili")
        if not media_files:  
            print(f"❌ B站：没有找到视频文件")
        elif media_files["videos"] == []:
            print(f"✅ B站：视频文件已经上传")
        else:
            bili = bilibili_upload.upload_to_bibi(media_files, platform)
            browsers.append(bili)
        
        # 上传到微信视频号
        media_files = list_media_files(folder_path, platform, "weixin")
        if not media_files:  
            print(f"❌ 微信视频号：没有找到视频文件")
        elif media_files["videos"] == []:
            print(f"✅ 微信视频号：视频文件已经上传")
        else:
            weixin = weixin_upload.upload_to_weixin(media_files, platform)
            browsers.append(weixin)
        
        # 可以继续添加其他平台...
        
    finally:
        # ✅ 如果没有异常，自动关闭浏览器
        print("\n🎉 上传完成！浏览器即将自动关闭...")
        for browser in browsers:
            if browser:
                browser.quit()

def show_platform_menu():
    """显示平台选择菜单"""
    print("\n" + "="*60)
    print("🎯 请选择要上传的平台:")
    print("="*60)
    print("1. 抖音")
    print("2. 快手") 
    print("3. B站")
    print("4. 微信")
    print("5. 抖音 + 快手 + B站 + 微信 (所有平台)")
    print("="*60)

def upload_main(platform):
    """主程序"""
    
    # # 自动上传
    # upload_sequential(platform)
    
    #  手动选择上传
    # 显示平台选择菜单
    show_platform_menu()
    platform_choice = input("请输入平台选择 (1/2/3/4/5): ").strip()
    
    if platform_choice in ["1", "2", "3", "4"]:
        # 单个平台，直接上传
        upload_single_platform(platform_choice, platform)
    
    elif platform_choice == "5":
        # 多个平台顺序上传
        upload_sequential(platform)
        
    else:
        print("❌ 无效的平台选择")

# if __name__ == "__main__":
#     upload_main()
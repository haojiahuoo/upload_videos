# main.py
from upload.douyin import DouyinUploader
from upload.kuaishou import KuaishouUploader
from upload.bibi import BibiUploader
import os
from pathlib import Path
import time
import threading

def list_video_files(directory):
    """列出目录中的所有视频文件"""
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.m4v', '.flv', '.wmv', '.webm']
    
    video_files = []
    for filename in os.listdir(directory):
        if any(filename.lower().endswith(ext) for ext in video_extensions):
            file_path = os.path.join(directory, filename)
            file_title = Path(filename).stem
            file_size = os.path.getsize(file_path) // (1024 * 1024)
            
            video_files.append({
                'path': file_path,
                'title': file_title,
                'filename': filename,
                'size': file_size
            })
    
    video_files.sort(key=lambda x: x['filename'])
    
    print(f"📁 找到 {len(video_files)} 个视频文件:")
    for video in video_files:
        print(f"🎬 视频: {video['title']}")
        print(f"📁 文件名: {video['filename']}")
        print(f"📍 路径: {video['path']}")
        print(f"📊 大小: {video['size']} MB")
        print("-" * 50)
    
    return video_files

def upload_to_douyin(video_files):
    """上传到抖音"""
    print("\n" + "="*50)
    print("🚀 开始上传到抖音")
    print("="*50)
    
    douyin = DouyinUploader()
    if douyin.login():
        for i, video in enumerate(video_files, 1):
            print(f"\n📤 抖音：正在上传第 {i}/{len(video_files)} 个视频: {video['title']}")
            success = douyin.upload_video(video['path'], video['title'])
            
            if success:
                print(f"✅ 抖音：第 {i} 个视频上传成功")
            else:
                print(f"❌ 抖音：第 {i} 个视频上传失败")
            
            # 上传间隔
            if i < len(video_files):
                print("⏳ 抖音：等待10秒后继续下一个视频...")
                time.sleep(10)
    else:
        print("❌ 抖音：登录失败，跳过抖音上传")
    
    print("🎉 抖音：所有视频上传完成")
    return douyin

def upload_to_kuaishou(video_files):
    """上传到快手"""
    print("\n" + "="*50)
    print("🚀 开始上传到快手")
    print("="*50)
    
    kuaishou = KuaishouUploader()
    if kuaishou.login():
        for i, video in enumerate(video_files, 1):
            print(f"\n📤 快手：正在上传第 {i}/{len(video_files)} 个视频: {video['title']}")
            success = kuaishou.upload_video(video['path'], video['title'])
            
            if success:
                print(f"✅ 快手：第 {i} 个视频上传成功")
            else:
                print(f"❌ 快手：第 {i} 个视频上传失败")
            
            # 上传间隔
            if i < len(video_files):
                print("⏳ 快手：等待10秒后继续下一个视频...")
                time.sleep(10)
    else:
        print("❌ 快手：登录失败，跳过快手上传")
    
    print("🎉 快手：所有视频上传完成")
    return kuaishou


def upload_to_bibi(video_files):
    """上传到B站"""
    print("\n" + "="*50)
    print("🚀 开始上传到B站")
    print("="*50)
    
    bibi = BibiUploader()
    if bibi.login():
        for i, video in enumerate(video_files, 1):
            print(f"\n📤 B站：正在上传第 {i}/{len(video_files)} 个视频: {video['title']}")
            success = bibi.upload_video(video['path'], video['title'])
            
            if success:
                print(f"✅ B站：第 {i} 个视频上传成功")
            else:
                print(f"❌ B站：第 {i} 个视频上传失败")
            
            # 上传间隔
            if i < len(video_files):
                print("⏳ B站：等待5秒后继续下一个视频...")
                time.sleep(5)
    else:
        print("❌ B站：登录失败，跳过B站上传")
        
    bibi.fapu_video() 
    print("🎉 B站：所有视频上传完成")
    return bibi

def upload_single_platform(platform_choice, video_files):
    """上传到单个指定平台"""
    browsers = []
    
    try:
        if platform_choice == "1":
            # 上传到抖音
            douyin = upload_to_douyin(video_files)
            browsers.append(douyin)
        elif platform_choice == "2":
            # 上传到快手
            kuaishou = upload_to_kuaishou(video_files)
            browsers.append(kuaishou)    
        elif platform_choice == "3":
            # 上传到B站
            bibi = upload_to_bibi(video_files)
            browsers.append(bibi)
        elif platform_choice == "4":
            # 上传到抖音\快手\B站
            douyin = upload_to_douyin(video_files)
            browsers.append(douyin)
            kuaishou = upload_to_kuaishou(video_files)
            browsers.append(kuaishou)
            bibi = upload_to_bibi(video_files)
            browsers.append(bibi)
        else:
            print("❌ 无效的平台选择")
            return
    
    finally:
        if browsers:
            input("\n🎉 上传完成！按回车键关闭浏览器...")
            for browser in browsers:
                if browser:
                    browser.quit()

def upload_sequential():
    """顺序上传到所有平台（一个平台完成后开始下一个）"""
    folder_path = r"E:\\Videos\\NA"
    if not os.path.exists(folder_path):
        print(f"❌ 目录不存在: {folder_path}")
        return
    
    video_files = list_video_files(folder_path)
    if not video_files:
        print("❌ 没有找到视频文件")
        return
    
    # 存储浏览器实例，最后统一关闭
    browsers = []
    
    try:
        # 上传到抖音
        douyin = upload_to_douyin(video_files)
        browsers.append(douyin)
        
        # 上传到快手
        kuaishou = upload_to_kuaishou(video_files)
        browsers.append(kuaishou)
        
        # 上传到B站
        bibi = upload_to_bibi(video_files)
        browsers.append(bibi)
        
        # 可以继续添加其他平台...
        
    finally:
        # 所有平台完成后关闭浏览器
        input("\n🎉 所有平台上传完成！按回车键关闭所有浏览器...")
        for browser in browsers:
            if browser:
                browser.quit()

def upload_parallel():
    """并行上传到所有平台（同时进行）"""
    folder_path = r"E:\\Videos\\NA"
    if not os.path.exists(folder_path):
        print(f"❌ 目录不存在: {folder_path}")
        return
    
    video_files = list_video_files(folder_path)
    if not video_files:
        print("❌ 没有找到视频文件")
        return
    
    # 创建线程
    threads = []
    
    # 抖音上传线程
    douyin_thread = threading.Thread(target=upload_to_douyin, args=(video_files,))
    threads.append(douyin_thread)
    
    # 快手上传线程
    kuaishou_thread = threading.Thread(target=upload_to_kuaishou, args=(video_files,))
    threads.append(kuaishou_thread)
    
    # B站上传线程
    kuaishou_thread = threading.Thread(target=upload_to_bibi, args=(video_files,))
    threads.append(kuaishou_thread)
    
    # 启动所有线程
    print("🚀 开始并行上传到所有平台...")
    for thread in threads:
        thread.start()
    
    # 等待所有线程完成
    for thread in threads:
        thread.join()
    
    print("🎉 所有平台并行上传完成！")

def show_platform_menu():
    """显示平台选择菜单"""
    print("\n" + "="*60)
    print("🎯 请选择要上传的平台:")
    print("="*60)
    print("1. 抖音")
    print("2. 快手") 
    print("3. B站")
    print("4. 抖音 + 快手 + B站 (所有平台)")
    print("="*60)

def show_upload_mode_menu():
    """显示上传模式菜单"""
    print("\n" + "="*60)
    print("🚀 请选择上传模式:")
    print("="*60)
    print("1. 顺序上传（一个平台完成后再开始下一个）")
    print("2. 并行上传（所有平台同时进行）")
    print("="*60)

def main():
    """主程序"""
    # 检查视频目录
    folder_path = r"E:\处理完的数据\YouTube"
    if not os.path.exists(folder_path):
        print(f"❌ 目录不存在: {folder_path}")
        return
    
    video_files = list_video_files(folder_path)
    if not video_files:
        print("❌ 没有找到视频文件")
        return
    
    # 显示平台选择菜单
    show_platform_menu()
    platform_choice = input("请输入平台选择 (1/2/3/4): ").strip()
    
    if platform_choice in ["1", "2", "3"]:
        # 单个平台，直接上传
        upload_single_platform(platform_choice, video_files)
    
    elif platform_choice == "4":
        # 多个平台，选择上传模式
        show_upload_mode_menu()
        mode_choice = input("请输入上传模式 (1/2): ").strip()
        
        if mode_choice == "1":
            upload_sequential()
        elif mode_choice == "2":
            upload_parallel()
        else:
            print("无效选择，使用默认顺序上传")
            upload_sequential()
    
    else:
        print("❌ 无效的平台选择")

if __name__ == "__main__":
    main()
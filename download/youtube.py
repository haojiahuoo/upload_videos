# --- download.py 顶部添加 ---
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import json, os, glob
import subprocess   
from utils.translate import *
from utils.common_utils import *
from utils.translate import *
from utils.convert_vtt_ass import *
from utils.embed_subtitle import *
from utils.segment_video import segment_video
from config import COOKIES_BROWSER, MAX_SEGMENT_DURATION, DOWNLOAD_ROOT

def chinese_title(title, video_path):
    # 判断标题是否含中文
    if contains_chinese(title):
        title_cn = title
    else:
        title_cn = translate_text(title)  # 你需要实现这个翻译函数
        title_cn = title_cn.rstrip("。！？.,!?")

    # 重命名视频文件为 title
    video_file = Path(video_path)
    new_video_path = video_file.with_name(f"{title_cn}{video_file.suffix}")
    os.rename(video_path, new_video_path)  # 重命名文件
    print(f"🎬 视频文件已重命名为: {new_video_path.name}")
    
    return str(new_video_path), title_cn


def get_video_info(video_url):
    """获取视频信息，包括是否有中文字幕和标题"""
    try:
        cmd = [
            "yt-dlp",
            "--cookies-from-browser", "firefox",
            "--skip-download",
            "--dump-single-json",
            video_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("❌ yt-dlp 执行失败:", result.stderr)
            return False, None, None

        info = json.loads(result.stdout) # 解析 JSON 信息
        title = info.get("title", "unknown_title") # 获取标题
        duration = info.get("duration", 0) # 获取时长（秒）
        subs = info.get("subtitles", {}) or {} # 获取字幕信息
        auto_subs = info.get("automatic_captions", {}) or {} # 获取自动字幕信息
        all_langs = list(subs.keys()) + list(auto_subs.keys()) # 合并字幕语言列表
        has_zh_subs = any(lang.startswith("zh") for lang in all_langs) # 检查是否有中文字幕
        return has_zh_subs, title, duration

    except Exception as e:
        print("❌ 无法检测字幕信息:", e)
        return False, None, None


def download_video(video_url, zh_available, index=1):
    """下载视频，返回视频文件路径和字幕文件路径（如果有）"""
    
    full_video_path = get_record(video_url)
    if full_video_path:
        print(f"⚠️ 视频已下载，跳过：{full_video_path}")
        # 尝试找对应字幕
        base = os.path.splitext(full_video_path)[0]
        vtt_files = glob.glob(base + "*.vtt")
        vtt_path = vtt_files[0] if vtt_files else None
        return full_video_path, vtt_path

    temp_video_name = f"temp_{index:02}.mp4"
    temp_video_path = os.path.join(DOWNLOAD_ROOT, temp_video_name)

    cmd = [
        "yt-dlp",
        "--cookies-from-browser", COOKIES_BROWSER,
        "-f", "best",
        "--merge-output-format", "mp4",
        "-o", temp_video_path,
        "--write-description",
        "--write-thumbnail",
        "--convert-thumbnails", "jpg",
        "--write-subs",
        "--write-auto-subs",
    ]

    if zh_available:
        cmd += ["--embed-subs", "--sub-langs", "zh-Hans,zh,zh-Hant", "--sub-format", "ass,vtt"]
        is_english_sub = False
    else:
        cmd += ["--sub-langs", "en,en-US", "--sub-format", "ass,vtt"]
        

    cmd.append(video_url)
    print(f"▶️ 正在下载完整视频：{temp_video_name}")
    result = subprocess.run([arg for arg in cmd if arg], text=True)

    if result.returncode != 0:
        print("⚠️ 完整视频下载失败，将按段下载。")
        return None, None
    else:
        print("✅ 视频下载完成（完整视频）")
        record_download(video_url, temp_video_path, category="videos", platform="youtube", mode="download")

    # 自动找到字幕文件
    base = os.path.splitext(temp_video_path)[0]

    # 查找对应的字幕文件（可能带语言后缀）
    ass_files = glob.glob(base + "*.ass")
    vtt_files = glob.glob(base + "*.vtt")

    subs_path = None

    # 优先使用 ASS 字幕
    if ass_files:
        subs_path = ass_files[0]
        print(f"🎬 找到 ASS 字幕文件：{subs_path}")
    elif vtt_files:
        subs_path = vtt_files[0]
        print(f"🎬 找到 VTT 字幕文件：{subs_path}")
    else:
        print("⚠️ 未找到字幕文件。")
        return temp_video_path, None


    # ========== 自动翻译逻辑 ==========
    if subs_path:
        if is_english_sub:
            print(f"🌍 检测到英文字幕，开始翻译：{subs_path}")
            if subs_path.endswith(".vtt"):
                subs_path = translate_vtt_file(subs_path, batch_size=10)
            elif subs_path.endswith(".ass"):
                subs_path = translate_ass_file(subs_path)  # 需要你实现的 ASS 翻译函数
            print(f"✅ 翻译完成：{subs_path}")
        else:
            print(f"检测到中文字幕，跳过翻译。")

    return temp_video_path, subs_path   

def get_playlist_video_urls(playlist_url):
    """获取播放列表中所有视频的 URL"""
    print("📋 正在获取播放列表视频链接...")
    cmd = [
        "yt-dlp",
        "--flat-playlist",
        "--dump-single-json",
        playlist_url
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    info = json.loads(result.stdout)
    entries = info.get("entries", [])
    urls = [entry["url"] for entry in entries]
    return urls

def youtube_playlist_url(playlist_url):
    """下载播放列表中的所有视频"""
    
    print("🚀 开始批量下载播放列表...")
    video_urls = get_playlist_video_urls(playlist_url)
    print(f"共检测到 {len(video_urls)} 个视频。")

    for idx, video_url in enumerate(video_urls, start=1):
        print(f"\n▶️ 正在下载第 {idx}/{len(video_urls)} 个视频：{video_url}")
        has_zh_subs, title, duration = get_video_info(video_url)  # 获取视频信息
        temp_video_path, subs_path = download_video(video_url, has_zh_subs, idx)
        ass_path = convert_vtt_ass(temp_video_path, subs_path)
        temp_video_path = embed_subtitle(temp_video_path, ass_path)
        video_path, title_cn = chinese_title(title, temp_video_path)
        if duration > MAX_SEGMENT_DURATION: 
            segment_video(video_path, title_cn, duration, idx)

    print("\n✅ 所有视频下载完成！")

    
def youtube_video_url(video_url):
    """下载单个视频"""
    print("🚀 开始下载单个视频...")
    has_zh_subs, title, duration = get_video_info(video_url)  # 获取视频信息
    temp_video_path, subs_path = download_video(video_url, has_zh_subs)
    ass_path = convert_vtt_ass(temp_video_path, subs_path)
    temp_video_path = embed_subtitle(temp_video_path, ass_path)
    video_path, title_cn = chinese_title(title, temp_video_path)
    if duration > MAX_SEGMENT_DURATION: 
        segment_video(video_path, title_cn, duration)
        
    print("\n✅ 视频下载完成！")
    
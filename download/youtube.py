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
from config import COOKIES_BROWSER, MAX_SEGMENT_DURATION, DOWNLOAD_ROOT, UPLOAD_ROOT

def chinese_title(title, video_path, index=1):
    # 判断标题是否含中文
    if contains_chinese(title):
        title_cn = title
    else:
        title_cn = translate_text(title)  # 你需要实现这个翻译函数
        # ① 去掉文件扩展名
        title_cn = os.path.splitext(title_cn)[0]

        # ② 删除多余的竖线和重复空格
        title_cn = re.sub(r'[|｜]+', ' ', title_cn)  # 竖线转空格
        title_cn = re.sub(r'\s{2,}', ' ', title_cn)  # 多空格合并

        # ③ 去掉结尾标点符号（中英文）
        title_cn = title_cn.rstrip("。！？.,!?|｜ ")

        # ④ 去掉首尾空格
        title_cn = title_cn.strip()

    # 重命名视频文件为 title
    video_file = Path(video_path)
    new_video_path = video_file.with_name(f"({index:02}){title_cn}{video_file.suffix}")
    
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
        print(f"duration : {duration}")
        print(f"all_langs : {all_langs}")
        return has_zh_subs, title, duration, all_langs

    except Exception as e:
        print("❌ 无法检测字幕信息:", e)
        return False, None, None


def download_video(video_url, zh_available, platform, all_langs, index=1):
    """下载视频，返回视频文件路径和字幕文件路径（如果有）"""
    temp_video_name = f"temp_{index:02}.mp4"
    temp_video_path = os.path.join(DOWNLOAD_ROOT, temp_video_name)

    # -------------------------
    # 统一初始化字幕语言标记
    # -------------------------
    is_english_sub = not zh_available

    # 判断是否已下载视频
    video_done = get_record(temp_video_path, platform, "download", video_url)
    if not video_done:
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
            cmd += ["--sub-langs", "zh-Hans,zh,zh-Hant", "--sub-format", "ass,vtt"]
        else:
            cmd += ["--sub-langs", "en,en-US", "--sub-format", "ass,vtt"]

        cmd.append(video_url)
        print(f"▶️ 正在下载完整视频：{temp_video_name}")
        result = subprocess.run(cmd, text=True)

        if result.returncode != 0:
            print("⚠️ 完整视频下载失败，将按段下载。")
            return None, None
        else:
            print("✅ 视频下载完成（完整视频）")
            record_download(video_url, True, temp_video_path, platform, mode="download")
    else:
        print(f"⚠️ 视频已下载，跳过：{temp_video_path}")

    # -------------------------
    # 处理字幕
    # -------------------------
    
    # 如果没有字幕，直接返回临时视频地址
    if all_langs == []:
        print("⚠️ 视频没有字幕，直接返回临时视频地址")
        return temp_video_path, None
    
    base = os.path.splitext(temp_video_path)[0]
    ass_files = glob.glob(base + "*.ass")
    vtt_files = glob.glob(base + "*.vtt")
    subs_path = None

    record_result = get_record(temp_video_path, platform, "download", "subtitles")
    # 安全获取 vtt 和 translate
    if isinstance(record_result, dict):
        vtt_state = record_result.get("vtt", False)
        translate_state = record_result.get("translate", False)
    else:
        vtt_state = False
        translate_state = False

    # =============== ASS 字幕优先 ===============
    if ass_files:
        subs_path = ass_files[0]
        print(f"🎬 找到 ASS 字幕文件：{subs_path}")

        if vtt_state and translate_state:
            print("✅ 字幕已处理过，直接使用")
            return temp_video_path, subs_path

        if is_english_sub:
            subs_path = translate_ass_file(subs_path)
            print(f"✅ 英文 ASS 字幕已翻译：{subs_path}")

        # 记录字幕状态
        record_download("subtitles", {"ass": True, "translate": True}, temp_video_path, platform, mode="download")
        return temp_video_path, subs_path

    # =============== VTT 字幕 ===============
    elif vtt_files:
        subs_path = vtt_files[0]
        print(f"🎬 找到 VTT 字幕文件：{subs_path}")

        if vtt_state and translate_state:
            print("✅ 字幕已处理过，直接使用")
            return temp_video_path, subs_path

        if is_english_sub:
            subs_path = translate_vtt_file(subs_path, batch_size=10)
            print(f"✅ 英文 VTT 字幕翻译完成：{subs_path}")

        # 记录字幕状态
        record_download("subtitles", {"vtt": True, "translate": True}, temp_video_path, platform, mode="download")
        return temp_video_path, subs_path

    # =============== 没找到字幕 ===============
    else:
        print("⚠️ 未找到字幕文件。")
        return temp_video_path, None



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

def process_video(video_url, platform, index=1):
    """处理单个视频的下载、字幕、嵌入、分段和记录"""
    try: 
        print(f"\n▶️ 正在处理第 {index} 个视频：{video_url}")
        name = f"E:\\Videos\\temp_{index:02}.mp4"
        title_record = get_record(name, platform="youtube", mode="download", done="title_cn")
        if title_record and title_record.get("done"):
            print(f"⚠️ 视频已经全部处理完，跳过...")
            return True
        
        else:
            # 获取视频信息
            has_zh_subs, title, duration, all_langs = get_video_info(video_url)
            
            # 下载视频和字幕
            temp_video_path, subs_path = download_video(video_url, has_zh_subs, platform, all_langs, index)
            if not all_langs == []: # 如果字幕为空
                ass_path = convert_vtt_ass(temp_video_path, subs_path)   # 把vtt转换为ass
                temp_video_path = embed_subtitle(temp_video_path, ass_path)  # 把ass字幕嵌入视频中

            # 生成中文标题和最终路径
            video_path, title_cn = chinese_title(title, temp_video_path, index)
            record_download("title_cn", title_cn, temp_video_path, platform="youtube", mode="download")

            # 如果视频太长则分段
            if duration > MAX_SEGMENT_DURATION:
                segment_video(video_path, title_cn, duration, index)

            print(f"✅ 第 {index} 个视频下载完成：{title_cn}")
            return True

    except Exception as e:
        print(f"❌ 第 {index} 个视频下载失败：{video_url}\n错误原因：{e}")
        return False


def youtube_playlist_url(playlist_url, platform):
    """下载播放列表中的所有视频"""
    print("🚀 开始批量下载播放列表...")
    video_urls = get_playlist_video_urls(playlist_url)
    print(f"共检测到 {len(video_urls)} 个视频。")

    success = 0
    for idx, video_url in enumerate(video_urls, start=1):
        if process_video(video_url, platform, idx):
            success += 1

    print(f"\n✅ 批量下载完成！成功 {success}/{len(video_urls)} 个视频。")


def youtube_video_url(video_url, platform, index):
    """下载单个视频"""
    print(f"🚀 开始下载第{index}个视频...")
    process_video(video_url, platform, index)
    print("\n✅ 视频下载完成！")

    
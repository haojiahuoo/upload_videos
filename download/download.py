# -*- coding: utf-8 -*-
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path
import glob

# 下载主目录
download_root = r"E:\Videos"
os.makedirs(download_root, exist_ok=True)  # 确保主目录存在

# Cookie 来源（可改为 "chrome" 或 "firefox"）
cookies_browser = "firefox"

# 单个视频最大下载时长（秒）—— 超过这个就自动分段
MAX_SEGMENT_DURATION = 30 * 60  # 30 分钟

# =======================
# 输出模板
# =======================
video_outtmpl = os.path.join(download_root, "%(playlist_title)s", "%(playlist_index)s - %(title)s.%(ext)s")
subs_outtmpl = os.path.join(download_root, "%(playlist_title)s", "%(playlist_index)s - %(title)s.%(lang)s.vtt")
desc_outtmpl = os.path.join(download_root, "%(playlist_title)s", "%(playlist_index)s - %(title)s.description")

# =======================
# 工具函数：检测是否有中文字幕
# =======================
def contains_chinese(text):
    """判断文本是否包含中文字符"""
    return any('\u4e00' <= c <= '\u9fff' for c in text)

def record_download(video_url, full_video_path):
    """记录已下载视频 URL 和本地路径"""
    record_file = os.path.join(download_root, "downloaded.txt")
    with open(record_file, "a", encoding="utf-8") as f:
        f.write(f"{video_url}|{full_video_path}\n")

def is_already_downloaded(video_url):
    """检查视频是否已经下载，返回本地路径（如果已下载）"""
    record_file = os.path.join(download_root, "downloaded.txt")
    if not os.path.exists(record_file):
        return None

    with open(record_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                url, path = line.split("|", 1)
                if url == video_url:
                    return path  # 找到已下载的视频，返回本地路径
            except ValueError:
                continue
    return None  # 没有找到



def translate(title):

    import requests
    import random
    import json
    from hashlib import md5

    # Set your own appid/appkey.
    appid = '20251020002479611'
    appkey = 'pUwpLZS1zzpCgYAzoS9s'

    # For list of language codes, please refer to `https://api.fanyi.baidu.com/doc/21`
    from_lang = 'en'
    to_lang =  'zh'

    endpoint = 'http://api.fanyi.baidu.com'
    path = '/api/trans/vip/translate'
    url = endpoint + path

    query = title

    # Generate salt and sign
    def make_md5(s, encoding='utf-8'):
        return md5(s.encode(encoding)).hexdigest()

    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)

    # Build request
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {'appid': appid, 'q': query, 'from': from_lang, 'to': to_lang, 'salt': salt, 'sign': sign}

    # Send request
    r = requests.post(url, params=payload, headers=headers)
    result = r.json()

    # Show response
    print(json.dumps(result, indent=4, ensure_ascii=False))
    return result["trans_result"][0]["dst"]

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

        info = json.loads(result.stdout)
        title = info.get("title", "unknown_title")
        subs = info.get("subtitles", {}) or {}
        auto_subs = info.get("automatic_captions", {}) or {}
        all_langs = list(subs.keys()) + list(auto_subs.keys())
        has_zh_subs = any(lang.startswith("zh") for lang in all_langs)
        print(f"ℹ️ 视频标题: {title}")
        print(f"ℹ️ 可用字幕语言: {all_langs}")   
        
        # 判断标题是否含中文
        if contains_chinese(title):
            title_cn = title
        else:
            title_cn = translate(title)  # 你需要实现这个翻译函数
            title_cn = title_cn.rstrip("。！？.,!?")
        return has_zh_subs, title_cn

    except Exception as e:
        print("❌ 无法检测字幕信息:", e)
        return False, None, None


# =======================
# 工具函数：获取视频时长
# =======================
def get_video_duration(video_url):
    """获取视频总时长（秒）"""
    try:
        cmd = [
            "yt-dlp",
            "--cookies-from-browser", "firefox",  # ⚠️ 必须加上 cookies
            "--skip-download",
            "--dump-single-json",
            video_url
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            print("⚠️ yt-dlp 执行失败:", result.stderr)
            return 0

        info = json.loads(result.stdout)
        return info.get("duration", 0)
    except Exception as e:
        print("⚠️ 无法获取视频时长:", e)
        return 0

# =======================
# 工具函数：下载单个视频（支持分段）
# =======================
def download_video(video_url, index):
    """
    下载完整视频，然后根据时长分段
    video_url: 视频链接
    index: 视频在列表中的序号（1 开始）
    """
    full_video_path = is_already_downloaded(video_url)
    if full_video_path:
        print(f"⚠️ 视频已下载，跳过：{full_video_path}")
        return full_video_path
        
    zh_available, title_cn = get_video_info(video_url)  # 返回是否有中文字幕 + 中文标题
    duration = get_video_duration(video_url)

    print(f"⏱️ 当前视频时长：{duration // 60} 分钟")

    # 中文序号前缀
    full_video_name = f"({index:02}){title_cn}.mp4"
    full_video_path = os.path.join(download_root, full_video_name)

    # 下载完整视频
    cmd = [
        "yt-dlp",
        "--cookies-from-browser", cookies_browser,
        "-f", "best",
        "--merge-output-format", "mp4",
        "-o", full_video_path,
        "--write-description",
        "--write-thumbnail",
        "--convert-thumbnails", "jpg",
        "--write-subs",          # 下载手动字幕
        "--write-auto-subs",     # 下载自动字幕
    ]

    # 如果有中文字幕，下载中文字幕，否则下载英文字幕
    if zh_available:
        cmd += ["--sub-langs", "zh-Hans,zh,zh-Hant", "--sub-format", "vtt"]
    else:
        cmd += ["--sub-langs", "en,en-US", "--sub-format", "vtt"]
    cmd.append(video_url)
    print(f"▶️ 正在下载完整视频：{full_video_path}")
    result = subprocess.run([arg for arg in cmd if arg], text=True)
    
    if result.returncode != 0:
        print("⚠️ 完整视频下载失败，将按段下载。")
    else:
        print("✅ 视频下载完成（完整视频）")
        record_download(video_url, full_video_path)  # 下载完成后记录
        return full_video_path
        
def embed_subtitles(full_video_path):
    # 假设 full_video_path 已经下载完成
    base = Path(full_video_path).with_suffix("")  # 去掉 .mp4
    subs_pattern = str(base) + "*.vtt"            # 匹配所有可能的字幕
    subs_files = glob.glob(subs_pattern)

    if subs_files:
        subs_file = subs_files[0]  # 找到第一个字幕文件
    else:
        subs_file = None

    if os.path.exists(subs_file):
        # 转义路径，让 ffmpeg 不会误判
        safe_subs = str(subs_file).replace("\\", "/")  # 用 / 代替 \ 最安全
        safe_video = str(full_video_path).replace("\\", "/")

        # 临时输出文件
        with tempfile.NamedTemporaryFile(suffix=".mp4", delete=False) as tmp_file:
            tmp_path = tmp_file.name.replace("\\", "/")  # FFmpeg 更安全

        ffmpeg_cmd = [
            "ffmpeg",
            "-i", safe_video,
            "-vf",
            f"subtitles=\"{safe_subs}\":force_style='FontName=SimHei,FontSize=36,PrimaryColour=&H00FFFF&,OutlineColour=&H000000&,BorderStyle=1'",
            "-c:a", "copy",
            tmp_path
        ]

        print(f"▶️ 正在嵌入字幕：{full_video_path}")
        result = subprocess.run(ffmpeg_cmd, text=True)

        if result.returncode == 0:
            os.replace(tmp_path, full_video_path)
            print("✅ 字幕嵌入完成，文件名保持不变")
        else:
            print("⚠️ 字幕嵌入失败，请检查 ffmpeg 命令或字幕文件。")
    else:
        print("⚠️ 未找到字幕文件，跳过嵌入。")

    # 替换原视频
    os.replace(tmp_path, full_video_path)
    print("✅ 字幕嵌入完成，文件名保持不变")
    # # 字幕嵌入完成后记录
    # record_download(video_url, full_video_path)  # 下载完成后记录
    
def segment_video(full_video_path, title_cn, index, duration):
    # 下载完成后分段
    if duration > MAX_SEGMENT_DURATION:
        num_parts = math.ceil(duration / MAX_SEGMENT_DURATION)
        part_len = duration / num_parts
        all_parts_exist = True
        for i in range(num_parts):
            start = int(i * part_len)
            end = int(min(duration, (i + 1) * part_len))
            part_name = f"({index:02}-{i+1}){title_cn}.mp4"
            part_path = os.path.join(download_root, part_name)
            ffmpeg_cmd = [
                "ffmpeg",
                "-y",
                "-i", full_video_path,
                "-ss", str(start),
                "-to", str(end),
                "-c", "copy",
                part_path
            ]
            print(f"▶️ 分段第 {i + 1}/{num_parts} ({start}-{end}s): {part_path}")
            subprocess.run(ffmpeg_cmd)
            
            # 检查该段文件是否生成且大小大于 0
            if not os.path.exists(part_path) or os.path.getsize(part_path) == 0:
                all_parts_exist = False
                print(f"❌ 分段 {i+1} 生成失败: {part_path}")

        # 如果所有分段都生成成功，删除原视频
        if all_parts_exist and os.path.exists(full_video_path):
            os.remove(full_video_path)
            print(f"🗑️ 原始完整视频已删除: {full_video_path}")
        elif not all_parts_exist:
            print("⚠️ 有分段未成功生成，原视频保留。")


# =======================
# 主流程：批量下载播放列表
# =======================
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


# =======================
# 主程序入口
# =======================

# =======================
# 配置参数
# =======================

# YouTube 播放列表 URL
video_url = "https://www.youtube.com/watch?v=05f8sG4OhZs"
full_video_path = download_video(video_url, 1)
embed_subtitles(full_video_path)
# playlist_url = "https://www.youtube.com/watch?v=rMmwC-qxnEI&list=PL4l-k0vRpXbfwhxbJN50O00xgnwajYx1K"  # ⚠️ 替换为你的播放列表链接
# print("🚀 开始批量下载播放列表...")
# video_urls = get_playlist_video_urls(playlist_url)
# print(f"共检测到 {len(video_urls)} 个视频。")

# for idx, video_url in enumerate(video_urls, start=1):
#     print(f"\n▶️ 正在下载第 {idx}/{len(video_urls)} 个视频：{video_url}")
#     download_video(video_url, idx)

print("\n✅ 所有视频下载完成！")

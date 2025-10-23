# common_utils.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os, json

download_root = "downloads"  # 你可以根据需要修改
record_file = os.path.join(download_root, "records.json")

def wait_for_element(driver, by, locator, timeout=60):
    """等待元素出现"""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))

def wait_for_element_clickable(driver, by, locator, timeout=60):
    """等待元素可点击"""
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable((by, locator)))

def check_element_exists(driver, by, locator, timeout=5):
    """检查元素是否存在"""
    try:
        wait_for_element(driver, by, locator, timeout)
        return True
    except:
        return False

def contains_chinese(text):
    """判断文本是否包含中文字符"""
    return any('\u4e00' <= c <= '\u9fff' for c in text)

def record_download(key, value, category, platform, mode):
    """
    记录下载或上传的文件信息（JSON格式）
    参数:
        video_url: 视频链接
        full_video_path: 本地文件路径
        category: "videos" | "subtitles" 字幕| "convert_vtt_ass" vtt转ass| "covers"
        platform: "youtube"（可扩展为bilibili、tiktok等）
        mode: "download" 或 "upload"
    """
    
    # 如果文件不存在，初始化结构
    if not os.path.exists(record_file):
        data = {
            platform: {
                mode: {"videos": {}, "subtitles": {}, "convert_vtt_ass": {}, "covers": {}},
            }
        }
    else:
        with open(record_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                # 如果文件损坏或为空，重新初始化
                data = {
                    platform: {
                            mode: {"videos": {}, "subtitles": {}, "dconvert_vtt_ass": {}, "covers": {}},
                    }
                }

    # 确保层级存在
    data.setdefault(platform, {})
    data[platform].setdefault(mode, {})
    data[platform][mode].setdefault(category, {})

    # 写入记录（以 video_url 为 key）
    data[platform][mode][category][key] = value

    # 保存 JSON 文件（格式化输出）
    os.makedirs(download_root, exist_ok=True)
    with open(record_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ 已记录 {platform}/{mode}/{category}: {key} -> {value}")


def get_record(video_url, platform="youtube"):
    if not os.path.exists(record_file):
        return None
    with open(record_file, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return None
    for mode in ("download", "upload"):
        for cat in ("videos", "subtitles", "descriptions", "covers"):
            if platform in data and mode in data[platform] and cat in data[platform][mode]:
                if video_url in data[platform][mode][cat]:
                    return data[platform][mode][cat][video_url]
    return None

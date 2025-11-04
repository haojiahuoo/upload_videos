# common_utils.py
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import os, json, shutil, re

download_root = "downloads"  # 你可以根据需要修改
record_file = os.path.join(download_root, "records.json")

def wait_for_element(driver, by, locator, timeout=60):
    """等待元素出现"""
    return WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, locator)))

def wait_for_elements(driver, by, locator):
    return WebDriverWait(driver, 30).until(EC.presence_of_all_elements_located((by, locator)))

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

def wait_for_element_disappear(driver, by, locator, timeout=5, check_visibility=True):
    """
    等待元素消失
    
    Args:
        driver: WebDriver实例
        by: 定位方式
        locator: 定位器
        timeout: 超时时间（秒）
        check_visibility: 是否检查可见性，True-等待元素不可见，False-等待元素从DOM中移除
    
    Returns:
        bool: 元素是否在超时时间内消失
    """
    try:
        if check_visibility:
            # 等待元素不可见（元素可能仍在DOM中但不可见）
            WebDriverWait(driver, timeout).until(
                EC.invisibility_of_element_located((by, locator))
            )
        else:
            # 等待元素从DOM中完全移除
            WebDriverWait(driver, timeout).until(
                lambda driver: len(driver.find_elements(by, locator)) == 0
            )
        return True
    except Exception as e:
        print(f"❌ 等待元素消失失败: {e}")
        return False
    
def clean_title(title):
    # 移除 (数字) 或 (数字-数字) 等前缀
    return re.sub(r'^\(\d+[^)]*\)\s*', '', title).strip()

def contains_chinese(text):
    """判断文本是否包含中文字符"""
    return any('\u4e00' <= c <= '\u9fff' for c in text)

def record_download(platform, mode, video_path, key, value):
    """
    记录下载或上传任务（支持嵌套结构）
    key:
        普通键，如 'video_url'、'description'、'upload_path'
        或字幕相关键，如 'vtt'、'translate'、'embed'
    """
    try:
        json.dumps(value)
    except TypeError:
        value = str(value)

    # 🔧 初始化数据结构
    if not os.path.exists(record_file):
        data = {}
    else:
        with open(record_file, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except json.JSONDecodeError:
                data = {}

    # ✅ 确保多层结构存在
    data.setdefault(platform, {})
    data[platform].setdefault(mode, {})
    data[platform][mode].setdefault(video_path, {})
    data[platform][mode][video_path].setdefault("subtitles", {"vtt": False, "translate": False})

    # ✅ 根据 key 分类更新
    if key in ("vtt", "ass", "translate", "embed"):
        # 更新字幕相关状态
        data[platform][mode][video_path]["subtitles"][key] = bool(value)
    else:
        # 其他普通任务（如 video_url、upload_path 等）
        data[platform][mode][video_path][key] = value

    # ✅ 保存 JSON 文件
    os.makedirs(download_root, exist_ok=True)
    with open(record_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"✅ 已记录 {platform}/{mode}/{video_path}: {key} -> {value}")



def get_record(platform, mode, video_path, done):
    """
    返回统一格式：
    - done="subtitles" 返回 {"vtt": bool, "translate": bool, "ass": bool}
    - 其他返回 {"done": bool}
    """
    if not os.path.exists(record_file):
        return None

    with open(record_file, "r", encoding="utf-8", errors="ignore") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            return None

    task_info = data.get(platform, {}).get(mode, {}).get(video_path, {})
    if not task_info:
        return None

    if done == "subtitles":
        # 如果没有“subtitles”键，就默认 False
        subtitles_info = task_info.get("subtitles", {})
        # 保证返回字典
        return {
            "vtt": subtitles_info.get("vtt", False),
            "translate": subtitles_info.get("translate", False)
        }
    else:
        return {"done": task_info.get(done, False)}


        
# -----------------------------
# ✅ 上传完成后的目标文件夹（全局定义）
# -----------------------------
UPLOAD_DONE_DIR = r"E:\Videos\Uploaded"

def move_to_uploaded_folder(file_path, target_dir=UPLOAD_DONE_DIR):
    """上传完后移动视频文件"""
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    new_path = os.path.join(target_dir, os.path.basename(file_path))
    try:
        shutil.move(file_path, new_path)
        print(f"✅ 文件已移动到：{new_path}")
    except Exception as e:
        print(f"⚠️ 移动文件失败：{e}")    


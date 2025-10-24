import requests
import random
from hashlib import md5
import re, time, os

# ======== 百度翻译配置 ========
appid = '20251020002479611'
appkey = 'pUwpLZS1zzpCgYAzoS9s'

from_lang = 'en'
to_lang = 'zh'

endpoint = 'http://api.fanyi.baidu.com'
path = '/api/trans/vip/translate'
url = endpoint + path


def make_md5(s, encoding='utf-8'):
    """计算MD5签名"""
    return md5(s.encode(encoding)).hexdigest()


def translate_text(query):
    """🟦 单句翻译函数"""
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + query + str(salt) + appkey)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'appid': appid,
        'q': query,
        'from': from_lang,
        'to': to_lang,
        'salt': salt,
        'sign': sign
    }

    r = requests.post(url, params=payload, headers=headers)
    result = r.json()
    if "trans_result" in result:
        return result["trans_result"][0]["dst"]
    else:
        print("❌ 翻译出错：", result)
        return query


def translate_batch(sentences):
    """🟩 批量翻译函数，将多行文字合并发送，减少API调用次数"""
    # 百度API支持批量翻译，只需用 '\n' 分隔多条文本
    joined = "\n".join(sentences)
    salt = random.randint(32768, 65536)
    sign = make_md5(appid + joined + str(salt) + appkey)
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    payload = {
        'appid': appid,
        'q': joined,
        'from': from_lang,
        'to': to_lang,
        'salt': salt,
        'sign': sign
    }

    r = requests.post(url, params=payload, headers=headers)
    result = r.json()

    if "trans_result" in result:
        # 按顺序提取每条翻译
        return [item["dst"] for item in result["trans_result"]]
    else:
        print("❌ 批量翻译出错：", result)
        return sentences


def translate_vtt_file(input_file, output_file=None, batch_size=10):
    """🟨 翻译整个VTT文件，保持时间轴，批量翻译字幕内容（中文在英文下方，自动覆盖原文件）"""
    import re, time, os

    # 如果没有指定 output_file，就覆盖原文件
    if output_file is None:
        output_file = input_file

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    translated_lines = []
    text_pattern = re.compile(r"^\d\d:\d\d:\d\d\.\d+ --> \d\d:\d\d:\d\d\.\d+")
    buffer = []          # 待翻译文本
    buffer_index = []    # 文本对应的插入位置

    for i, line in enumerate(lines):
        stripped = line.strip()

        # 跳过头部信息、时间轴、中文、空行等
        if (
            stripped == ""
            or stripped.startswith("WEBVTT")
            or text_pattern.match(stripped)
            or stripped.lower().startswith("kind")
            or stripped.lower().startswith("language")
            or "：" in stripped  # 中文符号说明行
        ):
            translated_lines.append(line)
            continue

        # 数字序号
        if stripped.isdigit():
            translated_lines.append(line)
            continue

        # 英文字幕内容
        buffer.append(stripped)
        buffer_index.append(len(translated_lines))
        translated_lines.append(line)

        # 达到批量大小 -> 翻译
        if len(buffer) >= batch_size:
            translated_results = translate_batch(buffer)

            # ✅ 清理翻译结果（去掉开头/结尾的标点符号和空白）
            cleaned_results = [
                re.sub(r'^[\s"“”‘’、，。！？!?.；;：:【】\[\]（）()…—-]+|[\s"“”‘’、，。！？!?.；;：:【】\[\]（）()…—-]+$', '', t.strip())
                for t in translated_results
            ]

            # ✅ 逆序插入，防止索引错位
            for idx, trans in sorted(zip(buffer_index, cleaned_results), reverse=True):
                translated_lines.insert(idx + 1, trans + "\n")
            buffer.clear()
            buffer_index.clear()
            time.sleep(1)

    # 处理剩余未翻译的部分
    if buffer:
        translated_results = translate_batch(buffer)
        cleaned_results = [
            re.sub(r'^[\s"“”‘’、，。！？!?.；;：:【】\[\]（）()…—-]+|[\s"“”‘’、，。！？!?.；;：:【】\[\]（）()…—-]+$', '', t.strip())
            for t in translated_results
        ]
        for idx, trans in sorted(zip(buffer_index, cleaned_results), reverse=True):
            translated_lines.insert(idx + 1, trans + "\n")

    # ✅ 直接覆盖原文件
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(translated_lines)

    print(f"✅ 已翻译并覆盖原文件：{os.path.basename(output_file)}")
    return output_file

def translate_ass_file(ass_path, translate_func=None):
    """
    翻译 .ass 字幕文件（如为英文）并生成新的 .zh.ass 文件

    参数：
        ass_path (str): 原始 .ass 文件路径
        translate_func (callable): 翻译函数，输入英文句子返回中文翻译
                                   如果未提供，会打印原文（仅调试用）

    返回：
        str: 翻译后的 .ass 文件路径
    """
    if not os.path.exists(ass_path):
        print(f"❌ 找不到字幕文件：{ass_path}")
        return None

    translated_path = ass_path.replace(".ass", ".zh.ass")

    # 读取原始文件
    with open(ass_path, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()

    new_lines = []
    dialogue_pattern = re.compile(r"^Dialogue:\s*\d+,")

    for line in lines:
        # 找到字幕行（以 Dialogue: 开头）
        if dialogue_pattern.match(line):
            parts = line.split(",", 9)
            if len(parts) > 9:
                text = parts[9].strip()

                # 跳过空白或无效行
                if not text or text.startswith("{") and text.endswith("}"):
                    new_lines.append(line)
                    continue

                # 调用翻译函数
                if translate_func:
                    try:
                        translated = translate_func(text)
                    except Exception as e:
                        print(f"⚠️ 翻译失败：{text} -> {e}")
                        translated = text
                else:
                    translated = f"[CN] {text}"

                # 替换文本部分
                parts[9] = translated
                line = ",".join(parts)
        new_lines.append(line)

    # 写出新的文件
    with open(translated_path, "w", encoding="utf-8") as f:
        f.writelines(new_lines)

    print(f"✅ 翻译完成，生成文件：{translated_path}")
    return translated_path

# # ======== 使用示例 ========
# if __name__ == "__main__":
#     # 单句翻译
#     text = "Hello everyone, welcome to our new video."
#     result = translate_text(text)
#     print("单句翻译：", result)

    # # 批量翻译VTT文件
    # translate_vtt_file("input.vtt", "output_translated.vtt", batch_size=10)

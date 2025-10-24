from pathlib import Path
import re
from utils.common_utils import *

def convert_vtt_ass(temp_video_path, vtt_path, font_name="SimHei", font_size=60,
                primary_color="&HFFFFFF&", outline_color="&H000000&", shadow=0):
    """
    自动将 VTT 转为 ASS 并嵌入视频（软字幕）
    temp_video_path: 视频文件路径
    vtt_path: VTT 字幕路径
    """
    vtt_ass = get_record(temp_video_path, platform="youtube", mode="download", done="dconvert_vtt_ass")
    if vtt_ass["done"]:
        print(f"⚠️ vtt文件已经转换为ass")
        return vtt_ass["done"]
        
    else:
        video_path = Path(temp_video_path)
        vtt_path = Path(vtt_path)

        if not video_path.exists():
            print(f"⚠️ 视频文件不存在: {video_path}")
            return False
        if not vtt_path.exists():
            print(f"⚠️ 字幕文件不存在: {vtt_path}")
            return False

        # 生成 ASS 路径
        ass_path = video_path.with_suffix(".ass")

        # 1️⃣ VTT 转 ASS
        with open(vtt_path, "r", encoding="utf-8") as f:
            lines = f.readlines()

        dialogue_lines = []
        pattern_time = re.compile(r"(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})")

        for i, line in enumerate(lines):
            match = pattern_time.match(line)
            if match:
                start = match.group(1)[:-1]  # H:MM:SS.cs
                end = match.group(2)[:-1]
                text_lines = []
                j = i + 1
                while j < len(lines) and lines[j].strip() != "":
                    text_lines.append(lines[j].strip())
                    j += 1
                text = "\\N".join(text_lines)
                dialogue_lines.append(f"Dialogue: 0,{start},{end},Default,,0,0,0,,{text}")

        ass_header = f"""[Script Info]
    ScriptType: v4.00+
    Collisions: Normal
    PlayResX: 1920
    PlayResY: 1080
    Timer: 100.0000

    [V4+ Styles]
    Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
    Style: Default,{font_name},{font_size},{primary_color},&H000000&,{outline_color},&H000000&,0,0,0,0,100,100,0,0,1,2,{shadow},2,10,10,10,1

    [Events]
    Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
    """

        with open(ass_path, "w", encoding="utf-8-sig") as f:
            f.write(ass_header)
            f.write("\n".join(dialogue_lines))

        print(f"✅ 已生成 ASS 字幕: {ass_path}")
        record_download("dconvert_vtt_ass", ass_path, temp_video_path, platform="youtube", mode="download")
        return ass_path
from pathlib import Path
import subprocess 
import os
from utils.common_utils import *

def embed_subtitle(temp_video_path, ass_path):
    
    embed_subtitle = get_record(temp_video_path, platform="youtube", mode="download", done="embed_subtitle")
    if embed_subtitle["done"]:
        print(f"⚠️ 视频字幕已经嵌入完成")
        return embed_subtitle["done"]
    else:   
        # FFmpeg 嵌入字幕
        temp_video_path = str(Path(temp_video_path).resolve())
        ass_path = str(Path(ass_path).resolve())
        ass_path_ffmpeg = ass_path.replace("\\", "/").replace(":", "\\:")
        tmp_path = str(Path(temp_video_path).parent / f"tmp_{Path(temp_video_path).name}")

        cmd = [
            "ffmpeg",
            "-y",
            "-hwaccel", "cuda",             # GPU 解码
            "-i", temp_video_path,
            "-vf", f"ass='{ass_path_ffmpeg}'",  # 字幕渲染
            "-c:v", "h264_nvenc",           # GPU 编码
            "-preset", "fast",              # 编码速度优先
            "-c:a", "copy",
            tmp_path
        ]

        print(f"▶️ 正在 GPU 嵌入字幕: {temp_video_path}")
        result = subprocess.run(cmd, text=True, capture_output=True)

        if result.returncode != 0:
            print("❌ ffmpeg 返回非零状态，嵌入失败。")
            print("----- ffmpeg stderr 输出 -----")
            print(result.stderr)
            return False

        os.replace(tmp_path, temp_video_path)
        print("✅ 字幕嵌入完成")
        record_download("embed_subtitle", temp_video_path, temp_video_path, platform="youtube", mode="download")
        return temp_video_path
from pathlib import Path
import subprocess 
import os

def embed_subtitle(video_path, ass_path):
    # FFmpeg 嵌入字幕
    video_path = str(Path(video_path).resolve())
    ass_path = str(Path(ass_path).resolve())
    ass_path_ffmpeg = ass_path.replace("\\", "/").replace(":", "\\:")
    tmp_path = str(Path(video_path).parent / f"tmp_{Path(video_path).name}")

    cmd = [
        "ffmpeg",
        "-y",
        "-hwaccel", "cuda",             # GPU 解码
        "-i", video_path,
        "-vf", f"ass='{ass_path_ffmpeg}'",  # 字幕渲染
        "-c:v", "h264_nvenc",           # GPU 编码
        "-preset", "fast",              # 编码速度优先
        "-c:a", "copy",
        tmp_path
    ]

    print(f"▶️ 正在 GPU 嵌入字幕: {video_path}")
    result = subprocess.run(cmd, text=True, capture_output=True)

    if result.returncode != 0:
        print("❌ ffmpeg 返回非零状态，嵌入失败。")
        print("----- ffmpeg stderr 输出 -----")
        print(result.stderr)
        return False

    os.replace(tmp_path, video_path)
    print("✅ 字幕嵌入完成")
    
    return video_path
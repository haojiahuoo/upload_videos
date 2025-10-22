from config import MAX_SEGMENT_DURATION
import os, subprocess, math
from download.youtube import download_root

def segment_video(full_video_path, title_cn, duration, index=1):
    # 下载完成后分段
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
        
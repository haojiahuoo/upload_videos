from config import MAX_SEGMENT_DURATION, DOWNLOAD_ROOT, UPLOAD_ROOT
import os, subprocess, math

def segment_video(full_video_path, title_cn, duration, index=1):
    """将视频分段保存为多个文件"""
    num_parts = math.ceil(duration / MAX_SEGMENT_DURATION)
    part_len = duration / num_parts
    all_parts_exist = True

    full_video_path = str(full_video_path).replace("\\", "/")

    for i in range(num_parts):
        start = round(i * part_len, 2)
        end = round(min(duration, (i + 1) * part_len), 2)
        part_name = f"({index:02}-{i+1}){title_cn}.mp4"
        part_path = os.path.join(DOWNLOAD_ROOT, part_name)
        part_path = str(part_path).replace("\\", "/")

        ffmpeg_cmd = [
            "ffmpeg",
            "-y",
            "-ss", str(start),
            "-to", str(end),
            "-i", full_video_path,
            "-c", "copy",
            part_path
        ]

        print(f"▶️ 分段第 {i + 1}/{num_parts} ({start}-{end}s): {part_path}")
        result = subprocess.run(ffmpeg_cmd, capture_output=True, text=True, encoding="utf-8", errors="ignore")
        
        # 检查生成结果
        if result.returncode != 0 or not os.path.exists(part_path) or os.path.getsize(part_path) == 0:
            all_parts_exist = False
            print(f"❌ 分段 {i+1} 生成失败: {part_path}")
        else:
            print(f"✅ 分段 {i+1} 成功: {part_path}")

    # 返回分段结果
    if all_parts_exist:
        print(f"🗑️ 所有分段成功生成，删除原视频：{full_video_path}")
        os.remove(full_video_path)
    else:
        print("⚠️ 有分段未成功生成，原视频保留。")

    return all_parts_exist

        
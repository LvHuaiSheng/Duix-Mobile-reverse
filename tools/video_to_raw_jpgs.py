#!/usr/bin/env python3
"""
从视频抽帧为 JPEG，改后缀为 .sij，保存到视频同目录的 raw_jpgs 文件夹。
使用 OpenCV 抽帧。仅支持 25fps 视频，非 25fps 会报错不提取。

用法:
    python video_to_raw_jpgs.py <video_path> [--fps FPS]

示例:
    python video_to_raw_jpgs.py /path/to/260127_muban.mp4
    python video_to_raw_jpgs.py /path/to/video.mp4 --fps 25
"""

import argparse
import sys
from pathlib import Path

import cv2

REQUIRED_FPS = 25.0


def extract_frames(video_path: Path, output_dir: Path, fps: float = None) -> int:
    """
    使用 OpenCV 抽帧为 JPEG，保存为 1.sij, 2.sij, ...
    仅支持 25fps 视频，否则报错不提取。
    fps: 抽帧帧率，None 表示按视频原帧率抽帧（每帧都保存）
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"无法打开视频: {video_path}")

    video_fps = cap.get(cv2.CAP_PROP_FPS)
    if video_fps is None or video_fps <= 0:
        cap.release()
        raise RuntimeError("无法获取视频帧率")
    if abs(video_fps - REQUIRED_FPS) > 0.01:
        cap.release()
        raise RuntimeError(
            f"视频必须是 {REQUIRED_FPS} fps，当前为 {video_fps:.2f} fps，不提取"
        )
    if fps is not None and fps > 0:
        frame_interval = video_fps / fps  # 每隔多少帧取一帧
    else:
        frame_interval = 1.0  # 每帧都取

    count = 0
    frame_index = 0
    next_save_at = 0.0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_index >= next_save_at:
            count += 1
            # 用 JPEG 编码写入 .sij 文件（内容为 JPEG，扩展名为 .sij）
            success, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            if not success:
                raise RuntimeError(f"编码第 {count} 帧失败")
            out_path = output_dir / f"{count}.sij"
            out_path.write_bytes(buf.tobytes())
            next_save_at += frame_interval

        frame_index += 1

    cap.release()
    return count


def main():
    parser = argparse.ArgumentParser(
        description="从视频抽帧为 JPEG，改后缀为 .sij，保存到视频同目录的 raw_jpgs（使用 OpenCV）"
    )
    parser.add_argument(
        "video_path",
        type=str,
        help="输入视频路径，例如 /path/to/260127_muban.mp4",
    )
    parser.add_argument(
        "--fps",
        type=float,
        default=None,
        help="抽帧帧率，不指定则按视频原帧率抽帧（每帧都保存）",
    )
    args = parser.parse_args()

    video_path = Path(args.video_path).resolve()
    if not video_path.is_file():
        print(f"错误：文件不存在 {video_path}", file=sys.stderr)
        sys.exit(1)

    output_dir = video_path.parent / "raw_jpgs"

    print(f"视频: {video_path}")
    print(f"输出目录: {output_dir}")
    if args.fps is not None:
        print(f"抽帧帧率: {args.fps} fps")

    try:
        count = extract_frames(video_path, output_dir, args.fps)
        print(f"完成：共生成 {count} 帧，已保存为 raw_jpgs/1.sij ~ {count}.sij")
    except Exception as e:
        print(f"抽帧失败: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

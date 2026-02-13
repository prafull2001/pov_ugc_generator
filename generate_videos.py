#!/usr/bin/env python3
"""
POV UGC Video Generator
-----------------------
Automatically generates multiple videos by combining:
- 1 intro clip (wake up sequence)
- Multiple meme clips (middle section - swapped out)
- 1 outro clip (screen time block sequence)
- 1 end card
- TikTok-style captions

Usage: python generate_videos.py
"""

import os
import subprocess
import sys
from pathlib import Path

# Caption options - each video gets one assigned (alternates between these two)
CAPTIONS = [
    "POV you slept late on a\nschool night",
    "POV you stay up too late\non a school night",
]


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            check=True
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_video_info(video_path):
    """Get video resolution and frame rate using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-select_streams", "v:0",
        "-show_entries", "stream=width,height,r_frame_rate",
        "-of", "csv=p=0",
        str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        parts = result.stdout.strip().split(",")
        if len(parts) >= 3:
            width, height = int(parts[0]), int(parts[1])
            fps_str = parts[2]
            if "/" in fps_str:
                num, den = fps_str.split("/")
                fps = float(num) / float(den)
            else:
                fps = float(fps_str)
            return width, height, fps
    return None, None, None


def get_video_duration(video_path):
    """Get video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return float(result.stdout.strip())
    return 0


def normalize_video(input_path, output_path, target_width, target_height, target_fps):
    """Normalize a video to target resolution and frame rate."""
    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_path),
        "-vf", f"scale={target_width}:{target_height}:force_original_aspect_ratio=decrease,pad={target_width}:{target_height}:(ow-iw)/2:(oh-ih)/2,fps={target_fps}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-c:a", "aac",
        "-b:a", "192k",
        "-ar", "44100",
        "-ac", "2",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def concatenate_videos_copy(video_paths, output_path, temp_dir):
    """Concatenate videos using stream copy (fast, for intermediate steps)."""
    list_file = temp_dir / "concat_list.txt"

    with open(list_file, "w") as f:
        for video_path in video_paths:
            escaped_path = str(video_path).replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path)
    ]

    subprocess.run(cmd, capture_output=True, check=True)


def add_caption_to_video(input_path, output_path, caption_text, video_width, video_height):
    """Add TikTok-style caption to video using FFmpeg drawtext."""
    # Escape special characters for FFmpeg drawtext
    escaped_text = caption_text.replace("'", "'\\''").replace(":", "\\:")

    # Font size
    font_size = int(video_width * 0.065)

    # Position: near top (18% from top)
    y_position = int(video_height * 0.18)

    # Split into two lines and center each separately
    lines = caption_text.split('\n')

    if len(lines) == 2:
        line1 = lines[0].replace("'", "'\\''").replace(":", "\\:")
        line2 = lines[1].replace("'", "'\\''").replace(":", "\\:")
        line_spacing = int(font_size * 1.3)

        # Two drawtext filters, one for each line, both centered
        drawtext_filter = (
            f"drawtext=text='{line1}':"
            f"fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
            f"fontsize={font_size}:"
            f"fontcolor=white:"
            f"borderw=8:"
            f"bordercolor=black:"
            f"shadowcolor=black@0.6:"
            f"shadowx=3:"
            f"shadowy=3:"
            f"x=(w-text_w)/2:"
            f"y={y_position},"
            f"drawtext=text='{line2}':"
            f"fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
            f"fontsize={font_size}:"
            f"fontcolor=white:"
            f"borderw=8:"
            f"bordercolor=black:"
            f"shadowcolor=black@0.6:"
            f"shadowx=3:"
            f"shadowy=3:"
            f"x=(w-text_w)/2:"
            f"y={y_position + line_spacing}"
        )
    else:
        drawtext_filter = (
            f"drawtext=text='{escaped_text}':"
            f"fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
            f"fontsize={font_size}:"
            f"fontcolor=white:"
            f"borderw=8:"
            f"bordercolor=black:"
            f"shadowcolor=black@0.6:"
            f"shadowx=3:"
            f"shadowy=3:"
            f"x=(w-text_w)/2:"
            f"y={y_position}"
        )

    cmd = [
        "ffmpeg",
        "-y",
        "-i", str(input_path),
        "-vf", f"{drawtext_filter},fps=30",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    Warning: Caption error - {result.stderr[:200]}")
        subprocess.run(["cp", str(input_path), str(output_path)], check=True)


def concatenate_final(video_paths, output_path, temp_dir):
    """Concatenate for final output with re-encoding."""
    list_file = temp_dir / "concat_list.txt"

    with open(list_file, "w") as f:
        for video_path in video_paths:
            escaped_path = str(video_path).replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    cmd = [
        "ffmpeg",
        "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-movflags", "+faststart",
        str(output_path)
    ]

    subprocess.run(cmd, capture_output=True, check=True)


def find_video_files(directory):
    """Find all video files in a directory."""
    video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".m4v", ".MP4", ".MOV"}
    videos = []

    if not directory.exists():
        return videos

    for file in sorted(directory.iterdir()):
        if file.suffix in video_extensions and not file.name.startswith("."):
            videos.append(file)

    return videos


def sort_by_numeric_prefix(files):
    """Sort files by numeric prefix (1_xxx, 2_xxx, etc.)."""
    import re

    def get_number(f):
        match = re.match(r'^(\d+)', f.name)
        return int(match.group(1)) if match else 999

    return sorted(files, key=get_number)


def main():
    print("=" * 50)
    print("   POV UGC Video Generator")
    print("=" * 50)
    print()

    # Check FFmpeg
    if not check_ffmpeg():
        print("ERROR: FFmpeg is not installed!")
        print()
        print("Please install FFmpeg first:")
        print("  Mac:     brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/download.html")
        print("  Linux:   sudo apt install ffmpeg")
        sys.exit(1)

    print("[OK] FFmpeg is installed")
    print()

    # Define paths
    base_dir = Path(__file__).parent
    input_dir = base_dir / "input"
    intro_dir = input_dir / "intro"
    memes_dir = input_dir / "memes"
    outro_dir = input_dir / "outro"
    endcard_dir = input_dir / "endcard"
    output_dir = base_dir / "output"
    temp_dir = base_dir / "temp"

    # Create output and temp directories
    output_dir.mkdir(exist_ok=True)
    temp_dir.mkdir(exist_ok=True)

    # Find intro video
    intro_videos = find_video_files(intro_dir)
    if not intro_videos:
        print(f"ERROR: No intro video found in {intro_dir}")
        print("Please add your wake-up clip to the 'input/intro' folder")
        sys.exit(1)
    intro_video = intro_videos[0]
    print(f"[OK] Found intro: {intro_video.name}")

    # Find outro video(s) - supports multiple clips with numeric prefixes
    outro_videos = find_video_files(outro_dir)
    if not outro_videos:
        print(f"ERROR: No outro video found in {outro_dir}")
        print("Please add your screen-time-block clip to the 'input/outro' folder")
        sys.exit(1)

    if len(outro_videos) == 1:
        outro_video = outro_videos[0]
        outro_is_multi = False
        print(f"[OK] Found outro: {outro_video.name}")
    else:
        outro_videos = sort_by_numeric_prefix(outro_videos)
        outro_is_multi = True
        print(f"[OK] Found {len(outro_videos)} outro clips (will stitch in order):")
        for v in outro_videos:
            print(f"      - {v.name}")

    # Find meme videos
    meme_videos = find_video_files(memes_dir)
    if not meme_videos:
        print(f"ERROR: No meme videos found in {memes_dir}")
        print("Please add your meme clips to the 'input/memes' folder")
        sys.exit(1)
    print(f"[OK] Found {len(meme_videos)} meme clip(s)")

    # Find endcard video (optional but expected)
    endcard_videos = find_video_files(endcard_dir)
    endcard_video = endcard_videos[0] if endcard_videos else None
    if endcard_video:
        print(f"[OK] Found endcard: {endcard_video.name}")

    print(f"[OK] Loaded {len(CAPTIONS)} caption options")
    print()

    # Force vertical video output (1080x1920 @ 30fps)
    print("Video settings...")
    width, height, fps = 1080, 1920, 30
    print(f"  Output: {width}x{height} @ {fps}fps (vertical)")
    print()

    # Normalize all clips to same format
    print("Normalizing video clips (this may take a moment)...")

    # Normalize intro
    print(f"  Processing intro...")
    normalized_intro = temp_dir / "intro_normalized.mp4"
    normalize_video(intro_video, normalized_intro, width, height, fps)

    # Normalize outro (handle single or multiple clips)
    if outro_is_multi:
        print(f"  Processing {len(outro_videos)} outro clips...")
        normalized_outro_clips = []
        for i, outro_clip in enumerate(outro_videos):
            print(f"    - {outro_clip.name}")
            norm_path = temp_dir / f"outro_{i}_normalized.mp4"
            normalize_video(outro_clip, norm_path, width, height, fps)
            normalized_outro_clips.append(norm_path)
        # Concatenate all outro clips into one
        normalized_outro = temp_dir / "outro_normalized.mp4"
        concatenate_videos_copy(normalized_outro_clips, normalized_outro, temp_dir)
    else:
        print(f"  Processing outro...")
        normalized_outro = temp_dir / "outro_normalized.mp4"
        normalize_video(outro_video, normalized_outro, width, height, fps)

    # Normalize endcard
    normalized_endcard = None
    if endcard_video:
        print(f"  Processing endcard...")
        normalized_endcard = temp_dir / "endcard_normalized.mp4"
        normalize_video(endcard_video, normalized_endcard, width, height, fps)

    # Normalize memes
    normalized_memes = []
    for i, meme in enumerate(meme_videos):
        print(f"  Processing meme {i+1}/{len(meme_videos)}: {meme.name}")
        normalized_path = temp_dir / f"meme_{i}_normalized.mp4"
        normalize_video(meme, normalized_path, width, height, fps)
        normalized_memes.append(normalized_path)

    print()
    print("Generating final videos with captions...")
    print()

    # Generate combined videos
    generated = []
    for i, meme_path in enumerate(normalized_memes):
        meme_name = meme_videos[i].stem
        output_name = f"video_{i+1}_{meme_name}.mp4"
        output_path = output_dir / output_name

        # Select caption (cycle through list)
        caption = CAPTIONS[i % len(CAPTIONS)]
        caption_preview = caption.replace('\n', ' ')[:40]
        print(f"  Creating: {output_name}")
        print(f"    Caption: \"{caption_preview}...\"")

        # Step 1: Concatenate intro + meme + outro (without endcard)
        main_content = temp_dir / f"main_content_{i}.mp4"
        concatenate_videos_copy(
            [normalized_intro, meme_path, normalized_outro],
            main_content,
            temp_dir
        )

        # Step 2: Add caption to main content
        captioned_content = temp_dir / f"captioned_{i}.mp4"
        add_caption_to_video(main_content, captioned_content, caption, width, height)

        # Step 3: Concatenate captioned content + endcard (if exists)
        if normalized_endcard:
            concatenate_final(
                [captioned_content, normalized_endcard],
                output_path,
                temp_dir
            )
        else:
            # Just copy the captioned content as final
            subprocess.run(["cp", str(captioned_content), str(output_path)], check=True)

        generated.append((output_path, caption))

    # Clean up temp files
    print()
    print("Cleaning up temporary files...")
    for temp_file in temp_dir.iterdir():
        temp_file.unlink()
    temp_dir.rmdir()

    # Summary
    print()
    print("=" * 50)
    print("   DONE!")
    print("=" * 50)
    print()
    print(f"Generated {len(generated)} video(s) in the 'output' folder:")
    for video, caption in generated:
        caption_short = caption.replace('\n', ' ')[:35]
        print(f"  - {video.name}")
        print(f"    \"{caption_short}...\"")
    print()


if __name__ == "__main__":
    main()

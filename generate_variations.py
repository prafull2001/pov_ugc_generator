#!/usr/bin/env python3
"""
POV UGC Variation Generator
---------------------------
Generates 5 unique video variations per meme for multi-account posting.
Each variation has different audio, visual treatment, and caption.

Usage: python generate_variations.py
"""

import os
import subprocess
import sys
import random
from pathlib import Path
from itertools import cycle

# Caption options - two main styles that perform best
CAPTIONS = [
    "POV you stayed up studying\nall night",
    "POV you stay up too late\non a school night",
    "POV you stayed up way too late\non a school night",
    "POV you stayed up studying\nall night again",
    "POV you stay up too late\non a school night...",
]

# Visual presets for uniqueness (brightness, saturation, speed, crop_x, crop_y, pitch_cents)
VISUAL_PRESETS = [
    {"name": "A", "brightness": 0.00, "saturation": 1.00, "speed": 1.00, "crop_x": 0, "crop_y": 0, "pitch": 0},
    {"name": "B", "brightness": 0.03, "saturation": 1.05, "speed": 1.01, "crop_x": 8, "crop_y": 0, "pitch": 15},
    {"name": "C", "brightness": -0.02, "saturation": 1.03, "speed": 0.99, "crop_x": -8, "crop_y": 0, "pitch": -10},
    {"name": "D", "brightness": 0.02, "saturation": 0.97, "speed": 1.02, "crop_x": 0, "crop_y": 8, "pitch": 20},
    {"name": "E", "brightness": -0.03, "saturation": 1.08, "speed": 0.98, "crop_x": 0, "crop_y": -8, "pitch": -15},
]

# Number of accounts/variations per meme
NUM_ACCOUNTS = 5


def check_ffmpeg():
    """Check if FFmpeg is installed."""
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False


def get_video_duration(video_path):
    """Get video duration in seconds using ffprobe."""
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration",
        "-of", "csv=p=0",
        str(video_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0 and result.stdout.strip():
        return float(result.stdout.strip())
    return 0


def find_files(directory, extensions):
    """Find all files with given extensions in a directory."""
    files = []
    if not directory.exists():
        return files
    for file in sorted(directory.iterdir()):
        if file.suffix.lower() in extensions and not file.name.startswith("."):
            files.append(file)
    return files


def find_audio_files(directory, prefix):
    """Find audio files matching a prefix (case-insensitive)."""
    audio_extensions = {".m4a", ".wav", ".mp3", ".aac"}
    files = []
    if not directory.exists():
        return files
    for file in sorted(directory.iterdir()):
        if file.suffix.lower() in audio_extensions and not file.name.startswith("."):
            if file.name.lower().startswith(prefix.lower()):
                files.append(file)
    return files


def normalize_video(input_path, output_path, width=1080, height=1920, fps=30):
    """Normalize a video to target resolution and frame rate."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps={fps}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
        "-an",  # Remove audio, we'll add our own
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def concatenate_videos(video_paths, output_path, temp_dir):
    """Concatenate videos using concat demuxer."""
    list_file = temp_dir / "concat_list.txt"
    with open(list_file, "w") as f:
        for video_path in video_paths:
            escaped_path = str(video_path).replace("'", "'\\''")
            f.write(f"file '{escaped_path}'\n")

    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def concatenate_audio(audio_paths, output_path, durations=None):
    """Concatenate audio files, trimming to match video durations if provided."""
    if len(audio_paths) == 1:
        # Just copy single audio
        subprocess.run(["cp", str(audio_paths[0]), str(output_path)], check=True)
        return

    # Build filter for concatenating audio
    inputs = []
    filter_parts = []

    for i, audio_path in enumerate(audio_paths):
        inputs.extend(["-i", str(audio_path)])
        if durations and i < len(durations):
            # Trim audio to match video duration
            filter_parts.append(f"[{i}:a]atrim=0:{durations[i]},asetpts=PTS-STARTPTS[a{i}]")
        else:
            filter_parts.append(f"[{i}:a]asetpts=PTS-STARTPTS[a{i}]")

    # Concatenate all audio streams
    concat_inputs = "".join([f"[a{i}]" for i in range(len(audio_paths))])
    filter_parts.append(f"{concat_inputs}concat=n={len(audio_paths)}:v=0:a=1[out]")

    filter_complex = ";".join(filter_parts)

    cmd = [
        "ffmpeg", "-y",
        *inputs,
        "-filter_complex", filter_complex,
        "-map", "[out]",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def apply_visual_preset(input_path, output_path, preset, width=1080, height=1920):
    """Apply visual modifications for uniqueness."""
    brightness = preset["brightness"]
    saturation = preset["saturation"]
    speed = preset["speed"]
    crop_x = preset["crop_x"]
    crop_y = preset["crop_y"]

    # Build video filter
    filters = []

    # Speed adjustment (affects both video and we'll handle audio separately)
    if speed != 1.0:
        filters.append(f"setpts={1/speed}*PTS")

    # Crop offset (crop slightly then scale back)
    if crop_x != 0 or crop_y != 0:
        crop_w = width - abs(crop_x) * 2
        crop_h = height - abs(crop_y) * 2
        offset_x = max(0, crop_x)
        offset_y = max(0, crop_y)
        filters.append(f"crop={crop_w}:{crop_h}:{offset_x}:{offset_y}")
        filters.append(f"scale={width}:{height}")

    # Brightness and saturation
    if brightness != 0 or saturation != 1.0:
        filters.append(f"eq=brightness={brightness}:saturation={saturation}")

    vf = ",".join(filters) if filters else "null"

    # Audio filter for speed and pitch
    af_parts = []
    if speed != 1.0:
        af_parts.append(f"atempo={speed}")

    pitch = preset["pitch"]
    if pitch != 0:
        # Pitch shift in cents (100 cents = 1 semitone)
        # asetrate changes pitch, aresample brings back to normal rate
        rate_mult = 2 ** (pitch / 1200)
        af_parts.append(f"asetrate=44100*{rate_mult},aresample=44100")

    af = ",".join(af_parts) if af_parts else "anull"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", vf,
        "-af", af,
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


def add_caption(input_path, output_path, caption_text, width=1080, height=1920):
    """Add TikTok-style caption to video."""
    font_size = int(width * 0.065)
    y_position = int(height * 0.18)

    lines = caption_text.split('\n')

    if len(lines) == 2:
        line1 = lines[0].replace("'", "'\\''").replace(":", "\\:")
        line2 = lines[1].replace("'", "'\\''").replace(":", "\\:")
        line_spacing = int(font_size * 1.3)

        drawtext_filter = (
            f"drawtext=text='{line1}':"
            f"fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
            f"fontsize={font_size}:fontcolor=white:"
            f"borderw=8:bordercolor=black:"
            f"shadowcolor=black@0.6:shadowx=3:shadowy=3:"
            f"x=(w-text_w)/2:y={y_position},"
            f"drawtext=text='{line2}':"
            f"fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
            f"fontsize={font_size}:fontcolor=white:"
            f"borderw=8:bordercolor=black:"
            f"shadowcolor=black@0.6:shadowx=3:shadowy=3:"
            f"x=(w-text_w)/2:y={y_position + line_spacing}"
        )
    else:
        escaped = caption_text.replace("'", "'\\''").replace(":", "\\:")
        drawtext_filter = (
            f"drawtext=text='{escaped}':"
            f"fontfile=/System/Library/Fonts/Supplemental/Arial Bold.ttf:"
            f"fontsize={font_size}:fontcolor=white:"
            f"borderw=8:bordercolor=black:"
            f"shadowcolor=black@0.6:shadowx=3:shadowy=3:"
            f"x=(w-text_w)/2:y={y_position}"
        )

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", drawtext_filter,
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        "-movflags", "+faststart",
        str(output_path)
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"    Warning: Caption error, copying without caption")
        subprocess.run(["cp", str(input_path), str(output_path)], check=True)


def merge_video_audio(video_path, audio_path, output_path):
    """Merge silent video with audio track."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-shortest",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def main():
    print("=" * 55)
    print("   POV UGC Variation Generator")
    print("   Generates 5 unique videos per meme")
    print("=" * 55)
    print()

    # Check FFmpeg
    if not check_ffmpeg():
        print("ERROR: FFmpeg is not installed!")
        sys.exit(1)
    print("[OK] FFmpeg found")

    # Define paths
    base_dir = Path(__file__).parent
    input_dir = base_dir / "input"
    audio_dir = base_dir / "audio_files"
    intro_dir = input_dir / "intro"
    memes_dir = input_dir / "memes"
    outro_dir = input_dir / "outro"
    endcard_dir = input_dir / "endcard"
    output_base = base_dir / "batch_output"
    temp_dir = base_dir / "temp_variations"

    # Create directories
    temp_dir.mkdir(exist_ok=True)
    for i in range(1, NUM_ACCOUNTS + 1):
        (output_base / f"acc{i}").mkdir(parents=True, exist_ok=True)

    # Find audio files
    intro_audios = find_audio_files(audio_dir, "intro")
    middle_audios = find_audio_files(audio_dir, "middle")
    outro_audios = find_audio_files(audio_dir, "outro")

    print(f"[OK] Found {len(intro_audios)} intro audio variants")
    print(f"[OK] Found {len(middle_audios)} middle audio variants")
    print(f"[OK] Found {len(outro_audios)} outro audio variants")

    if not intro_audios or not middle_audios or not outro_audios:
        print("ERROR: Missing audio files in audio_files/ folder")
        print("  Need: Intro audio X.m4a, Middle audio X.m4a, Outro audio X.m4a")
        sys.exit(1)

    # Find video files
    video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".m4v"}

    intro_videos = find_files(intro_dir, video_extensions)
    if not intro_videos:
        print(f"ERROR: No intro video in {intro_dir}")
        sys.exit(1)
    intro_video = intro_videos[0]
    print(f"[OK] Intro video: {intro_video.name}")

    outro_videos = sorted(find_files(outro_dir, video_extensions))
    if not outro_videos:
        print(f"ERROR: No outro videos in {outro_dir}")
        sys.exit(1)
    print(f"[OK] Found {len(outro_videos)} outro video clips")

    meme_videos = find_files(memes_dir, video_extensions)
    if not meme_videos:
        print(f"ERROR: No meme videos in {memes_dir}")
        sys.exit(1)
    print(f"[OK] Found {len(meme_videos)} meme clips")

    endcard_videos = find_files(endcard_dir, video_extensions)
    endcard_video = endcard_videos[0] if endcard_videos else None
    if endcard_video:
        print(f"[OK] Endcard: {endcard_video.name}")

    print()
    print("Normalizing base videos...")

    # Normalize intro (silent)
    normalized_intro = temp_dir / "intro_normalized.mp4"
    print("  Processing intro...")
    normalize_video(intro_video, normalized_intro)
    intro_duration = get_video_duration(normalized_intro)

    # Normalize and concatenate outro clips (silent)
    print("  Processing outro clips...")
    outro_normalized = []
    outro_durations = []
    for i, outro_clip in enumerate(outro_videos):
        norm_path = temp_dir / f"outro_{i}_norm.mp4"
        normalize_video(outro_clip, norm_path)
        outro_normalized.append(norm_path)
        outro_durations.append(get_video_duration(norm_path))

    normalized_outro = temp_dir / "outro_normalized.mp4"
    concatenate_videos(outro_normalized, normalized_outro, temp_dir)
    outro_duration = get_video_duration(normalized_outro)

    # Normalize endcard (silent)
    normalized_endcard = None
    if endcard_video:
        print("  Processing endcard...")
        normalized_endcard = temp_dir / "endcard_normalized.mp4"
        normalize_video(endcard_video, normalized_endcard)

    # Normalize memes (silent)
    print("  Processing memes...")
    normalized_memes = []
    meme_durations = []
    for i, meme in enumerate(meme_videos):
        print(f"    - {meme.name}")
        norm_path = temp_dir / f"meme_{i}_norm.mp4"
        normalize_video(meme, norm_path)
        normalized_memes.append(norm_path)
        meme_durations.append(get_video_duration(norm_path))

    print()
    print(f"Generating {NUM_ACCOUNTS} variations per meme...")
    print()

    # Track which combinations we've used to avoid repeats
    used_combinations = set()

    # Process each meme
    for meme_idx, (meme_path, meme_dur) in enumerate(zip(normalized_memes, meme_durations)):
        meme_name = meme_videos[meme_idx].stem
        print(f"[{meme_idx + 1}/{len(meme_videos)}] Processing: {meme_name}")

        # Generate 5 variations
        for acc_idx in range(NUM_ACCOUNTS):
            acc_num = acc_idx + 1
            output_path = output_base / f"acc{acc_num}" / f"{meme_name}_v{acc_num}.mp4"

            # Select unique combination
            while True:
                intro_audio_idx = random.randint(0, len(intro_audios) - 1)
                middle_audio_idx = random.randint(0, len(middle_audios) - 1)
                outro_audio_idx = random.randint(0, len(outro_audios) - 1)
                combo = (intro_audio_idx, middle_audio_idx, outro_audio_idx)
                if combo not in used_combinations or len(used_combinations) >= len(intro_audios) * len(middle_audios) * len(outro_audios):
                    used_combinations.add(combo)
                    break

            preset = VISUAL_PRESETS[acc_idx]
            caption = CAPTIONS[acc_idx % len(CAPTIONS)]

            print(f"  acc{acc_num}: audio({intro_audio_idx+1},{middle_audio_idx+1},{outro_audio_idx+1}) preset={preset['name']}")

            # Step 1: Concatenate video (intro + meme + outro + endcard)
            video_parts = [normalized_intro, meme_path, normalized_outro]
            if normalized_endcard:
                video_parts.append(normalized_endcard)

            concat_video = temp_dir / f"concat_{meme_idx}_{acc_idx}.mp4"
            concatenate_videos(video_parts, concat_video, temp_dir)

            # Step 2: Concatenate audio (intro + middle + outro)
            # Trim audio to match video durations
            audio_parts = [
                intro_audios[intro_audio_idx],
                middle_audios[middle_audio_idx],
                outro_audios[outro_audio_idx]
            ]
            durations = [intro_duration, meme_dur, outro_duration]

            concat_audio = temp_dir / f"audio_{meme_idx}_{acc_idx}.m4a"
            concatenate_audio(audio_parts, concat_audio, durations)

            # Step 3: Merge video + audio
            merged = temp_dir / f"merged_{meme_idx}_{acc_idx}.mp4"
            merge_video_audio(concat_video, concat_audio, merged)

            # Step 4: Apply visual preset
            styled = temp_dir / f"styled_{meme_idx}_{acc_idx}.mp4"
            apply_visual_preset(merged, styled, preset)

            # Step 5: Add caption
            add_caption(styled, output_path, caption)

        print()

    # Cleanup
    print("Cleaning up temporary files...")
    for temp_file in temp_dir.iterdir():
        temp_file.unlink()
    temp_dir.rmdir()

    # Summary
    print()
    print("=" * 55)
    print("   DONE!")
    print("=" * 55)
    print()
    print(f"Generated {len(meme_videos) * NUM_ACCOUNTS} total videos:")
    for i in range(1, NUM_ACCOUNTS + 1):
        acc_dir = output_base / f"acc{i}"
        count = len(list(acc_dir.glob("*.mp4")))
        print(f"  batch_output/acc{i}/ - {count} videos")
    print()
    print("Each video has unique:")
    print("  - Audio combination (intro + middle + outro)")
    print("  - Visual treatment (brightness, saturation, speed, crop)")
    print("  - Caption variation")
    print()


if __name__ == "__main__":
    main()

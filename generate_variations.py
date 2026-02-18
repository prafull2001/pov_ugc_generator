#!/usr/bin/env python3
"""
POV UGC Variation Generator
---------------------------
Generates unique POV videos with sequential numbering.
Each video uses random intro video + random audio combinations.

Usage: python generate_variations.py

Output: pov_videos/POV video 1.mp4, POV video 2.mp4, etc.
Counter persists in counter.txt between runs.
"""

import os
import subprocess
import sys
import random
from pathlib import Path

# Caption options - two main styles that perform best
CAPTIONS = [
    "POV you stayed up studying\nall night",
    "POV you stay up too late\non a school night",
    "POV you stayed up way too late\non a school night",
    "POV you stayed up studying\nall night again",
    "POV you stay up too late\non a school night...",
]

# Number of variations per meme
NUM_VARIATIONS = 1


def get_next_video_number(counter_file):
    """Get the next video number from counter file."""
    if counter_file.exists():
        try:
            return int(counter_file.read_text().strip())
        except:
            return 1
    return 1


def save_video_number(counter_file, number):
    """Save the current video number to counter file."""
    counter_file.write_text(str(number))


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


def normalize_video(input_path, output_path, width=1080, height=1920, fps=30, keep_audio=False):
    """Normalize a video to target resolution and frame rate."""
    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vf", f"scale={width}:{height}:force_original_aspect_ratio=decrease,pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,fps={fps}",
        "-c:v", "libx264",
        "-preset", "fast",
        "-crf", "23",
    ]
    if keep_audio:
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])
    else:
        cmd.append("-an")
    cmd.append(str(output_path))
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
        subprocess.run(["cp", str(audio_paths[0]), str(output_path)], check=True)
        return

    inputs = []
    filter_parts = []

    for i, audio_path in enumerate(audio_paths):
        inputs.extend(["-i", str(audio_path)])
        if durations and i < len(durations):
            filter_parts.append(f"[{i}:a]atrim=0:{durations[i]},asetpts=PTS-STARTPTS[a{i}]")
        else:
            filter_parts.append(f"[{i}:a]asetpts=PTS-STARTPTS[a{i}]")

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


def mix_meme_with_reaction(meme_video_path, reaction_audio_path, output_path, meme_volume=0.75):
    """Mix meme's original audio (at reduced volume) with reaction audio overlay."""
    meme_duration = get_video_duration(meme_video_path)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(meme_video_path),
        "-i", str(reaction_audio_path),
        "-filter_complex",
        f"[0:a]volume={meme_volume}[meme];[1:a]atrim=0:{meme_duration},asetpts=PTS-STARTPTS[react];[meme][react]amix=inputs=2:duration=shortest[out]",
        "-map", "0:v",
        "-map", "[out]",
        "-c:v", "copy",
        "-c:a", "aac",
        "-b:a", "192k",
        str(output_path)
    ]
    subprocess.run(cmd, capture_output=True, check=True)


def append_endcard(main_video_path, endcard_path, output_path, temp_dir):
    """Append endcard to the main video."""
    list_file = temp_dir / "final_concat.txt"
    with open(list_file, "w") as f:
        f.write(f"file '{str(main_video_path).replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'\n")
        f.write(f"file '{str(endcard_path).replace(chr(39), chr(39)+chr(92)+chr(39)+chr(39))}'\n")

    cmd = [
        "ffmpeg", "-y",
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


def main():
    print("=" * 55)
    print("   POV UGC Variation Generator")
    print("   Generates 5 unique videos per meme")
    print("=" * 55)
    print()

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
    output_dir = base_dir / "pov_videos"
    temp_dir = base_dir / "temp_variations"
    counter_file = base_dir / "counter.txt"

    # Create directories
    temp_dir.mkdir(exist_ok=True)
    output_dir.mkdir(exist_ok=True)

    # Get starting video number
    video_number = get_next_video_number(counter_file)
    print(f"[OK] Starting from video number: {video_number}")

    # Find audio files
    intro_audios = find_audio_files(audio_dir, "intro")
    middle_audios = find_audio_files(audio_dir, "middle")
    outro_audios = find_audio_files(audio_dir, "outro")

    print(f"[OK] Found {len(intro_audios)} intro audio variants")
    print(f"[OK] Found {len(middle_audios)} middle/reaction audio variants")
    print(f"[OK] Found {len(outro_audios)} outro audio variants")

    if not intro_audios or not middle_audios or not outro_audios:
        print("ERROR: Missing audio files in audio_files/ folder")
        sys.exit(1)

    # Find video files
    video_extensions = {".mp4", ".mov", ".avi", ".mkv", ".m4v"}

    # Multiple intro videos supported
    intro_videos = find_files(intro_dir, video_extensions)
    if not intro_videos:
        print(f"ERROR: No intro videos in {intro_dir}")
        sys.exit(1)
    print(f"[OK] Found {len(intro_videos)} intro video(s)")

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
    print("Normalizing videos...")

    # Normalize all intro videos (silent - we'll add audio)
    normalized_intros = []
    intro_durations = []
    for i, intro in enumerate(intro_videos):
        print(f"  Intro {i+1}: {intro.name}")
        norm_path = temp_dir / f"intro_{i}_norm.mp4"
        normalize_video(intro, norm_path)
        normalized_intros.append(norm_path)
        intro_durations.append(get_video_duration(norm_path))

    # Normalize and concatenate outro clips (silent)
    print("  Processing outro clips...")
    outro_normalized = []
    for i, outro_clip in enumerate(outro_videos):
        norm_path = temp_dir / f"outro_{i}_norm.mp4"
        normalize_video(outro_clip, norm_path)
        outro_normalized.append(norm_path)

    normalized_outro = temp_dir / "outro_normalized.mp4"
    concatenate_videos(outro_normalized, normalized_outro, temp_dir)
    outro_duration = get_video_duration(normalized_outro)

    # Normalize endcard (keep audio)
    normalized_endcard = None
    if endcard_video:
        print("  Processing endcard...")
        normalized_endcard = temp_dir / "endcard_normalized.mp4"
        normalize_video(endcard_video, normalized_endcard, keep_audio=True)

    # Normalize memes (keep audio for mixing)
    print("  Processing memes...")
    normalized_memes = []
    meme_durations = []
    for i, meme in enumerate(meme_videos):
        print(f"    - {meme.name}")
        norm_path = temp_dir / f"meme_{i}_norm.mp4"
        normalize_video(meme, norm_path, keep_audio=True)
        normalized_memes.append(norm_path)
        meme_durations.append(get_video_duration(norm_path))

    print()
    print(f"Generating {NUM_VARIATIONS} variations per meme...")
    print()

    # Track how many videos we generate
    videos_generated = 0

    # Process each meme
    for meme_idx, (meme_path, meme_dur) in enumerate(zip(normalized_memes, meme_durations)):
        meme_name = meme_videos[meme_idx].stem
        print(f"[{meme_idx + 1}/{len(meme_videos)}] Processing: {meme_name}")

        # Generate variations
        for var_idx in range(NUM_VARIATIONS):
            output_path = output_dir / f"POV video {video_number}.mp4"

            # Random selections
            intro_idx = random.randint(0, len(normalized_intros) - 1)
            intro_audio_idx = random.randint(0, len(intro_audios) - 1)
            middle_audio_idx = random.randint(0, len(middle_audios) - 1)
            outro_audio_idx = random.randint(0, len(outro_audios) - 1)
            caption = random.choice(CAPTIONS)

            selected_intro = normalized_intros[intro_idx]
            selected_intro_dur = intro_durations[intro_idx]

            print(f"  POV video {video_number}: intro={intro_idx+1}, audio=({intro_audio_idx+1},{middle_audio_idx+1},{outro_audio_idx+1})")

            # Step 1: Mix meme audio with reaction audio (meme at 75% volume)
            meme_with_reaction = temp_dir / f"meme_mixed_{meme_idx}_{var_idx}.mp4"
            mix_meme_with_reaction(
                meme_path,
                middle_audios[middle_audio_idx],
                meme_with_reaction,
                meme_volume=0.75
            )

            # Step 2: Concatenate video (intro + meme + outro)
            video_parts = [selected_intro, meme_with_reaction, normalized_outro]
            concat_video = temp_dir / f"concat_{meme_idx}_{var_idx}.mp4"
            concatenate_videos(video_parts, concat_video, temp_dir)

            # Step 3: Extract meme's mixed audio
            meme_audio_extracted = temp_dir / f"meme_audio_{meme_idx}_{var_idx}.m4a"
            subprocess.run([
                "ffmpeg", "-y", "-i", str(meme_with_reaction),
                "-vn", "-c:a", "aac", "-b:a", "192k",
                str(meme_audio_extracted)
            ], capture_output=True, check=True)

            # Step 4: Concatenate audio: intro_audio + meme_audio + outro_audio
            full_audio_parts = [
                intro_audios[intro_audio_idx],
                meme_audio_extracted,
                outro_audios[outro_audio_idx]
            ]
            full_durations = [selected_intro_dur, meme_dur, outro_duration]
            full_audio = temp_dir / f"full_audio_{meme_idx}_{var_idx}.m4a"
            concatenate_audio(full_audio_parts, full_audio, full_durations)

            # Step 5: Merge video + audio
            silent_concat = temp_dir / f"silent_concat_{meme_idx}_{var_idx}.mp4"
            subprocess.run([
                "ffmpeg", "-y", "-i", str(concat_video),
                "-an", "-c:v", "copy", str(silent_concat)
            ], capture_output=True, check=True)

            merged = temp_dir / f"merged_{meme_idx}_{var_idx}.mp4"
            merge_video_audio(silent_concat, full_audio, merged)

            # Step 6: Add caption
            captioned = temp_dir / f"captioned_{meme_idx}_{var_idx}.mp4"
            add_caption(merged, captioned, caption)

            # Step 7: Append endcard
            if normalized_endcard:
                append_endcard(captioned, normalized_endcard, output_path, temp_dir)
            else:
                subprocess.run(["cp", str(captioned), str(output_path)], check=True)

            video_number += 1
            videos_generated += 1

        print()

    # Save the counter for next run
    save_video_number(counter_file, video_number)

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
    print(f"Generated {videos_generated} videos in pov_videos/")
    print(f"Next run will start at: POV video {video_number}")
    print()
    print("Each video has:")
    print("  - Random intro video")
    print("  - Random audio combination (intro + reaction + outro)")
    print("  - Meme audio at 75% + reaction layered")
    print("  - Random caption")
    print("  - Endcard at the end")
    print()


if __name__ == "__main__":
    main()

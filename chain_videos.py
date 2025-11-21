#!/usr/bin/env python3
"""
Chain multiple Sora-2 segments into a longer video with better continuity.
Uses last frames as starting images, pads the head of each clip with the previous
last frame, and crossfades using the real segment durations.
"""

import argparse
import os
import subprocess
import sys
from typing import Optional

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n?? {description}...")

    # Use UTF-8 encoding for subprocess on Windows
    encoding = 'utf-8' if sys.platform == "win32" else None
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        encoding=encoding,
        errors='replace'  # Replace undecodable bytes with '?'
    )

    if result.returncode != 0:
        print(f"? Error: {description} failed")
        print(result.stderr)
        sys.exit(1)

    return result.stdout


def get_video_duration(path: str) -> float:
    """Return the duration of a video in seconds using ffprobe."""
    probe = subprocess.run(
        ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
         '-of', 'default=noprint_wrappers=1:nokey=1', path],
        capture_output=True, text=True
    )
    if probe.returncode != 0:
        print(f"? Error: Could not read duration for {path}")
        sys.exit(1)
    try:
        return float(probe.stdout.strip())
    except ValueError:
        print(f"? Error: Invalid duration returned for {path}: {probe.stdout}")
        sys.exit(1)


def get_video_fps(path: str) -> Optional[float]:
    """Return the average FPS for a video or None if unavailable."""
    probe = subprocess.run(
        ['ffprobe', '-v', 'error', '-select_streams', 'v:0',
         '-show_entries', 'stream=avg_frame_rate',
         '-of', 'default=noprint_wrappers=1:nokey=1', path],
        capture_output=True, text=True
    )
    if probe.returncode != 0:
        return None
    rate = probe.stdout.strip()
    if '/' in rate:
        num, den = rate.split('/')
        try:
            num = float(num)
            den = float(den)
            if den != 0:
                return num / den
        except ValueError:
            return None
    else:
        try:
            return float(rate)
        except ValueError:
            return None
    return None


def pad_segment_with_frame(segment_path: str, frame_path: str,
                           pad_seconds: float, fps: Optional[float]) -> None:
    """
    Prepend a short still section (previous segment's last frame) to the start
    of a segment so the next crossfade blends against identical frames. Unlike a
    pure freeze, this eases from the last frame into the first motion of the new
    segment to avoid a visible "static then jump".
    """
    if pad_seconds <= 0:
        return

    if not os.path.exists(frame_path):
        print(f"? Warning: pad frame missing ({frame_path}); skipping padding.")
        return

    # Clamp pad to segment duration to avoid zero-length outputs
    seg_duration = get_video_duration(segment_path)
    if pad_seconds >= seg_duration:
        pad_seconds = max(0, seg_duration - 0.1)
        print(f"? Pad trimmed to {pad_seconds:.2f}s to fit segment duration")
    if pad_seconds <= 0:
        return

    fps_value = fps if fps else 30
    padded_path = f"{segment_path}.padded"

    filter_complex = (
        f"[0:v]fps={fps_value},format=yuv420p,setsar=1[vpad];"
        f"[1:v]setpts=PTS-STARTPTS[vseg];"
        f"[1:a]aresample=48000,aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[aseg];"
        f"[2:a]aformat=sample_rates=48000:channel_layouts=stereo,asetpts=PTS-STARTPTS[asilence];"
        f"[vpad][vseg]concat=n=2:v=1:a=0[vout];"
        f"[asilence][aseg]concat=n=2:v=0:a=1[aout]"
    )

    cmd = (
        f'ffmpeg -y -loop 1 -t {pad_seconds} -i "{frame_path}" '
        f'-i "{segment_path}" -f lavfi -t {pad_seconds} '
        f'-i anullsrc=r=48000:cl=stereo '
        f'-filter_complex "{filter_complex}" '
        f'-map "[vout]" -map "[aout]" -c:v libx264 -crf 18 -preset fast '
        f'-c:a aac -shortest "{padded_path}"'
    )
    run_command(cmd, f"Padding {segment_path} with previous last frame ({pad_seconds}s)")
    os.replace(padded_path, segment_path)


def chain_videos(prompt, total_duration, output, segment_duration=12, crossfade_duration=1.0,
                 pad_seconds=None, size=None):
    """Create a longer video by chaining multiple segments."""

    num_segments = (total_duration + segment_duration - 1) // segment_duration
    pad_value = crossfade_duration if pad_seconds is None else pad_seconds

    print(f"?? Creating {total_duration}s video in {num_segments} segments")
    print(f"Base prompt: {prompt}")
    print(f"Output: {output}")
    print(f"Crossfade: {crossfade_duration}s")
    print(f"Start pad: {pad_value}s of previous last frame for continuity")
    print(f"? Using image-to-video chaining for smooth transitions\n")

    segment_files = []
    last_frame = None
    segment_durations = []

    continuity_hint = (
        "Continue the same shot with the identical characters, outfits, lighting, and camera direction. "
        "Do not reset the scene; keep background layout and motion consistent."
    )

    for i in range(num_segments):
        segment_num = i + 1
        segment_file = f"segment_{segment_num}.mp4"
        frame_file = f"frame_{segment_num}.jpg"

        print(f"\n{'='*60}")
        print(f"Segment {segment_num}/{num_segments}")
        print(f"{'='*60}")

        size_flag = f" -r {size}" if size else ""

        # Generate segment
        if i == 0:
            # First segment: text-to-video
            segment_prompt = prompt
            cmd = f'python video_generator.py "{segment_prompt}" -s {segment_duration}{size_flag} -o {segment_file}'
        else:
            # Subsequent segments: image-to-video using last frame
            segment_prompt = f"{prompt}. {continuity_hint}"
            cmd = f'python video_generator.py "{segment_prompt}" -s {segment_duration}{size_flag} -o {segment_file} -i {last_frame}'

        run_command(cmd, f"Generating segment {segment_num}")

        # Prepend a short still frame so the next crossfade blends into identical pixels
        if i > 0 and pad_value > 0:
            segment_fps = get_video_fps(segment_file)
            pad_segment_with_frame(segment_file, last_frame, pad_value, segment_fps)

        segment_files.append(segment_file)

        # Extract last frame for next segment (except for the last segment)
        if i < num_segments - 1:
            extract_cmd = f'python extract_last_frame.py {segment_file} -o {frame_file}'
            run_command(extract_cmd, f"Extracting last frame from segment {segment_num}")
            last_frame = frame_file

        # Track actual duration for accurate crossfade offsets
        duration = get_video_duration(segment_file)
        segment_durations.append(duration)
        print(f"   Segment duration after padding: {duration:.2f}s")

    # Combine all segments
    print(f"\n{'='*60}")
    print("Combining segments...")
    print(f"{'='*60}\n")

    if len(segment_files) == 1:
        # Single segment, just copy
        import shutil
        shutil.copy(segment_files[0], output)
        print(f"Single segment - copied to {output}")
    else:
        # Multiple segments - use crossfade for smooth transitions
        video_filter_parts = []
        audio_filter_parts = []

        min_duration = min(segment_durations)
        if crossfade_duration >= min_duration:
            new_cf = max(0.1, min_duration - 0.1)
            print(f"? Crossfade trimmed from {crossfade_duration}s to {new_cf}s to fit segment length")
            crossfade_duration = new_cf

        # Calculate cumulative offset for each transition using real durations
        cumulative_duration = segment_durations[0]
        for i in range(len(segment_files) - 1):
            # Video filter labels
            if i == 0:
                v_in_label = f"[0:v][{i+1}:v]"
                a_in_label = f"[0:a][{i+1}:a]"
            else:
                v_in_label = f"[v{i-1}{i}][{i+1}:v]"
                a_in_label = f"[a{i-1}{i}][{i+1}:a]"

            v_out_label = f"[v{i}{i+1}]" if i < len(segment_files) - 2 else "[vout]"
            a_out_label = f"[a{i}{i+1}]" if i < len(segment_files) - 2 else "[aout]"

            offset = cumulative_duration - crossfade_duration

            # Video crossfade with simple dissolve (sliding transitions looked jumpy)
            video_filter_parts.append(
                f"{v_in_label}xfade=transition=fade:duration={crossfade_duration}:offset={offset:.3f}{v_out_label}"
            )

            # Audio crossfade for smooth audio transitions
            audio_filter_parts.append(
                f"{a_in_label}acrossfade=d={crossfade_duration}:c1=tri:c2=tri{a_out_label}"
            )

            # Update cumulative duration (subtract overlap since streams overlap during crossfade)
            cumulative_duration = cumulative_duration + segment_durations[i + 1] - crossfade_duration

        # Combine video and audio filters
        filter_complex = ";".join(video_filter_parts + audio_filter_parts)

        # Build input arguments
        inputs = " ".join([f'-i "{seg}"' for seg in segment_files])

        # Full ffmpeg command with video and audio crossfades
        ffmpeg_cmd = (
            f'ffmpeg {inputs} -filter_complex "{filter_complex}" -map "[vout]" -map "[aout]" '
            f'-c:v libx264 -crf 18 -preset slow -c:a aac -b:a 192k "{output}" -y'
        )
        run_command(ffmpeg_cmd, "Combining segments with smooth transitions")

    # Cleanup temporary files
    print("\n?? Cleaning up temporary files...")
    for seg in segment_files:
        if os.path.exists(seg):
            os.remove(seg)
            print(f"  Removed {seg}")

    # Clean up frame files
    for i in range(1, num_segments):
        frame_file = f"frame_{i}.jpg"
        if os.path.exists(frame_file):
            os.remove(frame_file)
            print(f"  Removed {frame_file}")

    print(f"\n? Complete! Long video saved as: {output}")
    print(f"   Total duration: ~{total_duration} seconds")
    print(f"   Segments used: {num_segments}")
    print(f"   Transitions: {crossfade_duration}s smooth crossfade between segments")
    print(f"   Method: Image-to-video chaining with start padding and enhanced blending")


def main():
    parser = argparse.ArgumentParser(
        description='Chain multiple Sora-2 video segments to create longer videos',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Create a 24-second video (2 segments)
  python chain_videos.py "Ocean waves at sunset" --duration 24 -o ocean_long.mp4
  
  # Create a 36-second video (3 segments)
  python chain_videos.py "A bird flying through forest" -d 36 -o bird_flight.mp4
  
  # Create a 60-second video (5 segments)
  python chain_videos.py "City traffic time-lapse" -d 60 -o city_long.mp4

Note: Uses image-to-video chaining for smooth transitions between segments.
      Each segment is 12 seconds and uses the last frame of the previous segment.
Requirements: ffmpeg and extract_last_frame.py must be available.
        '''
    )

    parser.add_argument('prompt', help='Text description for the video')
    parser.add_argument('-d', '--duration', type=int, required=True,
                        help='Total desired duration in seconds')
    parser.add_argument('-o', '--output', type=str, default='chained_output.mp4',
                        help='Output filename (default: chained_output.mp4)')
    parser.add_argument('-s', '--segment-duration', type=int, default=12,
                        help='Duration of each segment in seconds (default: 12)')
    parser.add_argument('-c', '--crossfade', type=float, default=1.0,
                        help='Crossfade duration in seconds between segments (default: 1.0, recommended: 0.5-2.0)')
    parser.add_argument('--pad-start', type=float, default=None,
                        help='Seconds of previous last frame to prepend to every segment after the first '
                             '(default: match crossfade; set to 0 to disable padding)')
    parser.add_argument('--size', type=str, default=None,
                        help='Resolution for all segments (e.g., 1280x720). Defaults to video_generator internal default.')

    args = parser.parse_args()

    if args.duration <= 0:
        print("? Error: Duration must be positive")
        sys.exit(1)

    if args.segment_duration <= 0 or args.segment_duration > 12:
        print("? Error: Segment duration must be between 1 and 12 seconds")
        sys.exit(1)

    if args.crossfade < 0 or args.crossfade > args.segment_duration:
        print("? Error: Crossfade duration must be between 0 and segment duration")
        sys.exit(1)

    if args.pad_start is not None and args.pad_start < 0:
        print("? Error: pad-start must be zero or positive")
        sys.exit(1)

    # Check dependencies
    try:
        subprocess.run(['python', 'video_generator.py', '--help'],
                      capture_output=True, check=True)
    except Exception:
        print("? Error: video_generator.py not found or not working")
        sys.exit(1)

    try:
        subprocess.run(['python', 'extract_last_frame.py', '--help'],
                      capture_output=True, check=True)
    except Exception:
        print("? Error: extract_last_frame.py not found or not working")
        sys.exit(1)

    try:
        subprocess.run(['ffmpeg', '-version'],
                      capture_output=True, check=True)
    except Exception:
        print("? Error: ffmpeg not found")
        print("   Install ffmpeg: https://ffmpeg.org/download.html")
        sys.exit(1)

    pad_value = args.pad_start if args.pad_start is not None else args.crossfade

    chain_videos(args.prompt, args.duration, args.output,
                 args.segment_duration, args.crossfade, pad_value, args.size)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Chain multiple video segments using text-only generation (without image-to-video).
This is a temporary solution until image-to-video becomes available in Azure.
"""

import argparse
import subprocess
import os
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

def run_command(cmd, description):
    """Run a shell command and handle errors."""
    print(f"\n🔧 {description}...")
    
    # Use UTF-8 encoding for subprocess on Windows
    encoding = 'utf-8' if sys.platform == "win32" else None
    result = subprocess.run(
        cmd, 
        shell=True, 
        capture_output=True, 
        text=True,
        encoding=encoding,
        errors='replace'
    )
    
    if result.returncode != 0:
        print(f"❌ Error: {description} failed")
        print(result.stderr)
        sys.exit(1)
    
    return result.stdout

def chain_videos_text_only(prompt, total_duration, output, segment_duration=8):
    """Create a longer video by generating and chaining multiple text-only segments."""
    
    num_segments = (total_duration + segment_duration - 1) // segment_duration
    
    print(f"🎬 Creating {total_duration}s video in {num_segments} segments (text-only mode)")
    print(f"Base prompt: {prompt}")
    print(f"Output: {output}")
    print(f"\n⚠️  Note: Using text-only generation. Segments may not have smooth transitions.")
    print(f"    Image-to-video feature is coming soon to Azure!\n")
    
    segment_files = []
    python_cmd = sys.executable
    
    for i in range(num_segments):
        segment_num = i + 1
        segment_file = f"segment_{segment_num}.mp4"
        
        # Calculate duration for this segment (last segment might be shorter)
        remaining_duration = total_duration - (i * segment_duration)
        current_duration = min(segment_duration, remaining_duration)
        
        # Round to valid values: 4, 8, or 12
        if current_duration <= 4:
            current_duration = 4
        elif current_duration <= 8:
            current_duration = 8
        else:
            current_duration = 12
        
        print(f"\n{'='*60}")
        print(f"Segment {segment_num}/{num_segments} ({current_duration}s)")
        print(f"{'='*60}")
        
        # Generate text-to-video segment
        # Add variation to prompt for each segment to create some variety
        segment_prompt = f"{prompt}"
        if segment_num > 1:
            segment_prompt = f"{prompt}, continuation"
        
        cmd = f'"{python_cmd}" video_generator.py "{segment_prompt}" --seconds {current_duration} -o {segment_file}'
        run_command(cmd, f"Generating segment {segment_num}")
        
        segment_files.append(segment_file)
    
    # Concatenate all segments using ffmpeg
    print(f"\n{'='*60}")
    print("Concatenating segments...")
    print(f"{'='*60}")
    
    # Create a file list for ffmpeg concat
    concat_list = "concat_list.txt"
    with open(concat_list, 'w') as f:
        for segment_file in segment_files:
            f.write(f"file '{segment_file}'\n")
    
    # Use ffmpeg to concatenate
    ffmpeg_cmd = f'ffmpeg -f concat -safe 0 -i {concat_list} -c copy {output} -y'
    run_command(ffmpeg_cmd, "Concatenating videos with ffmpeg")
    
    # Cleanup temporary files
    print(f"\n🧹 Cleaning up temporary files...")
    for segment_file in segment_files:
        if os.path.exists(segment_file):
            os.remove(segment_file)
            print(f"   Deleted: {segment_file}")
    
    if os.path.exists(concat_list):
        os.remove(concat_list)
        print(f"   Deleted: {concat_list}")
    
    print(f"\n✅ Done! Final video saved to: {output}")
    print(f"   Total duration: ~{sum([8 if i < num_segments-1 else total_duration % segment_duration or segment_duration for i in range(num_segments)])}s")

def main():
    parser = argparse.ArgumentParser(
        description='Chain multiple video segments to create longer videos (text-only mode)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Create a 16-second video (2 segments of 8s each)
  python chain_videos_text_only.py "ocean waves" --duration 16 -o ocean.mp4
  
  # Create a 24-second video (3 segments of 8s each)
  python chain_videos_text_only.py "city at night" --duration 24 -o city.mp4

Note: This script uses text-only generation as image-to-video is not yet available
      in all Azure deployments. Transitions between segments may not be smooth.
        '''
    )
    
    parser.add_argument('prompt', help='Text description for the video')
    parser.add_argument('--duration', type=int, required=True,
                       help='Total video duration in seconds')
    parser.add_argument('-o', '--output', type=str, default='chained_video.mp4',
                       help='Output filename (default: chained_video.mp4)')
    parser.add_argument('--segment-duration', type=int, default=8, choices=[4, 8, 12],
                       help='Duration per segment in seconds (4, 8, or 12; default: 8)')
    
    args = parser.parse_args()
    
    chain_videos_text_only(args.prompt, args.duration, args.output, args.segment_duration)

if __name__ == "__main__":
    main()

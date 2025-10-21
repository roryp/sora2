#!/usr/bin/env python3
"""
Chain multiple 12-second video segments to create longer videos.
Automatically extracts last frames and uses them as input for continuation.
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
        errors='replace'  # Replace undecodable bytes with '?'
    )
    
    if result.returncode != 0:
        print(f"❌ Error: {description} failed")
        print(result.stderr)
        sys.exit(1)
    
    return result.stdout

def chain_videos(prompt, total_duration, output, segment_duration=12):
    """Create a longer video by chaining multiple segments."""
    
    num_segments = (total_duration + segment_duration - 1) // segment_duration
    
    print(f"🎬 Creating {total_duration}s video in {num_segments} segments")
    print(f"Base prompt: {prompt}")
    print(f"Output: {output}")
    print(f"⚠️  Note: Image-to-video not available - generating independent segments\n")
    
    segment_files = []
    
    for i in range(num_segments):
        segment_num = i + 1
        segment_file = f"segment_{segment_num}.mp4"
        
        print(f"\n{'='*60}")
        print(f"Segment {segment_num}/{num_segments}")
        print(f"{'='*60}")
        
        # Generate text-to-video segment (no image input since feature unavailable)
        if num_segments > 1:
            segment_prompt = f"{prompt} (part {segment_num})"
        else:
            segment_prompt = prompt
            
        cmd = f'python video_generator.py "{segment_prompt}" -s {segment_duration} -o {segment_file}'
        run_command(cmd, f"Generating segment {segment_num}")
        
        segment_files.append(segment_file)
    
    # Combine all segments
    print(f"\n{'='*60}")
    print("Combining segments...")
    print(f"{'='*60}\n")
    
    # Create file list for ffmpeg concat
    concat_file = "concat_list.txt"
    with open(concat_file, 'w') as f:
        for seg in segment_files:
            f.write(f"file '{seg}'\n")
    
    # Use ffmpeg to concatenate
    ffmpeg_cmd = f'ffmpeg -f concat -safe 0 -i {concat_file} -c copy {output} -y'
    run_command(ffmpeg_cmd, "Combining segments with ffmpeg")
    
    # Cleanup temporary files
    print("\n🧹 Cleaning up temporary files...")
    for seg in segment_files:
        if os.path.exists(seg):
            os.remove(seg)
            print(f"  Removed {seg}")
    
    if os.path.exists(concat_file):
        os.remove(concat_file)
        print(f"  Removed {concat_file}")
    
    print(f"\n✅ Complete! Long video saved as: {output}")
    print(f"   Total duration: ~{total_duration} seconds")
    print(f"   Segments used: {num_segments}")

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

Note: Each segment is generated independently (image-to-video feature not available).
      Segments are 12 seconds each and stitched together with ffmpeg.
Requirements: ffmpeg must be installed.
        '''
    )
    
    parser.add_argument('prompt', help='Text description for the video')
    parser.add_argument('-d', '--duration', type=int, required=True,
                        help='Total desired duration in seconds')
    parser.add_argument('-o', '--output', type=str, default='chained_output.mp4',
                        help='Output filename (default: chained_output.mp4)')
    parser.add_argument('-s', '--segment-duration', type=int, default=12,
                        help='Duration of each segment in seconds (default: 12)')
    
    args = parser.parse_args()
    
    if args.duration <= 0:
        print("❌ Error: Duration must be positive")
        sys.exit(1)
    
    if args.segment_duration <= 0 or args.segment_duration > 12:
        print("❌ Error: Segment duration must be between 1 and 12 seconds")
        sys.exit(1)
    
    # Check dependencies
    try:
        subprocess.run(['python', 'video_generator.py', '--help'], 
                      capture_output=True, check=True)
    except:
        print("❌ Error: video_generator.py not found or not working")
        sys.exit(1)
    
    try:
        subprocess.run(['ffmpeg', '-version'], 
                      capture_output=True, check=True)
    except:
        print("❌ Error: ffmpeg not found")
        print("   Install ffmpeg: https://ffmpeg.org/download.html")
        sys.exit(1)
    
    chain_videos(args.prompt, args.duration, args.output, args.segment_duration)

if __name__ == '__main__':
    main()

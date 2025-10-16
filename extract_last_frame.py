#!/usr/bin/env python3
"""
Extract the last frame from a video file.
Useful for daisy-chaining videos by using the last frame as input for the next segment.
"""

import argparse
import sys

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

try:
    import cv2
except ImportError:
    print("❌ Error: opencv-python is required for frame extraction")
    print("Install it with: pip install opencv-python")
    sys.exit(1)

def extract_last_frame(video_path, output_path):
    """Extract the last frame from a video and save it as an image."""
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"❌ Error: Could not open video file: {video_path}")
        sys.exit(1)
    
    # Get total number of frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    if total_frames == 0:
        print(f"❌ Error: Video has no frames")
        sys.exit(1)
    
    print(f"📹 Video has {total_frames} frames")
    
    # Set frame position to the last frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, total_frames - 1)
    
    # Read the last frame
    ret, frame = cap.read()
    
    if not ret:
        print(f"❌ Error: Could not read the last frame")
        sys.exit(1)
    
    # Save the frame
    success = cv2.imwrite(output_path, frame)
    
    if success:
        print(f"✅ Last frame extracted and saved to: {output_path}")
    else:
        print(f"❌ Error: Could not save frame to: {output_path}")
        sys.exit(1)
    
    # Release the video capture object
    cap.release()

def main():
    parser = argparse.ArgumentParser(
        description='Extract the last frame from a video file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python extract_last_frame.py video.mp4 -o last_frame.jpg
  python extract_last_frame.py segment1.mp4 -o frame1.jpg
  python extract_last_frame.py output.mp4 -o next_input.png
        '''
    )
    
    parser.add_argument('video', help='Input video file path')
    parser.add_argument('-o', '--output', required=True, help='Output image file path')
    
    args = parser.parse_args()
    
    extract_last_frame(args.video, args.output)

if __name__ == '__main__':
    main()

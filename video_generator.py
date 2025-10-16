import os
import sys
import argparse
import requests
import json
import time
from dotenv import load_dotenv

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except:
        pass

# Load environment variables
load_dotenv()

# Azure OpenAI configuration from environment variables
endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")
subscription_key = os.getenv("AZURE_OPENAI_API_KEY")

if not all([endpoint, deployment, subscription_key]):
    raise ValueError("Missing required environment variables. Please check your .env file.")

api_version = "preview"
path = f'openai/v1/videos'
params = f'?api-version={api_version}'
constructed_url = endpoint + path + params

# Parse command-line arguments
parser = argparse.ArgumentParser(
    description='Generate videos with Azure OpenAI Sora-2',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    epilog='''
Examples:
  # Text-to-video
  python video_generator.py "A cat playing with a ball of yarn"
  python video_generator.py "Ocean waves at sunset" --seconds 8 --output ocean.mp4
  
  # Image-to-video (animate a still image)
  python video_generator.py "Ocean waves continue" --input-image last_frame.jpg -o segment2.mp4
  
  # Video extension (daisy-chaining)
  python video_generator.py "Scene continues" -i frame.jpg -s 12 -o next_clip.mp4

Note: Maximum resolution is 720p (1280x720) and maximum duration is 12 seconds.
    '''
)
parser.add_argument('prompt', help='Text description of the video to generate')
parser.add_argument('-s', '--seconds', type=str, default='12', choices=['4', '8', '12'],
                    help='Video duration in seconds (options: 4, 8, or 12; default: 12)')
parser.add_argument('-r', '--size', type=str, default='1280x720',
                    help='Video resolution WIDTHxHEIGHT (max: 1280x720, default: 1280x720)')
parser.add_argument('-o', '--output', type=str, default='output.mp4',
                    help='Output filename (default: output.mp4)')
parser.add_argument('-i', '--input-image', type=str, default=None,
                    help='Input image file for image-to-video generation (optional)')
parser.add_argument('--frame-index', type=int, default=0,
                    help='Frame index where input image appears (default: 0 = start)')
parser.add_argument('--crop-left', type=float, default=0.0,
                    help='Crop left fraction (0.0-1.0, default: 0.0)')
parser.add_argument('--crop-top', type=float, default=0.0,
                    help='Crop top fraction (0.0-1.0, default: 0.0)')
parser.add_argument('--crop-right', type=float, default=1.0,
                    help='Crop right fraction (0.0-1.0, default: 1.0)')
parser.add_argument('--crop-bottom', type=float, default=1.0,
                    help='Crop bottom fraction (0.0-1.0, default: 1.0)')

args = parser.parse_args()

headers = {
  'Api-Key': subscription_key,
}

# Prepare request based on whether we have an input image
if args.input_image:
    # Image-to-video with multipart/form-data
    print(f"🎬 Generating video with Sora-2 (Image-to-Video mode)...")
    print(f"Input image: {args.input_image}")
    
    import json
    
    # Prepare inpaint_items
    inpaint_items = [{
        "frame_index": args.frame_index,
        "type": "image",
        "file_name": os.path.basename(args.input_image),
        "crop_bounds": {
            "left_fraction": args.crop_left,
            "top_fraction": args.crop_top,
            "right_fraction": args.crop_right,
            "bottom_fraction": args.crop_bottom
        }
    }]
    
    # Flatten the body for multipart/form-data
    data = {
        "prompt": args.prompt,
        "size": args.size,
        "seconds": args.seconds,
        "model": deployment,
        "inpaint_items": json.dumps(inpaint_items)
    }
    
    # Open the image file and prepare multipart upload
    with open(args.input_image, "rb") as image_file:
        files = [
            ("files", (os.path.basename(args.input_image), image_file, "image/jpeg"))
        ]
        
        print(f"Prompt: {data['prompt']}")
        print(f"Duration: {data['seconds']} seconds")
        print(f"Size: {data['size']}")
        print(f"Frame index: {args.frame_index}")
        print(f"Output: {args.output}\n")
        
        job_response = requests.post(constructed_url, headers=headers, data=data, files=files)
else:
    # Text-to-video with JSON
    print(f"🎬 Generating video with Sora-2 (Text-to-Video mode)...")
    
    headers['Content-Type'] = 'application/json'
    
    body = {
      "model": deployment,
      "prompt": args.prompt,
      "seconds": args.seconds,
      "size": args.size
    }
    
    print(f"Prompt: {body['prompt']}")
    print(f"Duration: {body['seconds']} seconds")
    print(f"Size: {body['size']}")
    print(f"Output: {args.output}")
    print(f"\nDEBUG - Request body: {json.dumps(body, indent=2)}\n")
    
    job_response = requests.post(constructed_url, headers=headers, json=body)


if not job_response.ok:
    print("❌ Video generation failed.")
    print(json.dumps(job_response.json(), sort_keys=True, indent=4, separators=(',', ': ')))
    exit(1)
else:
    job_data = job_response.json()
    
    # Check if we got a job ID
    if 'id' in job_data:
        job_id = job_data.get("id")
        status = job_data.get("status")
        status_url = f"{endpoint}openai/v1/videos/{job_id}?api-version={api_version}"

        print(f"⏳ Job ID: {job_id}")
        print(f"⏳ Polling status...\n")
        
        while status not in ["succeeded", "completed", "failed"]:
            time.sleep(5)
            status_response = requests.get(status_url, headers=headers)
            job_data = status_response.json()
            status = job_data.get("status")
            progress = job_data.get("progress", 0)
            print(f"Status: {status} (Progress: {progress}%)")

        if status in ["succeeded", "completed"]:
            print(f"\n✅ Video generation succeeded!")
            
            # Download the video
            video_url = f'{endpoint}openai/v1/videos/{job_id}/content?api-version={api_version}'
            
            print(f"⬇️  Downloading video...")
            video_response = requests.get(video_url, headers=headers)
            
            if video_response.ok:
                with open(args.output, "wb") as file:
                    file.write(video_response.content)
                file_size = len(video_response.content) / (1024 * 1024)  # MB
                print(f'✅ Video saved as "{args.output}" ({file_size:.2f} MB)')
                print(f'🎵 Video includes audio generated by Sora-2')
            else:
                print(f"❌ Failed to download video: {video_response.status_code}")
                exit(1)
                
        elif status == "failed":
            print("\n❌ Video generation failed.")
            error_info = job_data.get("error", {})
            if error_info:
                print(f"Error code: {error_info.get('code')}")
                print(f"Error message: {error_info.get('message')}")
            exit(1)
    else:
        print("⚠️ Unexpected response format")
        print(json.dumps(job_data, sort_keys=True, indent=4, separators=(',', ': ')))
        exit(1)

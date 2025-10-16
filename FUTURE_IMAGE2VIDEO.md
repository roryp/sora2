# Image2Video Feature

## Status: ✅ AVAILABLE NOW

The image2video feature is **now available** in the Azure OpenAI Sora-2 API through the `inpaint_items` parameter! This document describes how to use this feature.

## Available Features

### 1. Image-to-Video Generation
Generate a video starting from a still image:
```bash
python video_generator.py "Ocean waves crashing" --input-image beach.jpg -o animated_beach.mp4
```

### 2. Video Extension (Daisy-Chaining)
Create videos longer than 12 seconds by chaining segments:
```bash
# Step 1: Generate first segment
python video_generator.py "A bird flying through the forest" -o segment1.mp4

# Step 2: Extract last frame
python extract_last_frame.py segment1.mp4 -o frame1.jpg

# Step 3: Generate next segment from that frame
python video_generator.py "The bird continues flying" --input-image frame1.jpg -o segment2.mp4
```

### 3. Automated Chaining
Automatically create longer videos:
```bash
python chain_videos.py "A journey through the mountains" --duration 36 -o long_video.mp4
# This creates 3x 12-second segments and stitches them together
```

## API Implementation

The Azure API uses multipart/form-data with the `inpaint_items` parameter:

```python
# Text-to-video (JSON)
body = {
    "model": "sora-2",
    "prompt": "Your video description",
    "seconds": "12",
    "size": "1280x720"
}

# Image-to-video (multipart)
files = [
    ("files", (image_filename, image_file, "image/jpeg"))
]
data = {
    "model": "sora-2",
    "prompt": "Your video description",
    "seconds": "12",
    "size": "1280x720",
    "inpaint_items": json.dumps([{
        "frame_index": 0,
        "type": "image",
        "file_name": image_filename,
        "crop_bounds": {
            "left_fraction": 0.0,
            "top_fraction": 0.0,
            "right_fraction": 1.0,
            "bottom_fraction": 1.0
        }
    }])
}
```

## Parameters

### `--input-image`
Path to the input image file (JPEG or PNG).

### `--frame-index`
Where the image appears in the video (default: 0 = start).

### `--crop-*` (left, top, right, bottom)
Crop bounds as fractions (0.0-1.0) defining image position:
- `0.0, 0.0, 1.0, 1.0` = full frame (default)
- `0.1, 0.1, 0.9, 0.9` = 80% centered crop

## Technical Requirements

Now installed and working:
- **opencv-python** for frame extraction ✅
- **ffmpeg** for video concatenation ✅

## Utilities

### extract_last_frame.py
Extract the final frame from a video for chaining:
```bash
python extract_last_frame.py video.mp4 -o last_frame.jpg
```

### chain_videos.py
Automatically generate and stitch multiple segments:
```bash
python chain_videos.py "prompt" --duration 36 -o output.mp4
```

## References

- [Azure OpenAI Video Generation Quickstart](https://learn.microsoft.com/en-us/azure/ai-foundry/openai/video-generation-quickstart)
- See `README.md` for complete usage examples

---

**Status**: ✅ Implemented and Ready to Use  
**Last Updated**: January 2025


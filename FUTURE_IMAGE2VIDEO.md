# Image2Video Feature (Coming Soon)

## Status: Not Yet Available in Azure

The image2video feature is currently **coming soon** to Azure AI Foundry Sora-2 API. This document describes the planned functionality once it becomes available.

## Planned Features

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

# Step 4: Combine segments
python combine_videos.py segment1.mp4 segment2.mp4 -o full_video.mp4
```

### 3. Automated Chaining
Automatically create longer videos:
```bash
python chain_videos.py "A journey through the mountains" --total-duration 36 -o long_video.mp4
# This would create 3x 12-second segments and stitch them together
```

## Expected API Parameters

Based on OpenAI's Sora implementation, the Azure API will likely support:

```python
body = {
  "model": "sora-2",
  "prompt": "Your video description",
  "seconds": "12",
  "size": "1280x720",
  "image": "base64_encoded_image_or_url"  # New parameter
}
```

## Technical Requirements

When this feature launches, you'll need:
- **ffmpeg** or **opencv-python** for frame extraction
- **moviepy** or **ffmpeg** for video concatenation

Install future dependencies:
```bash
pip install opencv-python moviepy
```

## Monitoring Updates

To stay informed about when this feature becomes available:
1. Check [Azure AI Foundry Playground](https://ai.azure.com/) regularly
2. Monitor [Azure OpenAI Updates](https://learn.microsoft.com/en-us/azure/ai-services/openai/whats-new)
3. Watch this repository for updates

## Contributing

Once image2video becomes available, contributions are welcome for:
- Frame extraction utilities
- Video chaining automation
- Seamless transition algorithms
- Quality optimization for stitched videos

---

**Last Updated**: October 16, 2025  
**Status**: Waiting for Azure feature release

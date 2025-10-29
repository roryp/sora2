# Azure OpenAI Sora-2 Video Generator

Generate videos with audio using Azure OpenAI's Sora-2 model. Text-to-video, image-to-video, and chain segments for longer videos with smooth crossfade transitions.

## Model Information

**Model:** Azure OpenAI Sora-2  
**Provider:** Microsoft Azure OpenAI Service  
**Capabilities:** Text-to-video and image-to-video generation with audio  
**Access:** Requires Azure OpenAI API key and endpoint

## Quick Start

```bash
# Install
pip install -r requirements.txt

# Configure .env
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key
AZURE_OPENAI_DEPLOYMENT=sora-2

# Generate
python video_generator.py "A cat playing with yarn"                    # 12s video
python video_generator.py "Ocean sunset" -s 4 -o ocean.mp4            # 4s video
python video_generator.py "Scene animates" -i photo.jpg -o anim.mp4   # Image-to-video
python chain_videos.py "Mountain journey" -d 36 -o long.mp4           # 36s chained video
```

## Usage

### video_generator.py
```bash
python video_generator.py "PROMPT" [OPTIONS]

Options:
  -s, --seconds 4|8|12     Duration (default: 12)
  -r, --size WxH           Resolution (default: 1280x720, max: 1920x1080)
  -o, --output FILE        Output filename (default: output.mp4)
  -i, --input-image FILE   Input image for image-to-video
```

### chain_videos.py
```bash
python chain_videos.py "PROMPT" -d SECONDS [OPTIONS]

Options:
  -d, --duration SECONDS      Total duration (required)
  -s, --segment-duration N    Seconds per segment (default: 12)
  -c, --crossfade SECONDS     Crossfade duration (default: 1.0, range: 0.5-2.0)
  -o, --output FILE           Output filename
  --size WxH                  Resolution
```

**Examples:**
```bash
# 24-second video with 1-second crossfade
python chain_videos.py "Train through mountains" -d 24 -o train.mp4

# Extra smooth 2-second crossfade for slow scenes
python chain_videos.py "Sunset timelapse" -d 60 --crossfade 2.0 -o sunset.mp4

# Quick 0.5-second crossfade for action
python chain_videos.py "Car chase" -d 36 --crossfade 0.5 -o chase.mp4
```

### extract_last_frame.py
```bash
python extract_last_frame.py VIDEO.mp4 -o FRAME.jpg
```

## Setup

1. **Install dependencies:** `pip install -r requirements.txt` (requires OpenAI Python SDK 2.0+)
2. **Install ffmpeg** (for chaining): `winget install ffmpeg` (Windows) or `brew install ffmpeg` (macOS)
3. **Configure `.env`:** Copy `.env.example` to `.env` and add your Azure credentials

## Features

- 🎬 **Text-to-video**: Generate from prompts (max 12s per generation)
- 🖼️ **Image-to-video**: Animate still images
- 🔗 **Video chaining**: Create videos >12s with smooth crossfade transitions
- 🎵 **Audio**: Automatically generated
- ⚙️ **Configurable**: Duration (4/8/12s), resolution (up to 1080p), crossfade (0.5-2.0s)

## API Details

- **Client**: OpenAI Python SDK v2.0+ with Azure endpoint
- **Endpoint**: `/openai/v1/` (OpenAI v1 API format)
- **Authentication**: API Key header
- **Max Duration**: 12 seconds per generation
- **Max Resolution**: 1920x1080
- **Supported Formats**: JPEG, PNG, WebP (input images)

## Content Moderation

Azure content filters may block certain prompts even with minimal settings:

❌ **Avoid:** Children/minors in activities ("girl swimming")  
✅ **Use:** Animals, nature, objects ("dog swimming", "ocean waves")

If blocked, reformulate without specific people or sensitive contexts.

## Troubleshooting

- **ModuleNotFoundError**: `pip install -r requirements.txt`
- **API Key error**: Check `.env` file
- **Moderation blocked**: Use neutral prompts (animals, nature, scenery)
- **ffmpeg not found**: Install ffmpeg for video chaining

## Notes

- Video generation: 1-3 minutes per 12-second segment
- Crossfade transitions create smooth segment blending (1.0s default)
- Some motion discontinuity may remain depending on scene complexity
- Never commit `.env` file (already in `.gitignore`)

## License

MIT

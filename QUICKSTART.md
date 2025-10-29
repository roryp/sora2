# Quick Start Guide

## Prerequisites
```bash
pip install -r requirements.txt
```

## Basic Usage

### 1. Text-to-Video (Simple)
```bash
python video_generator.py "A serene lake at sunset"
```
Output: `output.mp4` (12 seconds, 1280x720)

### 2. Text-to-Video (Custom)
```bash
python video_generator.py "Ocean waves" -s 8 --size 1920x1080 -o ocean.mp4
```
Output: `ocean.mp4` (8 seconds, 1920x1080)

### 3. Image-to-Video
```bash
python video_generator.py "The scene comes alive" -i photo.jpg -o animated.mp4
```
Output: `animated.mp4` (12 seconds from your image)

### 4. Long Videos (Chaining)
```bash
python chain_videos.py "A journey through mountains" -d 36 -o journey.mp4
```
Output: `journey.mp4` (36 seconds with smooth transitions)

## Tips

- **Prompt Quality**: Be specific and descriptive
- **Duration**: 4, 8, or 12 seconds per segment
- **Resolution**: Max 1920x1080 (1080p)
- **Chaining**: Automatically handles transitions
- **Moderation**: Some content may be blocked by safety filters (see below)

### Content Moderation Notes

Azure's content safety may block prompts even with minimal filter settings:
- ❌ Avoid: Children/minors in activities (e.g., "girl swimming")
- ✅ Use: Animals, nature, objects (e.g., "dog swimming", "ocean waves")
- ✅ Use: General scenes without specific people (e.g., "forest landscape")
- If blocked, try reformulating without specific people or sensitive contexts

## Common Commands

```bash
# Quick 4-second test
python video_generator.py "test scene" -s 4 -o test.mp4

# High quality 12-second video
python video_generator.py "detailed prompt here" -s 12 --size 1920x1080 -o output.mp4

# Create 1-minute video
python chain_videos.py "your story" -d 60 -o video.mp4

# Extract frame for continuation
python extract_last_frame.py video.mp4 -o last_frame.jpg
python video_generator.py "continuation" -i last_frame.jpg -o next.mp4
```

## Environment Setup

Create `.env` file:
```bash
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=sora-2
```

## Troubleshooting

- **"ModuleNotFoundError"**: Run `pip install -r requirements.txt`
- **"API Key not found"**: Check your `.env` file
- **"Moderation blocked"**: Avoid prompts with children/minors; use animals, nature, or general scenes instead
- **"ffmpeg not found"**: Install ffmpeg for chaining (`winget install ffmpeg` on Windows)

See [README.md](README.md) for detailed documentation.

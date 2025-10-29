# Azure OpenAI Sora-2 Video Generator

Generate videos with audio using Azure OpenAI's Sora-2 model via Python.

## Features

- 🎬 Generate videos from text prompts
- 🖼️ **NEW:** Animate still images (image-to-video)
- 🔗 **NEW:** Chain multiple segments for videos longer than 12 seconds
- 🎵 Automatic audio generation
- ⚙️ Configurable duration and resolution
- 🔒 Secure credential management via environment variables

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/roryp/sora2.git
   cd sora2
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```
   
   **Important:** You need OpenAI Python client 2.0+ for Sora video generation support.
   
   **For video chaining, also install ffmpeg:**
   - Windows: Download from [ffmpeg.org](https://ffmpeg.org/download.html) or use `winget install ffmpeg`
   - Linux: `sudo apt install ffmpeg`
   - macOS: `brew install ffmpeg`

3. **Configure environment variables**
   
   Copy `.env.example` to `.env` and fill in your Azure OpenAI credentials:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your values:
   ```
   AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
   AZURE_OPENAI_API_KEY=your-api-key-here
   AZURE_OPENAI_DEPLOYMENT=sora-2
   ```

## Usage

### Basic Usage

Generate a video with a simple prompt:
```bash
python video_generator.py "A cat playing with a ball of yarn"
```

### Command-Line Arguments

- **`prompt`** (required): Text description of the video to generate
- **`-s, --seconds`**: Video duration in seconds (options: 4, 8, or 12; default: 12)
- **`-r, --size`**: Video resolution WIDTHxHEIGHT (max: 1280x720, default: 1280x720)
- **`-o, --output`**: Output filename (default: output.mp4)
- **`-i, --input-image`**: Input image file for image-to-video generation (optional)
- **`--frame-index`**: Frame index where input image appears (default: 0)
- **`--crop-*`**: Crop bounds for input image (left, top, right, bottom fractions 0.0-1.0)

### Examples

**Basic text-to-video:**
```bash
python video_generator.py "A golden retriever puppy playing in a park"
```

**Custom duration and output:**
```bash
python video_generator.py "Ocean waves at sunset" --seconds 10 -o ocean.mp4
```

**Image-to-video (animate a still image):**
```bash
python video_generator.py "The scene comes to life" --input-image photo.jpg -o animated.mp4
```

**Video extension (daisy-chaining):**
```bash
# Generate first segment
python video_generator.py "Ocean waves" -o segment1.mp4

# Extract last frame
python extract_last_frame.py segment1.mp4 -o frame1.jpg

# Generate continuation from that frame
python video_generator.py "Ocean waves continue" -i frame1.jpg -o segment2.mp4
```

**Automatic chaining for long videos:**
```bash
# Create a 36-second video (3 segments of 12 seconds each)
python chain_videos.py "A bird flying through a forest" --duration 36 -o bird_long.mp4
```

## Advanced Features

### Image-to-Video

You can use a still image as the starting point for video generation. This is useful for:
- Animating photos or artwork
- Creating video continuations (daisy-chaining)
- Starting from a specific visual state

**How it works:**
- The input image is positioned at the specified `frame_index` (default: 0 = start of video)
- `crop_bounds` define which portion of the video frame the image occupies (fractions from 0.0 to 1.0)
- The AI generates motion based on your text prompt, continuing from the input image

**Crop Bounds Format:**
```
--crop-left 0.0 --crop-top 0.0 --crop-right 1.0 --crop-bottom 1.0  # Full frame (default)
--crop-left 0.1 --crop-top 0.1 --crop-right 0.9 --crop-bottom 0.9  # 80% centered
```

**Example workflow:**
```bash
# 1. Start with a photo
python video_generator.py "The lake ripples gently" -i lake.jpg -o lake_video.mp4

# 2. Extract the last frame to continue the scene
python extract_last_frame.py lake_video.mp4 -o lake_end.jpg

# 3. Generate a continuation
python video_generator.py "The sun sets over the water" -i lake_end.jpg -o lake_sunset.mp4
```

### Video Chaining (Breaking the 12-Second Limit)

The Azure Sora-2 API has a 12-second maximum per generation. To create longer videos, use the automatic chaining script:

**How it works:**
1. First segment: generates from your text prompt (12 seconds)
2. Extracts the last frame from that segment
3. Second segment: uses image-to-video with that frame + your prompt (12 seconds)
4. Repeats for as many segments as needed
5. Concatenates all segments into one video using ffmpeg

This creates much smoother transitions compared to generating independent segments!

**Usage:**
```bash
python chain_videos.py "PROMPT" --duration SECONDS [OPTIONS]

Options:
  --duration SECONDS    Total video duration (required)
  --segment-duration    Seconds per segment (default: 12)
  -o, --output         Output filename (default: chained_video.mp4)
  --size               Resolution WIDTHxHEIGHT (default: 1280x720)
  --keep-temp          Keep temporary segment files
```

**Examples:**
```bash
# 24-second video (2 segments)
python chain_videos.py "A train journey through mountains" --duration 24 -o train.mp4

# 60-second video with custom resolution
python chain_videos.py "Time-lapse of city at night" --duration 60 --size 1280x720 -o city.mp4
```

**Notes:**
- Each segment uses the last frame of the previous segment for continuity
- There may be slight visual transitions between segments
- Longer videos take proportionally longer to generate (12s per segment)
- ffmpeg is required for concatenation

### Help

Get all available options:
```bash
python video_generator.py --help
```

## API Details

This project uses the Azure OpenAI Sora-2 API with the OpenAI Python client:
- **Client**: OpenAI Python SDK v2.0+
- **Endpoint**: `/openai/v1/` (OpenAI v1 API format)
- **Authentication**: API Key via header
- **Max Resolution**: 1920x1080 (1080p)
- **Max Duration**: 12 seconds per generation (supported values: "4", "8", or "12" as strings)
- **Input Modes**:
  - **Text-to-video**: Generate from text prompt using `client.videos.create()`
  - **Image-to-video**: ✅ **NOW AVAILABLE** - Animate from still image using `input_reference` parameter
- **Supported Image Formats**: JPEG, PNG, WebP
- **Video Chaining**: ✅ **NOW AVAILABLE** - Combine multiple 12-second segments using image-to-video for smooth transitions

The API automatically generates audio for the videos based on the prompt.

**Note:** Sora 2 uses the OpenAI v1 API format, which is compatible with the standard OpenAI Python client when configured with Azure endpoints.


## Output

The generated video will:
- Be saved as `output.mp4` (or your specified filename)
- Include both video and audio
- Be in MP4 format at 720p resolution
- Match your specified duration (up to 12 seconds)

## Notes

- Video generation typically takes 1-3 minutes depending on duration
- The API includes content moderation; some prompts may be blocked
- Ensure your Azure OpenAI resource has Sora-2 deployment enabled
- Maximum resolution is 1920x1080 (1080p)
- Maximum duration is 12 seconds per generation
- **Image-to-video** feature is now fully supported!
  - ✅ Animate still images into videos
  - ✅ Extend videos beyond 12 seconds using chaining
  - ✅ Create smooth transitions between segments

### Content Moderation

Azure OpenAI includes content safety filters that may block certain prompts even with minimal filter settings configured in your deployment. The moderation system operates at the API level and includes safeguards beyond deployment configuration.

**Common blocking scenarios:**
- Prompts involving children or minors in certain contexts (e.g., "girl swimming")
- Combinations of people + activities that could be sensitive
- Content that could be interpreted as unsafe or inappropriate

**Best practices:**
- Test prompts with simple, non-controversial subjects first
- If a prompt is blocked, try reformulating without specific people (e.g., "A dog swimming" instead of "A girl and dog swimming")
- Use descriptive, neutral language focused on scenery, animals, or general activities
- Contact Azure support if you need access to less restrictive content filtering for legitimate use cases

**Successful prompt examples:**
- ✅ "A dog playing in water"
- ✅ "Ocean waves at sunset"
- ✅ "A bird flying through a forest"
- ❌ "A girl swimming in a lake" (may be blocked)

## Future Features

Potential upcoming enhancements:
- � Video-to-video transformations
- �️ Advanced inpainting and frame interpolation
- � Style transfer and video effects
- ⏱️ Longer native generation (beyond 12 seconds)

## Security

⚠️ **Never commit your `.env` file!** 

The `.env` file is included in `.gitignore` to prevent accidental credential exposure.

## License

MIT

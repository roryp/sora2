# Azure OpenAI Sora-2 Video Generator

Generate videos with audio using Azure OpenAI's Sora-2 model via Python.

## Features

- 🎬 Generate videos from text prompts
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
- **`-s, --seconds`**: Video duration in seconds (max: 12, default: 12)
- **`-r, --size`**: Video resolution WIDTHxHEIGHT (max: 1280x720, default: 1280x720)
- **`-o, --output`**: Output filename (default: output.mp4)

### Examples

Generate a basic video with default settings (720p, 12 seconds):
```bash
python video_generator.py "A golden retriever puppy playing in a park"
```

Generate a video with custom output filename:
```bash
python video_generator.py "Ocean waves at sunset" -o ocean.mp4
```

Generate a video with shorter duration:
```bash
python video_generator.py "City traffic time-lapse" --seconds 8 --output city.mp4
```

### Help

Get all available options:
```bash
python video_generator.py --help
```

## API Details

This project uses the Azure OpenAI Sora-2 API (Preview):
- **Endpoint**: `/openai/v1/videos`
- **API Version**: `preview`
- **Authentication**: API Key via header
- **Max Resolution**: 1280x720 (720p)
- **Max Duration**: 12 seconds

The API automatically generates audio for the videos based on the prompt.

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
- This is a **preview API** with limited documentation
- Maximum resolution is 720p (1280x720)
- Maximum duration is 12 seconds

## Security

⚠️ **Never commit your `.env` file!** 

The `.env` file is included in `.gitignore` to prevent accidental credential exposure.

## License

MIT

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

### Advanced Usage

Customize duration, resolution, and output filename:
```bash
python video_generator.py "Sunset over ocean" --seconds 16 --size 1920x1080 --output sunset.mp4
```

### Command-Line Arguments

- **`prompt`** (required): Text description of the video to generate
- **`-s, --seconds`**: Video duration in seconds (default: 12)
- **`-r, --size`**: Video resolution WIDTHxHEIGHT (default: 1280x720)
- **`-o, --output`**: Output filename (default: output.mp4)

### Examples

```bash
# Basic generation with defaults
python video_generator.py "A dog running in a park"

# Specify duration
python video_generator.py "Time-lapse of clouds" --seconds 8

# Custom resolution and output file
python video_generator.py "Flying drone footage" -s 16 -r 1920x1080 -o drone.mp4

# Short form arguments
python video_generator.py "Dancing robot" -s 10 -r 1280x720 -o robot.mp4
```

### Help

Get all available options:
```bash
python video_generator.py --help
```

## API Details

This project uses the Azure OpenAI Sora-2 API endpoint:
- **Endpoint**: `/openai/v1/videos`
- **API Version**: `preview`
- **Authentication**: API Key via header

The API automatically generates audio for the videos based on the prompt.

## Output

The generated video will:
- Be saved as `output.mp4` (or your specified filename)
- Include both video and audio
- Match your specified duration and resolution

## Notes

- Video generation typically takes 1-3 minutes depending on duration
- The API includes content moderation; some prompts may be blocked
- Ensure your Azure OpenAI resource has Sora-2 deployment enabled

## Security

⚠️ **Never commit your `.env` file!** 

The `.env` file is included in `.gitignore` to prevent accidental credential exposure.

## License

MIT

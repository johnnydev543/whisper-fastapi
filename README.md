# Whisper FastAPI STT Service

A FastAPI service for speech-to-text transcription with hardware acceleration support (Hailo-8, OpenVINO, DirectML, CPU).

## Features

- Asynchronous task queue with single worker
- Hardware fallback: Hailo-8 > OpenVINO > DirectML > CPU
- Audio normalization with ffmpeg
- VAD-based audio slicing (Silero VAD)
- Language detection
- SRT subtitle output
- Temperature monitoring and throttling
- Auto cleanup of temp files

## Installation

### System Requirements
- Python 3.11+ (Python 3.14 may not be supported by HailoRT yet)
- FFmpeg
- Hailo-8/Hailo-8L (optional, for acceleration)

### Dependencies Installation

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install FFmpeg:
   ```bash
   # Ubuntu/Debian
   sudo apt install ffmpeg

   # macOS
   brew install ffmpeg

   # Windows
   # Download from https://ffmpeg.org/download.html
   ```

### Hailo Installation (for Raspberry Pi 5)

1. Install HailoRT system packages:
   ```bash
   sudo apt update
   sudo apt install hailo-all
   ```

2. Install PyHailoRT wheel:
   - Go to https://hailo.ai/developer-zone/software-downloads/
   - Download "HailoRT – Python package (whl)" for Python 3.11, aarch64
   - File name: `hailort-4.21.0-cp311-cp311-linux_aarch64.whl`
   - Install: `pip install hailort-4.21.0-cp311-cp311-linux_aarch64.whl`

3. Install hailo-apps-infra for model management:
   ```bash
   git clone https://github.com/hailo-ai/hailo-apps-infra.git
   cd hailo-apps-infra
   sudo ./scripts/cleanup_installation.sh
   sudo ./install.sh
   ```

### Hailo Installation (for x86 Ubuntu)

1. Download and install HailoRT from developer zone
2. Install PyHailoRT wheel for x86_64
3. Install hailo-apps-infra as above

### Version Detection

Run the detection script to check your setup:
```bash
python detect_hailo.py
```

## Usage

Run the server:
```bash
python main.py
```

Or with uvicorn:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000
```

## API Endpoints

### POST /transcribe
Upload audio file for transcription.

Parameters:
- `file`: Audio file (wav, flac, mp3, m4a, ogg)
- `model`: Model size (tiny, base, small) - optional
- `language`: Language code - optional
- `output_format`: json or srt - optional

Returns: `{"task_id": "uuid"}`

### GET /task/{task_id}
Get task status and result.

Returns:
```json
{
  "task_id": "uuid",
  "status": "pending|processing|completed|failed",
  "result": {...},
  "error": "string"
}
```

### GET /health
Get system health.

Returns:
```json
{
  "hardware_engine": "cpu|hailo|openvino|directml",
  "cpu_temperature": 45.0,
  "hailo_temperature": null,
  "queue_length": 0
}
```

## Supported Audio Formats

- WAV
- FLAC
- MP3
- M4A
- OGG

Unsupported formats will return HTTP 400.

## Hardware Requirements

- Raspberry Pi 5 (optimized)
- Hailo-8/Hailo-8L (optional)
- Intel CPU with OpenVINO (optional)
- AMD GPU with DirectML (optional)

## Temperature Protection

- CPU > 80°C: Reject new tasks
- Hailo > 75°C: Reject new tasks

## Cleanup

Temp files are deleted after task completion or 10 minutes timeout.
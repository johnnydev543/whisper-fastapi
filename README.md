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

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. For Hailo support, install HailoRT and hailo-apps-infra.

3. Ensure ffmpeg is installed.

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
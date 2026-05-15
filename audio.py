import os
import tempfile
import subprocess
import numpy as np
import torch
import whisper
import logging

try:
    from silero_vad import load_silero_vad, read_audio, get_speech_timestamps
    VAD_AVAILABLE = True
except ImportError:
    VAD_AVAILABLE = False
    logger = logging.getLogger(__name__)
    logger.warning("silero_vad not available, using simple audio slicing")

logger = logging.getLogger(__name__)

class AudioProcessor:
    def __init__(self):
        if VAD_AVAILABLE:
            self.vad_model = load_silero_vad(onnx=False)
        else:
            self.vad_model = None

    def normalize_audio(self, input_path: str, output_path: str):
        """
        Normalize audio to 16kHz mono PCM using ffmpeg.
        """
        cmd = [
            "ffmpeg", "-i", input_path,
            "-ar", "16000", "-ac", "1", "-f", "wav",
            "-y", output_path
        ]
        subprocess.run(cmd, check=True, capture_output=True)

    def slice_audio_with_vad(self, audio_path: str, max_chunk_length: int = 30) -> list:
        """
        Slice audio into chunks using VAD, each <= max_chunk_length seconds.
        Returns list of (start_time, end_time, audio_array) tuples.
        """
        if VAD_AVAILABLE:
            wav = read_audio(audio_path, sampling_rate=16000)
            speech_timestamps = get_speech_timestamps(
                wav, self.vad_model, sampling_rate=16000,
                threshold=0.5, min_speech_duration_ms=250,
                max_speech_duration_s=max_chunk_length
            )

            chunks = []
            for ts in speech_timestamps:
                start = ts['start'] / 16000  # to seconds
                end = ts['end'] / 16000
                audio_chunk = wav[int(ts['start']):int(ts['end'])]
                chunks.append((start, end, audio_chunk))
        else:
            # Simple slicing: split into fixed chunks
            wav = self.load_audio(audio_path)
            sample_rate = 16000
            chunk_samples = max_chunk_length * sample_rate
            chunks = []
            for i in range(0, len(wav), chunk_samples):
                start_time = i / sample_rate
                end_time = min((i + chunk_samples) / sample_rate, len(wav) / sample_rate)
                chunk = wav[i:i + chunk_samples]
                if len(chunk) > 0:
                    chunks.append((start_time, end_time, chunk))

        return chunks

    def load_audio(self, path: str) -> np.ndarray:
        """
        Load audio using Whisper's method.
        """
        return whisper.load_audio(path)

    def detect_language(self, model, audio: np.ndarray) -> str:
        """
        Detect language from first 30 seconds of audio.
        """
        # Use Whisper's language detection
        audio_segment = audio[:30 * 16000]  # first 30s
        mel = whisper.log_mel_spectrogram(audio_segment).to(model.device)
        _, probs = model.detect_language(mel)
        return max(probs, key=probs.get)
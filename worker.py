import asyncio
import logging
import os
import time
from typing import Dict, Any
from dataclasses import dataclass
from audio import AudioProcessor
from hardware import HardwareManager
from models import TaskStatus

logger = logging.getLogger(__name__)

@dataclass
class Task:
    task_id: str
    audio_path: str
    model_name: str
    language: str = None
    output_format: str = "json"

class Worker:
    def __init__(self, hardware_manager: HardwareManager, audio_processor: AudioProcessor):
        self.hardware_manager = hardware_manager
        self.audio_processor = audio_processor
        self.queue = asyncio.Queue()
        self.tasks: Dict[str, Dict[str, Any]] = {}
        self.running = True

    async def start(self):
        """
        Start the worker loop.
        """
        logger.info("Starting worker")
        while self.running:
            try:
                task = await asyncio.wait_for(self.queue.get(), timeout=1.0)
                await self.process_task(task)
                self.queue.task_done()
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker error: {e}")

    def stop(self):
        self.running = False

    async def add_task(self, task: Task) -> str:
        """
        Add task to queue and return task_id.
        """
        self.tasks[task.task_id] = {
            "status": TaskStatus.PENDING,
            "result": None,
            "error": None,
            "created_at": time.time()
        }
        await self.queue.put(task)
        return task.task_id

    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        return self.tasks.get(task_id, {"status": TaskStatus.FAILED, "error": "Task not found"})

    async def process_task(self, task: Task):
        """
        Process a transcription task.
        """
        self.tasks[task.task_id]["status"] = TaskStatus.PROCESSING

        try:
            # Normalize audio
            normalized_path = task.audio_path.replace('.wav', '_norm.wav')
            self.audio_processor.normalize_audio(task.audio_path, normalized_path)

            # Load audio
            audio = self.audio_processor.load_audio(normalized_path)

            # Detect language if not provided
            model = self.hardware_manager.get_model()
            if not task.language:
                try:
                    task.language = self.audio_processor.detect_language(model, audio)
                except:
                    task.language = "en"  # default

            # Slice audio with VAD
            chunks = self.audio_processor.slice_audio_with_vad(normalized_path)

            # Transcribe each chunk
            transcriptions = []
            current_time = 0.0

            for start, end, chunk in chunks:
                # Transcribe chunk
                try:
                    result = model.transcribe(chunk, language=task.language, fp16=False)
                    text = result["text"].strip()
                    if text:
                        transcriptions.append({
                            "start": current_time + start,
                            "end": current_time + end,
                            "text": text
                        })
                except Exception as e:
                    logger.error(f"Transcription failed for chunk: {e}")
                    continue

            # Generate output
            if task.output_format == "srt":
                result = self._generate_srt(transcriptions)
            else:
                result = {"transcription": " ".join([t["text"] for t in transcriptions]), "segments": transcriptions}

            self.tasks[task.task_id]["status"] = TaskStatus.COMPLETED
            self.tasks[task.task_id]["result"] = result

            # Cleanup temp files
            os.unlink(task.audio_path)
            if os.path.exists(normalized_path):
                os.unlink(normalized_path)

        except Exception as e:
            logger.error(f"Task {task.task_id} failed: {e}")
            self.tasks[task.task_id]["status"] = TaskStatus.FAILED
            self.tasks[task.task_id]["error"] = str(e)

    def _generate_srt(self, segments: list) -> str:
        """
        Generate SRT subtitle format.
        """
        srt_lines = []
        for i, seg in enumerate(segments, 1):
            start = self._format_time(seg["start"])
            end = self._format_time(seg["end"])
            text = seg["text"]
            srt_lines.append(f"{i}\n{start} --> {end}\n{text}\n")
        return "\n".join(srt_lines)

    def _format_time(self, seconds: float) -> str:
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
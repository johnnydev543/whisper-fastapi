import asyncio
import logging
import os
import tempfile
import uuid
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form
from fastapi.responses import JSONResponse
import uvicorn

from hardware import HardwareManager
from audio import AudioProcessor
from worker import Worker, Task
from models import TaskResponse, HealthResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global instances
hardware_manager = HardwareManager()
audio_processor = AudioProcessor()
worker = Worker(hardware_manager, audio_processor)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Initializing hardware and models...")
    try:
        success, hw_type = hardware_manager.detect_and_load_model()
        if not success:
            logger.error("Failed to initialize hardware. Using CPU fallback.")
            hw_type = "cpu"
            # Load model anyway
            import whisper
            hardware_manager.model = whisper.load_model("tiny", device="cpu")
            hardware_manager.hardware_type = "cpu"
    except Exception as e:
        logger.error(f"Hardware init failed: {e}. Using CPU.")
        import whisper
        hardware_manager.model = whisper.load_model("tiny", device="cpu")
        hardware_manager.hardware_type = "cpu"
        hw_type = "cpu"

    logger.info(f"Hardware initialized: {hw_type}")

    # Start worker
    worker_task = asyncio.create_task(worker.start())

    yield

    # Shutdown
    logger.info("Shutting down...")
    worker.stop()
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass

app = FastAPI(lifespan=lifespan)

@app.post("/transcribe", response_model=dict)
async def transcribe_audio(
    file: UploadFile = File(...),
    model: str = Form(default="tiny"),
    language: Optional[str] = Form(default=None),
    output_format: str = Form(default="json")
):
    # Validate file type
    allowed_extensions = ['.wav', '.flac', '.mp3', '.m4a', '.ogg']
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_ext}. Supported: {allowed_extensions}")

    # Check temperatures
    cpu_temp, hailo_temp = hardware_manager.get_temperatures()
    if cpu_temp > 80 or (hailo_temp and hailo_temp > 75):
        raise HTTPException(status_code=503, detail="System temperature too high. Please try again later.")

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext, dir="/tmp" if os.name != 'nt' else None) as tmp:
        content = await file.read()
        tmp.write(content)
        audio_path = tmp.name

    # Create task
    task_id = str(uuid.uuid4())
    task = Task(
        task_id=task_id,
        audio_path=audio_path,
        model_name=model,
        language=language,
        output_format=output_format
    )

    await worker.add_task(task)

    return {"task_id": task_id}

@app.get("/task/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str):
    status = worker.get_task_status(task_id)
    return TaskResponse(
        task_id=task_id,
        status=status["status"],
        result=status.get("result"),
        error=status.get("error"),
        model=status.get("model"),
        language=status.get("language"),
        output_format=status.get("output_format")
    )

@app.get("/health", response_model=HealthResponse)
async def health():
    cpu_temp, hailo_temp = hardware_manager.get_temperatures()
    queue_length = worker.queue.qsize()

    return HealthResponse(
        hardware_engine=hardware_manager.get_hardware_type(),
        cpu_temperature=cpu_temp,
        hailo_temperature=hailo_temp,
        queue_length=queue_length
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
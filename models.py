from pydantic import BaseModel
from typing import Optional, Dict, Any, Union
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class TranscribeRequest(BaseModel):
    model: Optional[str] = "tiny"
    language: Optional[str] = None
    output_format: Optional[str] = "json"  # json or srt

class TaskResponse(BaseModel):
    task_id: str
    status: TaskStatus
    result: Optional[Union[str, Dict[str, Any]]] = None
    error: Optional[str] = None
    model: Optional[str] = None
    language: Optional[str] = None
    output_format: Optional[str] = None

class HealthResponse(BaseModel):
    hardware_engine: str
    cpu_temperature: float
    hailo_temperature: Optional[float] = None
    queue_length: int
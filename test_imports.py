#!/usr/bin/env python3
"""
Test that all required imports work correctly.
"""

import sys
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Test that all required imports work"""
    try:
        import whisper
        import onnxruntime as ort
        import psutil
        import fastapi
        import uvicorn
        import asyncio
        import threading
        import queue
        import tempfile
        import hashlib
        import json
        import time
        import subprocess
        import ffmpeg
        from fastapi import FastAPI, File, UploadFile, HTTPException, BackgroundTasks
        from pydantic import BaseModel
        import torch
        
        print("All imports successful")
        return True
    except ImportError as e:
        logger.error(f"Import failed: {e}")
        return False

def test_hailo_imports():
    """Test that Hailo-related imports work"""
    try:
        import hailo_platform
        from hailo_platform import Device, HailoRTVersion
        print("Hailo imports successful")
        return True
    except ImportError as e:
        logger.warning(f"Hailo imports failed (optional): {e}")
        return True  # Hailo is optional
    except Exception as e:
        logger.error(f"Hailo imports failed with unexpected error: {e}")
        return False

if __name__ == "__main__":
    result1 = test_imports()
    result2 = test_hailo_imports()
    sys.exit(0 if (result1 and result2) else 1)
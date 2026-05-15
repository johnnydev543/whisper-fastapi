#!/usr/bin/env python3

# Test script to validate imports and basic functionality

try:
    from hardware import HardwareManager
    print("✓ HardwareManager imported")
except ImportError as e:
    print(f"✗ HardwareManager import failed: {e}")

try:
    from audio import AudioProcessor
    print("✓ AudioProcessor imported")
except ImportError as e:
    print(f"✗ AudioProcessor import failed: {e}")

try:
    from worker import Worker, Task
    print("✓ Worker imported")
except ImportError as e:
    print(f"✗ Worker import failed: {e}")

try:
    from models import TranscribeRequest, TaskResponse, HealthResponse
    print("✓ Models imported")
except ImportError as e:
    print(f"✗ Models import failed: {e}")

try:
    from main import app
    print("✓ FastAPI app imported")
except ImportError as e:
    print(f"✗ FastAPI app import failed: {e}")

print("Basic validation complete.")
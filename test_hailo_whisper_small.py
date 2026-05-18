#!/usr/bin/env python3
"""
Test script for Hailo-8 Whisper small model integration.
This script tests the integration of Hailo-8 with Whisper small model.
"""

import sys
import os
import logging
from hardware import HardwareManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hailo_whisper_small():
    """Test Hailo-8 with Whisper small model"""
    print("Testing Hailo-8 with Whisper small model...")
    
    # Initialize hardware manager
    hw_manager = HardwareManager()
    
    # Try to load Whisper small model with Hailo detection
    success, hardware_type = hw_manager.detect_and_load_model("small")
    
    print(f"Hardware detection result: {success}")
    print(f"Hardware type: {hardware_type}")
    
    if hardware_type == "hailo":
        print("SUCCESS: Hailo-8 detected and Whisper small model loaded")
        return True
    elif success:
        print(f"INFO: Model loaded with fallback hardware: {hardware_type}")
        return True
    else:
        print("FAILED: Could not load Whisper small model")
        return False

if __name__ == "__main__":
    try:
        result = test_hailo_whisper_small()
        sys.exit(0 if result else 1)
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        sys.exit(1)
#!/usr/bin/env python3
"""
Test script for Hailo-8 integration with Whisper models.
This script specifically tests the integration of Hailo-8 with Whisper small model.
"""

import sys
import os
import logging
from hardware import HardwareManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_hailo_detection():
    """Test Hailo device detection"""
    print("Testing Hailo device detection...")
    
    try:
        import hailo_platform
        from hailo_platform import Device
        devices = Device.scan()
        print(f"Found {len(devices)} Hailo device(s)")
        
        if devices:
            device = devices[0]
            print(f"Connected to Hailo device: {device}")
            return True
        else:
            print("No Hailo devices found")
            return False
    except ImportError:
        print("hailo_platform not installed")
        return False
    except Exception as e:
        print(f"Hailo detection failed: {e}")
        return False

def test_hailo_model_loading():
    """Test loading Whisper model for Hailo inference"""
    print("Testing Whisper model loading for Hailo...")
    
    hw_manager = HardwareManager()
    
    # Test loading small model specifically for Hailo
    model = hw_manager.load_hailo_model("small")
    
    if model is not None:
        print("SUCCESS: Whisper small model loaded for Hailo inference")
        return True
    else:
        print("FAILED: Could not load Whisper small model for Hailo")
        return False

def test_hardware_detection_with_hailo():
    """Test hardware detection with Hailo preference"""
    print("Testing hardware detection with Hailo preference...")
    
    hw_manager = HardwareManager()
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

def main():
    """Run all Hailo integration tests"""
    print("Running Hailo-8 Whisper integration tests...")
    print("=" * 50)
    
    # Test 1: Hailo detection
    test1_result = test_hailo_detection()
    print()
    
    # Test 2: Model loading
    test2_result = test_hailo_model_loading()
    print()
    
    # Test 3: Hardware detection
    test3_result = test_hardware_detection_with_hailo()
    print()
    
    print("=" * 50)
    if test1_result and test2_result and test3_result:
        print("All Hailo integration tests PASSED")
        return True
    else:
        print("Some Hailo integration tests FAILED")
        return False

if __name__ == "__main__":
    try:
        result = main()
        sys.exit(0 if result else 1)
    except Exception as e:
        logger.error(f"Test failed with exception: {e}")
        sys.exit(1)
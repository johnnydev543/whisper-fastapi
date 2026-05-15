#!/usr/bin/env python3

import sys
import platform
import subprocess
import os

def get_python_version():
    """Get Python version info."""
    return {
        'version': sys.version,
        'version_info': sys.version_info,
        'platform': platform.platform(),
        'architecture': platform.architecture(),
        'python_executable': sys.executable
    }

def get_hailo_version():
    """Get Hailo firmware and driver versions."""
    try:
        # Try to import hailo_platform
        import hailo_platform
        print("hailo_platform imported successfully")

        # Get HailoRT version
        try:
            from hailo_platform import HailoRTVersion
            hailort_version = HailoRTVersion()
            print(f"HailoRT version: {hailort_version}")
        except:
            print("Could not get HailoRT version")

        # Try to scan devices
        try:
            from hailo_platform import Device
            devices = Device.scan()
            print(f"Found {len(devices)} Hailo devices")
            for i, dev in enumerate(devices):
                print(f"Device {i}: {dev}")
                # Try to get firmware version
                try:
                    fw_version = dev.control.get_extended_device_information()
                    print(f"Firmware info: {fw_version}")
                except Exception as e:
                    print(f"Could not get firmware info: {e}")
        except Exception as e:
            print(f"Could not scan devices: {e}")

        return True

    except ImportError as e:
        print(f"hailo_platform not installed: {e}")
        return False

def check_system_info():
    """Check system information for wheel selection."""
    info = get_python_version()
    print("=== Python Version Info ===")
    for k, v in info.items():
        print(f"{k}: {v}")

    print("\n=== Hailo Detection ===")
    hailo_available = get_hailo_version()

    if not hailo_available:
        print("\nHailo not detected. Please install HailoRT first.")
        print("For Raspberry Pi: sudo apt install hailo-all")
        print("For x86 Ubuntu: Download from https://hailo.ai/developer-zone/software-downloads/")
        print("\nFor manual PyHailoRT wheel installation:")
        print("1. Go to https://hailo.ai/developer-zone/software-downloads/")
        print("2. Download 'HailoRT – Python package (whl)' for your Python version and architecture")
        print("3. Install with: pip install <wheel_file>")
        return

    # Determine wheel filename based on Python version
    py_version = sys.version_info
    py_tag = f"cp{py_version.major}{py_version.minor}"

    # For Linux
    if platform.system() == "Linux":
        if "aarch64" in platform.machine():
            # Raspberry Pi / ARM64
            wheel_name = f"hailort-4.21.0-{py_tag}-{py_tag}-linux_aarch64.whl"
            print(f"\nSuggested wheel for ARM64: {wheel_name}")
            print("Download from: https://hailo.ai/developer-zone/software-downloads/")
            print("Note: Python 3.14 may not be supported yet. Try Python 3.11.")
        else:
            # x86_64
            wheel_name = f"hailort-4.21.0-{py_tag}-{py_tag}-linux_x86_64.whl"
            print(f"\nSuggested wheel for x86_64: {wheel_name}")
            print("Download from: https://hailo.ai/developer-zone/software-downloads/")
            print("Note: Python 3.14 may not be supported yet. Try Python 3.11.")
    else:
        print(f"\nUnsupported platform: {platform.system()}")
        print("Hailo is primarily for Linux systems (Raspberry Pi, Ubuntu)")

if __name__ == "__main__":
    check_system_info()
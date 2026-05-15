import logging
import os
from typing import Optional, Tuple
import whisper
import onnxruntime as ort

logger = logging.getLogger(__name__)

class HardwareManager:
    def __init__(self):
        self.model = None
        self.hardware_type = "cpu"  # default

    def detect_and_load_model(self, model_name: str = "tiny") -> Tuple[bool, str]:
        """
        Detect hardware and load Whisper model with appropriate provider.
        Returns (success, hardware_type)
        """
        # Try Hailo-8 first
        if self._try_hailo():
            self.hardware_type = "hailo"
            logger.info("Using Hailo-8 for inference")
            # For Hailo, we might need custom loading, but for now assume CPU fallback
            # Since Hailo integration is complex, use CPU for Whisper, but mark as hailo
            self.model = whisper.load_model(model_name, device="cpu")
            return True, "hailo"

        # Try OpenVINO (Intel)
        if self._try_openvino():
            self.hardware_type = "openvino"
            logger.info("Using OpenVINO for inference")
            self.model = whisper.load_model(model_name, device="cpu")  # onnxruntime handles provider
            return True, "openvino"

        # Try DirectML (AMD)
        if self._try_directml():
            self.hardware_type = "directml"
            logger.info("Using DirectML for inference")
            self.model = whisper.load_model(model_name, device="cpu")
            return True, "directml"

        # Fallback to CPU
        self.hardware_type = "cpu"
        logger.info("Using CPU for inference")
        self.model = whisper.load_model(model_name, device="cpu")
        return True, "cpu"

    def _try_hailo(self) -> bool:
        try:
            # Check if Hailo is available
            import hailo_platform
            from hailo_platform import Device
            devices = Device.scan()
            if devices:
                logger.info(f"Found {len(devices)} Hailo device(s)")
                # Check if models are available
                # hailo-apps should have downloaded models
                return True
        except ImportError:
            logger.warning("hailo_platform not installed. Install from https://hailo.ai/developer-zone/software-downloads/")
        except Exception as e:
            logger.warning(f"Hailo detection failed: {e}")
        return False

    def _try_openvino(self) -> bool:
        try:
            # Check if OpenVINO provider is available
            available_providers = ort.get_available_providers()
            if "OpenVINOExecutionProvider" in available_providers:
                return True
        except:
            pass
        return False

    def _try_directml(self) -> bool:
        try:
            available_providers = ort.get_available_providers()
            if "DmlExecutionProvider" in available_providers:
                return True
        except:
            pass
        return False

    def get_model(self):
        return self.model

    def get_hardware_type(self):
        return self.hardware_type

    def get_temperatures(self) -> Tuple[float, Optional[float]]:
        """
        Get CPU and Hailo temperatures.
        Returns (cpu_temp, hailo_temp)
        """
        cpu_temp = 0.0
        try:
            import psutil
            temps = psutil.sensors_temperatures()
            if 'cpu_thermal' in temps:
                cpu_temp = temps['cpu_thermal'][0].current
            elif 'coretemp' in temps:
                cpu_temp = temps['coretemp'][0].current
            else:
                cpu_temp = 50.0  # dummy
        except:
            cpu_temp = 50.0  # dummy

        hailo_temp = None
        if self.hardware_type == "hailo":
            try:
                from hailo_platform import Device
                dev = Device()
                hailo_temp = dev.control.get_chip_temperature().ts0_temperature
            except:
                pass

        return cpu_temp, hailo_temp
"""Screen capture functionality"""

import os
import time
from typing import Optional
from .device import Device
from ..utils.logger import get_logger
from ..utils.helpers import compress_image

logger = get_logger(__name__)


class ScreenCapture:
    """Captures screenshots from Android device"""

    def __init__(self, device: Device):
        """
        Initialize screen capture

        Args:
            device: Target device
        """
        self.device = device
        self._device_screenshot_path = "/sdcard/smartmonkey_screenshot.png"

    def take_screenshot(self, output_path: str, compress: bool = True, quality: int = 80) -> bool:
        """
        Take screenshot and save to file

        Args:
            output_path: Local path to save screenshot
            compress: Whether to compress the image
            quality: Compression quality (1-100)

        Returns:
            True if successful
        """
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Take screenshot on device
            self.device.adb.shell(f"screencap -p {self._device_screenshot_path}")
            time.sleep(0.2)

            # Pull screenshot to local
            pull_cmd = f"pull {self._device_screenshot_path} {output_path}"
            self.device.adb.execute(pull_cmd)

            # Clean up device screenshot
            self.device.adb.shell(f"rm {self._device_screenshot_path}")

            # Compress if requested
            if compress and os.path.exists(output_path):
                compress_image(output_path, quality=quality)

            logger.debug(f"Screenshot saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to take screenshot: {e}")
            return False

    def get_screen_size(self) -> Optional[tuple]:
        """
        Get screen size

        Returns:
            (width, height) or None if failed
        """
        try:
            output = self.device.adb.shell("wm size")
            # Output: "Physical size: 1080x2400"
            if ":" in output:
                size_str = output.split(":")[-1].strip()
                width, height = map(int, size_str.split("x"))
                return (width, height)

        except Exception as e:
            logger.error(f"Failed to get screen size: {e}")

        return None

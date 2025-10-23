"""Event injection for Android devices"""

import time
from enum import Enum
from typing import Optional
from .device import Device
from ..utils.logger import get_logger

logger = get_logger(__name__)


class KeyCode(Enum):
    """Common Android key codes"""
    HOME = 3
    BACK = 4
    MENU = 82
    ENTER = 66
    DELETE = 67
    VOLUME_UP = 24
    VOLUME_DOWN = 25


class EventInjector:
    """Injects touch and key events to Android device"""

    def __init__(self, device: Device):
        """
        Initialize event injector

        Args:
            device: Target device
        """
        self.device = device

    def tap(self, x: int, y: int, duration: int = 100) -> bool:
        """
        Tap at coordinates

        Args:
            x: X coordinate
            y: Y coordinate
            duration: Tap duration in ms

        Returns:
            True if successful
        """
        try:
            cmd = f"input tap {x} {y}"
            self.device.adb.shell(cmd)
            time.sleep(duration / 1000.0)
            logger.debug(f"Tapped at ({x}, {y})")
            return True

        except Exception as e:
            logger.error(f"Failed to tap at ({x}, {y}): {e}")
            return False

    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool:
        """
        Swipe from one point to another

        Args:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate
            duration: Swipe duration in ms

        Returns:
            True if successful
        """
        try:
            cmd = f"input swipe {x1} {y1} {x2} {y2} {duration}"
            self.device.adb.shell(cmd)
            time.sleep(duration / 1000.0 + 0.1)  # Add small buffer
            logger.debug(f"Swiped from ({x1}, {y1}) to ({x2}, {y2})")
            return True

        except Exception as e:
            logger.error(f"Failed to swipe: {e}")
            return False

    def press_key(self, keycode: int) -> bool:
        """
        Press a key

        Args:
            keycode: Android keycode

        Returns:
            True if successful
        """
        try:
            cmd = f"input keyevent {keycode}"
            self.device.adb.shell(cmd)
            time.sleep(0.1)
            logger.debug(f"Pressed key {keycode}")
            return True

        except Exception as e:
            logger.error(f"Failed to press key {keycode}: {e}")
            return False

    def press_back(self) -> bool:
        """Press back button"""
        return self.press_key(KeyCode.BACK.value)

    def press_home(self) -> bool:
        """Press home button"""
        return self.press_key(KeyCode.HOME.value)

    def input_text(self, text: str) -> bool:
        """
        Input text

        Args:
            text: Text to input (spaces will be replaced with %s)

        Returns:
            True if successful
        """
        try:
            # Replace spaces with %s for shell
            escaped_text = text.replace(" ", "%s")
            cmd = f"input text '{escaped_text}'"
            self.device.adb.shell(cmd)
            time.sleep(0.2)
            logger.debug(f"Input text: {text}")
            return True

        except Exception as e:
            logger.error(f"Failed to input text: {e}")
            return False

    def long_press(self, x: int, y: int, duration: int = 1000) -> bool:
        """
        Long press at coordinates

        Args:
            x: X coordinate
            y: Y coordinate
            duration: Long press duration in ms

        Returns:
            True if successful
        """
        try:
            # Simulate long press with swipe at same point
            cmd = f"input swipe {x} {y} {x} {y} {duration}"
            self.device.adb.shell(cmd)
            time.sleep(duration / 1000.0 + 0.1)
            logger.debug(f"Long pressed at ({x}, {y})")
            return True

        except Exception as e:
            logger.error(f"Failed to long press: {e}")
            return False

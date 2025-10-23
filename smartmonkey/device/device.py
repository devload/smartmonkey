"""Device abstraction"""

from typing import Optional, Dict
from .adb_manager import ADBManager
from ..utils.logger import get_logger
from ..utils.exceptions import DeviceConnectionError

logger = get_logger(__name__)


class Device:
    """Represents an Android device"""

    def __init__(self, serial: str):
        """
        Initialize device

        Args:
            serial: Device serial number
        """
        self.serial = serial
        self.adb = ADBManager(device_serial=serial)
        self._info: Optional[Dict[str, str]] = None
        self._connected = False

    def connect(self) -> bool:
        """
        Connect to device

        Returns:
            True if connected successfully
        """
        try:
            if not self.adb.is_device_connected():
                raise DeviceConnectionError(f"Device {self.serial} not found")

            # Get device info
            self._info = self._get_device_info()
            self._connected = True

            logger.info(f"Connected to device: {self.serial} ({self.model})")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to device {self.serial}: {e}")
            self._connected = False
            return False

    def disconnect(self) -> None:
        """Disconnect from device"""
        self._connected = False
        logger.info(f"Disconnected from device: {self.serial}")

    def is_connected(self) -> bool:
        """Check if device is connected"""
        if not self._connected:
            return False
        return self.adb.is_device_connected()

    def _get_device_info(self) -> Dict[str, str]:
        """
        Get device information

        Returns:
            Dictionary with device info
        """
        info = {}

        try:
            # Get model
            info['model'] = self.adb.shell("getprop ro.product.model").strip()

            # Get Android version
            info['android_version'] = self.adb.shell("getprop ro.build.version.release").strip()

            # Get SDK version
            info['sdk_version'] = self.adb.shell("getprop ro.build.version.sdk").strip()

            # Get manufacturer
            info['manufacturer'] = self.adb.shell("getprop ro.product.manufacturer").strip()

        except Exception as e:
            logger.warning(f"Failed to get some device info: {e}")

        return info

    @property
    def model(self) -> str:
        """Get device model"""
        return self._info.get('model', 'Unknown') if self._info else 'Unknown'

    @property
    def android_version(self) -> str:
        """Get Android version"""
        return self._info.get('android_version', 'Unknown') if self._info else 'Unknown'

    @property
    def sdk_version(self) -> str:
        """Get SDK version"""
        return self._info.get('sdk_version', 'Unknown') if self._info else 'Unknown'

    @property
    def manufacturer(self) -> str:
        """Get manufacturer"""
        return self._info.get('manufacturer', 'Unknown') if self._info else 'Unknown'

    def __repr__(self) -> str:
        return f"Device({self.serial}, {self.model})"

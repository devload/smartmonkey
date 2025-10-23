"""ADB Manager for executing ADB commands"""

import subprocess
import time
from typing import List, Optional
from ..utils.exceptions import ADBCommandError, DeviceConnectionError
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ADBManager:
    """Manages ADB command execution"""

    def __init__(self, device_serial: Optional[str] = None, timeout: int = 30):
        """
        Initialize ADB Manager

        Args:
            device_serial: Device serial number (None for single device)
            timeout: Default command timeout in seconds
        """
        self.device_serial = device_serial
        self.timeout = timeout

    def _build_command(self, command: str, use_shell: bool = False) -> List[str]:
        """
        Build ADB command with device serial

        Args:
            command: ADB command
            use_shell: Whether to use adb shell

        Returns:
            Command as list of strings
        """
        cmd = ["adb"]

        if self.device_serial:
            cmd.extend(["-s", self.device_serial])

        if use_shell:
            cmd.append("shell")

        cmd.extend(command.split())
        return cmd

    def execute(self, command: str, timeout: Optional[int] = None, retries: int = 3) -> str:
        """
        Execute ADB command

        Args:
            command: ADB command to execute
            timeout: Command timeout (uses default if None)
            retries: Number of retries on failure

        Returns:
            Command output

        Raises:
            ADBCommandError: If command execution fails
        """
        timeout = timeout or self.timeout
        cmd = self._build_command(command)

        for attempt in range(retries):
            try:
                logger.debug(f"Executing: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=timeout,
                    check=False
                )

                if result.returncode != 0:
                    error_msg = result.stderr.strip() or result.stdout.strip()
                    if "device not found" in error_msg.lower():
                        raise DeviceConnectionError(f"Device not found: {self.device_serial}")

                    logger.warning(f"Command failed (attempt {attempt + 1}/{retries}): {error_msg}")
                    if attempt < retries - 1:
                        time.sleep(1)
                        continue
                    raise ADBCommandError(f"ADB command failed: {error_msg}")

                return result.stdout.strip()

            except subprocess.TimeoutExpired:
                logger.warning(f"Command timeout (attempt {attempt + 1}/{retries})")
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                raise ADBCommandError(f"ADB command timeout after {timeout}s")

            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                if attempt < retries - 1:
                    time.sleep(1)
                    continue
                raise ADBCommandError(f"ADB command failed: {str(e)}")

        raise ADBCommandError("Failed after all retries")

    def shell(self, command: str, timeout: Optional[int] = None) -> str:
        """
        Execute ADB shell command

        Args:
            command: Shell command
            timeout: Command timeout

        Returns:
            Command output
        """
        cmd = self._build_command(command, use_shell=True)
        cmd_str = " ".join(cmd)

        try:
            logger.debug(f"Executing shell: {cmd_str}")
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout or self.timeout,
                check=False
            )

            if result.returncode != 0 and "error" in result.stderr.lower():
                raise ADBCommandError(f"Shell command failed: {result.stderr}")

            return result.stdout.strip()

        except subprocess.TimeoutExpired:
            raise ADBCommandError(f"Shell command timeout after {timeout or self.timeout}s")
        except Exception as e:
            raise ADBCommandError(f"Shell command failed: {str(e)}")

    def get_devices(self) -> List[str]:
        """
        Get list of connected devices

        Returns:
            List of device serial numbers
        """
        try:
            output = self.execute("devices")
            devices = []

            for line in output.splitlines()[1:]:  # Skip "List of devices attached"
                if line.strip() and "\tdevice" in line:
                    serial = line.split("\t")[0]
                    devices.append(serial)

            return devices

        except Exception as e:
            logger.error(f"Failed to get devices: {e}")
            return []

    def is_device_connected(self) -> bool:
        """
        Check if device is connected

        Returns:
            True if device is connected
        """
        try:
            devices = self.get_devices()
            if self.device_serial:
                return self.device_serial in devices
            return len(devices) > 0
        except Exception:
            return False

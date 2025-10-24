"""App management functionality"""

import time
from typing import Optional
from .device import Device
from ..utils.logger import get_logger
from ..utils.exceptions import AppNotFoundError

logger = get_logger(__name__)


class AppManager:
    """Manages app lifecycle on Android device"""

    def __init__(self, device: Device):
        """
        Initialize app manager

        Args:
            device: Target device
        """
        self.device = device

    def get_launcher_activity(self, package: str) -> Optional[str]:
        """
        Get the main launcher activity for a package

        Args:
            package: App package name

        Returns:
            Launcher activity name or None
        """
        try:
            cmd = f"dumpsys package {package} | grep -A 5 'android.intent.action.MAIN'"
            output = self.device.adb.shell(cmd)

            # Parse output to find launcher activity
            # Format: "io.whatap.session.sample/.Screen1Activity filter"
            for line in output.split('\n'):
                if package in line and '/' in line:
                    # Extract activity name
                    parts = line.split()
                    for part in parts:
                        if package in part and '/' in part:
                            # Extract just the activity part after /
                            activity = part.split('/')[-1]
                            logger.info(f"Found launcher activity: {activity}")
                            return activity

            logger.warning(f"Could not find launcher activity for {package}")
            return None

        except Exception as e:
            logger.error(f"Failed to get launcher activity: {e}")
            return None

    def launch_app(self, package: str, activity: Optional[str] = None, wait: bool = True) -> bool:
        """
        Launch app

        Args:
            package: App package name
            activity: Activity name (optional, will use main activity if not provided)
            wait: Whether to wait for app to launch

        Returns:
            True if successful
        """
        try:
            # Determine which activity to launch
            if activity:
                component = f"{package}/{activity}"
            else:
                # Auto-detect launcher activity
                launcher_activity = self.get_launcher_activity(package)
                if launcher_activity:
                    component = f"{package}/{launcher_activity}"
                else:
                    # Fallback to monkey if we can't find launcher activity
                    logger.warning(f"Using monkey command as fallback for {package}")
                    cmd = f"monkey -p {package} -c android.intent.category.LAUNCHER 1"
                    self.device.adb.shell(cmd)

                    if wait:
                        time.sleep(2)

                    logger.info(f"Launched app: {package} (via monkey)")
                    return True

            # Use am start to launch app
            cmd = f"am start -n {component} -a android.intent.action.MAIN -c android.intent.category.LAUNCHER"
            output = self.device.adb.shell(cmd)

            # Check if launch was successful
            if "Error" in output or "exception" in output.lower():
                logger.warning(f"am start failed, trying with monkey command: {output}")
                # Fallback to monkey command
                cmd = f"monkey -p {package} -c android.intent.category.LAUNCHER 1"
                self.device.adb.shell(cmd)

            if wait:
                time.sleep(2)  # Wait for app to launch

            logger.info(f"Launched app: {package}")
            return True

        except Exception as e:
            logger.error(f"Failed to launch app {package}: {e}")
            return False

    def stop_app(self, package: str) -> bool:
        """
        Stop app

        Args:
            package: App package name

        Returns:
            True if successful
        """
        try:
            cmd = f"am force-stop {package}"
            self.device.adb.shell(cmd)
            logger.info(f"Stopped app: {package}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop app {package}: {e}")
            return False

    def clear_app_data(self, package: str) -> bool:
        """
        Clear app data

        Args:
            package: App package name

        Returns:
            True if successful
        """
        try:
            cmd = f"pm clear {package}"
            output = self.device.adb.shell(cmd)

            if "success" in output.lower():
                logger.info(f"Cleared app data: {package}")
                return True
            else:
                logger.warning(f"Failed to clear app data: {output}")
                return False

        except Exception as e:
            logger.error(f"Failed to clear app data {package}: {e}")
            return False

    def is_app_installed(self, package: str) -> bool:
        """
        Check if app is installed

        Args:
            package: App package name

        Returns:
            True if app is installed
        """
        try:
            cmd = f"pm list packages | grep {package}"
            output = self.device.adb.shell(cmd)
            return package in output

        except Exception:
            return False

    def get_current_activity(self) -> Optional[str]:
        """
        Get current activity

        Returns:
            Current activity name or None
        """
        try:
            # Try dumpsys window (not "windows")
            cmd = "dumpsys window | grep -E 'mCurrentFocus|mFocusedApp'"
            output = self.device.adb.shell(cmd)

            if output:
                # Parse activity from output
                # Format: "mCurrentFocus=Window{... u0 package/activity}"
                for line in output.split('\n'):
                    if 'mCurrentFocus' in line or 'mFocusedApp' in line:
                        parts = line.split()
                        for part in parts:
                            if '/' in part and not part.startswith('Window'):
                                activity = part.split('}')[0] if '}' in part else part
                                return activity

        except Exception as e:
            logger.error(f"Failed to get current activity: {e}")

        return None

    def is_app_running(self, package: str) -> bool:
        """
        Check if app is currently running

        Args:
            package: App package name

        Returns:
            True if app is running
        """
        try:
            current = self.get_current_activity()
            return current is not None and package in current

        except Exception:
            return False

    def install_apk(self, apk_path: str) -> bool:
        """
        Install APK

        Args:
            apk_path: Path to APK file

        Returns:
            True if successful
        """
        try:
            cmd = f"install -r {apk_path}"
            output = self.device.adb.execute(cmd, timeout=60)

            if "success" in output.lower():
                logger.info(f"Installed APK: {apk_path}")
                return True
            else:
                logger.error(f"Failed to install APK: {output}")
                return False

        except Exception as e:
            logger.error(f"Failed to install APK {apk_path}: {e}")
            return False

    def uninstall_app(self, package: str) -> bool:
        """
        Uninstall app

        Args:
            package: App package name

        Returns:
            True if successful
        """
        try:
            cmd = f"uninstall {package}"
            output = self.device.adb.execute(cmd)

            if "success" in output.lower():
                logger.info(f"Uninstalled app: {package}")
                return True
            else:
                logger.warning(f"Failed to uninstall app: {output}")
                return False

        except Exception as e:
            logger.error(f"Failed to uninstall app {package}: {e}")
            return False

"""Core exploration engine"""

import time
from typing import List, Optional, Dict
from datetime import datetime
from ..device.device import Device
from ..device.app_manager import AppManager
from ..device.screen_capture import ScreenCapture
from .ui_parser import UIParser
from .state import AppState
from .action import Action
from .strategies.base import ExplorationStrategy
from ..utils.logger import get_logger
from ..utils.helpers import ensure_dir

logger = get_logger(__name__)


class ExplorationResult:
    """Result of exploration"""

    def __init__(self):
        self.states: List[AppState] = []
        self.actions: List[Action] = []
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.total_events = 0
        self.unique_states = 0
        self.crash_detected = False
        self.crash_info: Optional[str] = None

    def finish(self):
        """Mark exploration as finished"""
        self.end_time = datetime.now()
        self.total_events = len(self.actions)
        self.unique_states = len(set(s.state_hash for s in self.states))

    @property
    def duration(self) -> float:
        """Get duration in seconds"""
        if not self.end_time:
            return 0.0
        return (self.end_time - self.start_time).total_seconds()


class ExplorationEngine:
    """Explores app using given strategy"""

    def __init__(
        self,
        device: Device,
        strategy: ExplorationStrategy,
        package: str,
        screenshot_dir: str = "./screenshots"
    ):
        """
        Initialize exploration engine

        Args:
            device: Target device
            strategy: Exploration strategy
            package: App package name
            screenshot_dir: Directory to save screenshots
        """
        self.device = device
        self.strategy = strategy
        self.package = package
        self.screenshot_dir = screenshot_dir

        self.ui_parser = UIParser(device)
        self.app_manager = AppManager(device)
        self.screen_capture = ScreenCapture(device)

        self.visited_states: Dict[str, int] = {}
        self.current_state: Optional[AppState] = None
        self.consecutive_no_elements = 0  # Track consecutive states with no elements

        ensure_dir(screenshot_dir)

    def explore(self, max_steps: int = 100, save_screenshots: bool = True) -> ExplorationResult:
        """
        Explore app for given number of steps

        Args:
            max_steps: Maximum number of actions to perform
            save_screenshots: Whether to save screenshots

        Returns:
            ExplorationResult
        """
        result = ExplorationResult()

        logger.info(f"Starting exploration with {self.strategy.name} strategy")
        logger.info(f"Package: {self.package}, Max steps: {max_steps}")

        # Launch app
        if not self.app_manager.launch_app(self.package):
            logger.error("Failed to launch app")
            result.finish()
            return result

        time.sleep(2)  # Wait for app to stabilize

        try:
            for step in range(max_steps):
                logger.info(f"\n=== Step {step + 1}/{max_steps} ===")

                # Capture current state
                state = self._capture_state(step, save_screenshots)
                if not state:
                    logger.warning("Failed to capture state, stopping")
                    break

                result.states.append(state)
                self.current_state = state

                # Track visited states
                state_hash = state.state_hash
                self.visited_states[state_hash] = self.visited_states.get(state_hash, 0) + 1

                logger.info(f"State: {state.activity}")
                logger.info(f"Clickable elements: {len(state.get_clickable_elements())}")
                logger.info(f"State hash: {state_hash[:8]}... (visited {self.visited_states[state_hash]} times)")

                # ALWAYS check if app is still running (every step)
                if not self._is_app_running():
                    logger.error(f"🔴 APP EXITED! App {self.package} is not in foreground!")
                    result.crash_detected = True
                    result.crash_info = f"App exited or moved to background after step {step + 1}"
                    logger.error(f"Last action before exit: {result.actions[-1] if result.actions else 'None'}")
                    break

                # Check if app crashed (no clickable elements for multiple consecutive steps)
                if len(state.get_clickable_elements()) == 0:
                    self.consecutive_no_elements += 1

                    if self.consecutive_no_elements >= 3:
                        logger.warning(f"⚠️ No clickable elements for {self.consecutive_no_elements} consecutive steps")
                        logger.warning("Possible app crash or stuck state. Stopping exploration.")
                        result.crash_detected = True
                        result.crash_info = f"No UI elements for {self.consecutive_no_elements} consecutive steps"
                        break
                else:
                    self.consecutive_no_elements = 0  # Reset counter

                # Select next action
                action = self.strategy.next_action(state)
                if not action:
                    logger.info("No action available, stopping")
                    break

                logger.info(f"Action: {action}")
                result.actions.append(action)

                # Execute action
                if not action.execute(self.device):
                    logger.warning("Action execution failed")

                # Wait for UI to settle
                time.sleep(1)

        except KeyboardInterrupt:
            logger.info("\nExploration interrupted by user")
        except Exception as e:
            logger.error(f"Exploration error: {e}")
        finally:
            result.finish()
            logger.info(f"\n=== Exploration Complete ===")
            logger.info(f"Duration: {result.duration:.1f}s")
            logger.info(f"Total events: {result.total_events}")
            logger.info(f"Unique states: {result.unique_states}")

        return result

    def _capture_state(self, step: int, save_screenshot: bool = True) -> Optional[AppState]:
        """
        Capture current app state

        Args:
            step: Current step number
            save_screenshot: Whether to save screenshot

        Returns:
            AppState or None if failed
        """
        try:
            # Get current activity
            activity = self.app_manager.get_current_activity()
            if not activity:
                activity = "Unknown"

            # Dump UI hierarchy
            elements = self.ui_parser.dump_hierarchy()

            # Take screenshot
            screenshot_path = None
            if save_screenshot:
                screenshot_path = f"{self.screenshot_dir}/screenshot_{step:04d}.png"
                self.screen_capture.take_screenshot(screenshot_path)

            state = AppState(
                activity=activity,
                elements=elements,
                screenshot_path=screenshot_path
            )

            return state

        except Exception as e:
            logger.error(f"Failed to capture state: {e}")
            return None

    def _is_app_running(self) -> bool:
        """
        Check if target app is still running

        Returns:
            True if app is running
        """
        try:
            current_activity = self.app_manager.get_current_activity()
            if current_activity and self.package in current_activity:
                return True
            return False
        except Exception:
            return False

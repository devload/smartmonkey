"""Chrome Device wrapper integrating CDP and ADB"""

import asyncio
from typing import Optional
from ..device import Device
from ..event_injector import EventInjector
from .chrome_manager import ChromeDevToolsManager
from ...exploration.html.html_parser import HTMLParser
from ...exploration.html.html_element import HTMLElement
from ...exploration.html.html_state import HTMLState
from ...exploration.action import Action, ActionType
from ...utils.logger import get_logger

logger = get_logger(__name__)


class ChromeDevice:
    """
    Chrome Device wrapper that integrates CDP and ADB.

    This class combines:
    - Chrome DevTools Protocol (CDP) for HTML DOM inspection
    - Android Debug Bridge (ADB) for touch/swipe events

    It provides a unified interface for web testing that is
    compatible with existing SmartMonkey exploration strategies.
    """

    def __init__(self, device_serial: str, cdp_port: int = 9222):
        """
        Initialize ChromeDevice.

        Args:
            device_serial: Android device serial (e.g., "emulator-5556")
            cdp_port: Chrome DevTools Protocol port (default: 9222)
        """
        # Initialize ADB device for touch/swipe
        self.device = Device(device_serial)

        # Initialize event injector for touch/swipe actions
        self.event_injector = EventInjector(self.device)

        # Initialize CDP manager for HTML inspection
        ws_url = f"ws://localhost:{cdp_port}/devtools/page/1"
        self.cdp = ChromeDevToolsManager(ws_url=ws_url)

        # HTML parser for extracting elements
        self.parser: Optional[HTMLParser] = None

        # Current URL
        self.current_url: Optional[str] = None

    async def connect(self, initial_url: Optional[str] = None) -> bool:
        """
        Connect to both ADB device and Chrome browser.

        Args:
            initial_url: Optional URL to navigate to after connection

        Returns:
            True if connection successful
        """
        try:
            # Connect to ADB device
            if not self.device.connect():
                logger.error(f"Failed to connect to ADB device: {self.device.serial}")
                return False

            # Connect to Chrome via CDP
            if not await self.cdp.connect():
                logger.error("Failed to connect to Chrome DevTools")
                return False

            # Initialize parser
            self.parser = HTMLParser(self.cdp)

            # Navigate to initial URL if provided
            if initial_url:
                await self.navigate_to(initial_url)

            # Get current URL
            self.current_url = await self.cdp.evaluate_js("document.URL")

            logger.info(f"ChromeDevice connected: {self.device.serial} -> {self.current_url}")
            return True

        except Exception as e:
            logger.error(f"ChromeDevice connection failed: {e}")
            return False

    async def disconnect(self):
        """Disconnect from Chrome and ADB"""
        if self.cdp:
            await self.cdp.disconnect()
        if self.device:
            self.device.disconnect()
        logger.info("ChromeDevice disconnected")

    async def navigate_to(self, url: str):
        """
        Navigate to URL.

        Args:
            url: URL to navigate to
        """
        await self.cdp.navigate_to(url)
        self.current_url = url
        logger.info(f"Navigated to: {url}")

    async def get_current_state(self) -> HTMLState:
        """
        Get current page state.

        Returns:
            HTMLState object containing page elements
        """
        if not self.parser:
            raise RuntimeError("Parser not initialized. Call connect() first.")

        # Wait for page to be fully loaded and rendered
        await asyncio.sleep(2.0)

        # Extract DOM elements (DOMNode objects)
        dom_nodes = await self.parser.get_clickable_elements()

        # Get current URL
        url = await self.cdp.evaluate_js("document.URL")
        self.current_url = url

        # Create and return HTMLState with DOMNode objects directly
        state = HTMLState(url, dom_nodes, self.cdp)

        logger.debug(f"State extracted: {len(dom_nodes)} elements from {url}")
        return state

    async def execute_action(self, action: Action):
        """
        Execute action on web page.

        For HTML elements, we use ADB tap/swipe on coordinates
        since CDP click doesn't always work reliably.

        Args:
            action: Action to execute
        """
        if action.action_type == ActionType.TAP:
            # Get screen dimensions via ADB
            screen_size = self.device.adb.shell("wm size").strip()
            # Parse "Physical size: 1080x2400"
            if ":" in screen_size:
                size_str = screen_size.split(":")[-1].strip()
                width, height = map(int, size_str.split("x"))
            else:
                # Default fallback for Samsung
                width, height = 1080, 2400

            # Validate and clamp coordinates within screen bounds
            clamped_x = max(0, min(action.x, width - 1))
            clamped_y = max(0, min(action.y, height - 1))

            if clamped_x != action.x or clamped_y != action.y:
                logger.warning(f"Click coordinates ({action.x}, {action.y}) out of bounds. "
                             f"Screen size: {width}x{height}. "
                             f"Clamping to ({clamped_x}, {clamped_y})")
                action.x = clamped_x
                action.y = clamped_y

            logger.info(f"Executing action: TAP at ({action.x}, {action.y})")
            # Use ADB tap for reliability
            self.event_injector.tap(action.x, action.y)
            await asyncio.sleep(0.5)  # Wait for page response

        elif action.action_type == ActionType.SWIPE:
            logger.info(f"Executing action: SWIPE from ({action.start_x}, {action.start_y}) to ({action.end_x}, {action.end_y})")
            # Use ADB swipe
            self.event_injector.swipe(
                action.start_x, action.start_y,
                action.end_x, action.end_y,
                duration=action.duration
            )
            await asyncio.sleep(0.5)

        elif action.action_type == ActionType.BACK:
            logger.info("Executing action: BACK")
            # Use ADB back button
            self.event_injector.press_back()
            await asyncio.sleep(0.5)

        else:
            logger.warning(f"Unsupported action type: {action.action_type}")

    async def capture_screenshot(self, output_path: str, click_x: int = None, click_y: int = None,
                                swipe_start_x: int = None, swipe_start_y: int = None,
                                swipe_end_x: int = None, swipe_end_y: int = None) -> bool:
        """
        Capture screenshot using ADB screencap (more reliable than CDP).
        Optionally draws a circle marker at click position or swipe gesture.

        Args:
            output_path: Path to save screenshot
            click_x: X coordinate of click position (optional)
            click_y: Y coordinate of click position (optional)
            swipe_start_x: X coordinate of swipe start (optional)
            swipe_start_y: Y coordinate of swipe start (optional)
            swipe_end_x: X coordinate of swipe end (optional)
            swipe_end_y: Y coordinate of swipe end (optional)

        Returns:
            True if successful
        """
        try:
            # Use ADB screencap instead of CDP to avoid caching issues
            import os

            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            device_screenshot_path = "/sdcard/smartmonkey_chrome_screenshot.png"

            # Take screenshot on device
            screencap_result = self.device.adb.shell(f"screencap -p {device_screenshot_path}")
            await asyncio.sleep(0.3)  # Wait for file to be written

            # Verify screenshot was created on device
            ls_result = self.device.adb.shell(f"ls -l {device_screenshot_path}")
            if "No such file" in ls_result:
                logger.error(f"Screenshot file not created on device: {device_screenshot_path}")
                return False

            # Pull screenshot to local
            pull_cmd = f"pull {device_screenshot_path} {output_path}"
            pull_result = self.device.adb.execute(pull_cmd)

            # Verify screenshot was pulled successfully
            if not os.path.exists(output_path):
                logger.error(f"Failed to pull screenshot to local: {output_path}")
                return False

            # Clean up device screenshot
            self.device.adb.shell(f"rm {device_screenshot_path}")

            # Draw markers if coordinates provided
            if click_x is not None and click_y is not None:
                # Click marker
                try:
                    from PIL import Image, ImageDraw

                    # Open screenshot
                    img = Image.open(output_path)
                    draw = ImageDraw.Draw(img)

                    # Draw red circle at click position
                    radius = 30
                    circle_bbox = [
                        click_x - radius,
                        click_y - radius,
                        click_x + radius,
                        click_y + radius
                    ]

                    # Draw outer circle (red)
                    draw.ellipse(circle_bbox, outline='red', width=5)

                    # Draw inner circle (semi-transparent red fill)
                    inner_radius = radius - 10
                    inner_bbox = [
                        click_x - inner_radius,
                        click_y - inner_radius,
                        click_x + inner_radius,
                        click_y + inner_radius
                    ]
                    draw.ellipse(inner_bbox, fill=(255, 0, 0, 100), outline='red', width=3)

                    # Draw crosshair
                    line_length = 15
                    draw.line([click_x - line_length, click_y, click_x + line_length, click_y], fill='red', width=3)
                    draw.line([click_x, click_y - line_length, click_x, click_y + line_length], fill='red', width=3)

                    # Save annotated image
                    img.save(output_path)
                    logger.info(f"Screenshot saved with click marker at ({click_x}, {click_y}): {output_path}")

                except ImportError:
                    logger.warning("PIL/Pillow not installed. Screenshot saved without click marker.")
                except Exception as e:
                    logger.warning(f"Failed to draw click marker: {e}")
            elif (swipe_start_x is not None and swipe_start_y is not None and
                  swipe_end_x is not None and swipe_end_y is not None):
                # Swipe/drag marker
                try:
                    from PIL import Image, ImageDraw
                    import math

                    # Open screenshot
                    img = Image.open(output_path)
                    draw = ImageDraw.Draw(img)

                    # Draw circles at start and end points
                    circle_radius = 40

                    # Start point (green circle)
                    start_bbox = [
                        swipe_start_x - circle_radius,
                        swipe_start_y - circle_radius,
                        swipe_start_x + circle_radius,
                        swipe_start_y + circle_radius
                    ]
                    draw.ellipse(start_bbox, outline='green', width=8)

                    # End point (blue circle)
                    end_bbox = [
                        swipe_end_x - circle_radius,
                        swipe_end_y - circle_radius,
                        swipe_end_x + circle_radius,
                        swipe_end_y + circle_radius
                    ]
                    draw.ellipse(end_bbox, outline='blue', width=8)

                    # Draw thick arrow from start to end
                    # Calculate angle for arrowhead
                    dx = swipe_end_x - swipe_start_x
                    dy = swipe_end_y - swipe_start_y
                    angle = math.atan2(dy, dx)

                    # Draw main arrow line (thick)
                    draw.line([swipe_start_x, swipe_start_y, swipe_end_x, swipe_end_y],
                             fill='yellow', width=12)

                    # Draw arrowhead
                    arrow_length = 60
                    arrow_angle = math.pi / 6  # 30 degrees

                    # Left side of arrowhead
                    left_x = swipe_end_x - arrow_length * math.cos(angle - arrow_angle)
                    left_y = swipe_end_y - arrow_length * math.sin(angle - arrow_angle)

                    # Right side of arrowhead
                    right_x = swipe_end_x - arrow_length * math.cos(angle + arrow_angle)
                    right_y = swipe_end_y - arrow_length * math.sin(angle + arrow_angle)

                    # Draw arrowhead lines
                    draw.line([swipe_end_x, swipe_end_y, left_x, left_y], fill='yellow', width=12)
                    draw.line([swipe_end_x, swipe_end_y, right_x, right_y], fill='yellow', width=12)

                    # Save annotated image
                    img.save(output_path)
                    logger.info(f"Screenshot saved with swipe marker from ({swipe_start_x}, {swipe_start_y}) "
                               f"to ({swipe_end_x}, {swipe_end_y}): {output_path}")

                except ImportError:
                    logger.warning("PIL/Pillow not installed. Screenshot saved without swipe marker.")
                except Exception as e:
                    logger.warning(f"Failed to draw swipe marker: {e}")
            else:
                logger.info(f"Screenshot saved: {output_path}")

            return True

        except Exception as e:
            logger.error(f"Screenshot capture failed: {e}")
            return False

    async def scroll_page(self, direction: str = "down", distance: int = 500):
        """
        Scroll the page.

        Args:
            direction: "up" or "down"
            distance: Pixels to scroll
        """
        scroll_y = distance if direction == "down" else -distance
        await self.cdp.evaluate_js(f"window.scrollBy(0, {scroll_y})")
        await asyncio.sleep(0.3)  # Wait for scroll to complete

    async def reload_page(self):
        """Reload current page"""
        await self.cdp.reload()
        await asyncio.sleep(1.0)  # Wait for page load

    def is_connected(self) -> bool:
        """Check if connected"""
        return self.device.is_connected() and self.cdp._ws is not None

    @property
    def serial(self) -> str:
        """Get device serial"""
        return self.device.serial

    @property
    def url(self) -> Optional[str]:
        """Get current URL"""
        return self.current_url

    def __repr__(self) -> str:
        return f"ChromeDevice(serial={self.serial}, url={self.current_url})"

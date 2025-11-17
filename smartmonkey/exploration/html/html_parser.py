"""Simplified HTML DOM Parser using Chrome DevTools Protocol"""

import asyncio
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class DOMNode:
    """Represents a DOM node (HTML element)"""

    node_id: int
    tag_name: str
    text_content: str
    attributes: Dict[str, str] = field(default_factory=dict)
    is_visible: bool = True
    is_clickable: bool = False
    is_input: bool = False
    coordinates: Optional[Dict[str, int]] = None  # {x, y, width, height}

    @property
    def center_x(self) -> Optional[int]:
        """Get center X coordinate"""
        if self.coordinates:
            return self.coordinates["x"] + self.coordinates["width"] // 2
        return None

    @property
    def center_y(self) -> Optional[int]:
        """Get center Y coordinate"""
        if self.coordinates:
            return self.coordinates["y"] + self.coordinates["height"] // 2
        return None

    @property
    def width(self) -> int:
        """Get width"""
        if self.coordinates:
            return self.coordinates.get("width", 0)
        return 0

    @property
    def height(self) -> int:
        """Get height"""
        if self.coordinates:
            return self.coordinates.get("height", 0)
        return 0

    @property
    def href(self) -> Optional[str]:
        """Get href attribute for links"""
        return self.attributes.get("href")

    @property
    def css_selector(self) -> str:
        """Generate CSS selector for element"""
        selector = self.tag_name

        # Add ID if available
        if self.attributes.get("id"):
            selector += f"#{self.attributes['id']}"

        # Add class if available
        if self.attributes.get("class"):
            classes = self.attributes["class"].split()
            selector += "." + ".".join(classes[:2])  # First 2 classes

        return selector

    def is_interactable(self) -> bool:
        """Check if element can be interacted with"""
        return self.is_visible and (self.is_clickable or self.is_input)

    def __repr__(self) -> str:
        text_preview = self.text_content[:30].replace("\n", " ").strip()
        return f"<{self.tag_name} text='{text_preview}...' clickable={self.is_clickable}>"


class HTMLParser:
    """Simplified HTML Parser using Chrome DevTools Protocol"""

    # CSS selectors for different element types
    CLICKABLE_SELECTORS = [
        "a",
        "button",
        "[role='button']",
        "[onclick]",
        "input[type='button']",
        "input[type='submit']",
    ]

    def __init__(self, cdp_manager: "ChromeDevToolsManager"):  # noqa: F821
        """
        Initialize HTML parser

        Args:
            cdp_manager: Chrome DevTools manager instance
        """
        self.cdp = cdp_manager

    async def get_clickable_elements(self) -> List[DOMNode]:
        """
        Get all clickable HTML elements

        Returns:
            List of clickable DOM nodes
        """
        try:
            logger.info("Starting HTML element extraction...")

            # Get document
            doc = await self.cdp.get_document()
            root_node_id = doc.get("root", {}).get("nodeId")

            if not root_node_id:
                logger.error("Could not get document root")
                return []

            logger.info(f"Document root node ID: {root_node_id}")

            clickable = []
            seen_ids = set()

            # Query for each selector type
            for selector in self.CLICKABLE_SELECTORS:
                try:
                    node_ids = await self.cdp.query_selector_all(selector, node_id=root_node_id)
                    logger.info(f"Found {len(node_ids)} elements for selector '{selector}'")

                    for node_id in node_ids:
                        if node_id in seen_ids:
                            continue

                        # Get node details
                        try:
                            # Get attributes
                            attrs = await self.cdp.get_attributes(node_id)

                            # Get coordinates
                            coords = await self._get_coordinates(node_id)

                            # Skip if no coordinates or size is 0
                            if not coords or coords["width"] == 0 or coords["height"] == 0:
                                continue

                            # **FIX**: Skip elements outside viewport (화면 밖 요소 제외)
                            # 모바일 화면 크기는 일반적으로 ~3000px 이하
                            # y 좌표가 3500을 넘으면 화면 밖으로 판단
                            if coords["y"] > 3500:
                                logger.debug(f"Skipping element outside viewport: y={coords['y']}")
                                continue

                            # Get text content
                            text = await self._get_text_via_js(node_id)

                            # Create node
                            node = DOMNode(
                                node_id=node_id,
                                tag_name=selector.split('[')[0],  # Extract tag name
                                text_content=text,
                                attributes=attrs,
                                is_visible=True,
                                is_clickable=True,
                                coordinates=coords
                            )

                            clickable.append(node)
                            seen_ids.add(node_id)

                        except Exception as e:
                            logger.debug(f"Failed to process node {node_id}: {e}")
                            continue

                except Exception as e:
                    logger.debug(f"Error querying {selector}: {e}")
                    continue

            logger.info(f"✅ Found {len(clickable)} interactive HTML elements")
            return clickable

        except Exception as e:
            logger.error(f"Failed to get clickable elements: {e}", exc_info=True)
            return []

    async def _get_coordinates(self, node_id: int) -> Optional[Dict[str, int]]:
        """
        Get element screen coordinates (physical screen pixels for ADB tap)

        Args:
            node_id: Node ID

        Returns:
            Dictionary with x, y, width, height or None
        """
        try:
            box_model = await self.cdp.get_box_model(node_id)
            model = box_model.get("model", {})

            # Get content area (CSS pixel coordinates)
            content = model.get("content", [])

            if not content or len(content) < 8:
                return None

            # Content area: [x1, y1, x2, y1, x2, y2, x1, y2]
            # These are CSS pixel coordinates (may include scroll offset and zoom)
            x1_css, y1_css = int(content[0]), int(content[1])
            x2_css, y2_css = int(content[4]), int(content[5])

            width = max(0, x2_css - x1_css)
            height = max(0, y2_css - y1_css)

            # Get viewport info: scroll position and device pixel ratio
            try:
                # Get scroll position
                scroll_x = await self.cdp.evaluate_js("window.scrollX || window.pageXOffset || 0")
                scroll_y = await self.cdp.evaluate_js("window.scrollY || window.pageYOffset || 0")

                # Get device pixel ratio (physical pixels per CSS pixel)
                # On mobile, this is often > 1 (e.g., 2.625 for 1080p with viewport width=411)
                dpr = await self.cdp.evaluate_js("window.devicePixelRatio || 1")

                # Get viewport dimensions (CSS pixels)
                viewport_width = await self.cdp.evaluate_js("window.innerWidth || document.documentElement.clientWidth")
                viewport_height = await self.cdp.evaluate_js("window.innerHeight || document.documentElement.clientHeight")

                # Convert to numbers
                scroll_x = int(float(scroll_x))
                scroll_y = int(float(scroll_y))
                dpr = float(dpr)
                viewport_width_css = int(float(viewport_width))
                viewport_height_css = int(float(viewport_height))

            except Exception as e:
                logger.debug(f"Failed to get viewport info: {e}")
                scroll_x = 0
                scroll_y = 0
                dpr = 1.0
                viewport_width_css = 0
                viewport_height_css = 0

            # Convert CSS coordinates to viewport coordinates (remove scroll)
            x1_viewport_css = x1_css - scroll_x
            y1_viewport_css = y1_css - scroll_y

            # Get browser chrome height (address bar, toolbar, etc.)
            # This is the offset between viewport (0,0) and actual screen (0,0)
            try:
                # Method 1: Try visualViewport.offsetTop (works on some browsers)
                offset_top = await self.cdp.evaluate_js("window.visualViewport ? window.visualViewport.offsetTop : -1")
                offset_top = int(float(offset_top))

                if offset_top > 0:
                    browser_chrome_height = offset_top
                else:
                    # Method 2: Calculate from screen height vs innerHeight
                    # Both are in CSS pixels, need to convert to physical
                    screen_height_css = await self.cdp.evaluate_js("window.screen.height")
                    inner_height_css = await self.cdp.evaluate_js("window.innerHeight")
                    screen_height_css = int(float(screen_height_css))
                    inner_height_css = int(float(inner_height_css))

                    # Convert both to physical pixels
                    screen_height_physical = int(screen_height_css * dpr)
                    inner_height_physical = int(inner_height_css * dpr)

                    # Difference is all the UI chrome (status bar + address bar + nav bar)
                    total_ui_height = screen_height_physical - inner_height_physical

                    # Subtract status bar (~60px) and bottom nav (~150px) to get just address bar
                    # Total UI is usually 200-250px, address bar is ~140-150px
                    browser_chrome_height = max(0, total_ui_height - 60)  # Remove status bar only

                    logger.info(f"🔍 Chrome UI: screen={screen_height_css}CSS={screen_height_physical}px, "
                              f"inner={inner_height_css}CSS={inner_height_physical}px, "
                              f"UI_total={total_ui_height}px, chrome_bar={browser_chrome_height}px")
            except Exception as e:
                logger.debug(f"Failed to get browser chrome height: {e}")
                # Fallback: typical mobile Chrome has ~56dp address bar
                # With DPR ~2.6, that's about 145 physical pixels
                browser_chrome_height = int(56 * dpr)

            # Convert CSS pixels to physical screen pixels for ADB tap
            # Physical pixel = CSS pixel * devicePixelRatio
            x1_physical = int(x1_viewport_css * dpr)
            y1_physical = int(y1_viewport_css * dpr) + browser_chrome_height
            width_physical = int(width * dpr)
            height_physical = int(height * dpr)

            # Validate coordinates are within screen bounds
            # Get physical screen dimensions
            try:
                screen_width_physical = int(screen_height_css * dpr * 0.45)  # Approximate aspect ratio
                screen_height_physical = int(screen_height_css * dpr)
            except:
                screen_width_physical = 1080  # Common mobile width
                screen_height_physical = 2400  # Common mobile height

            # Check if coordinates are out of bounds
            if x1_physical < 0 or y1_physical < 0:
                logger.warning(f"⚠️  Element at ({x1_physical}, {y1_physical}) is out of bounds (negative coordinates)! Skipping.")
                return None

            if x1_physical >= screen_width_physical or y1_physical >= screen_height_physical:
                logger.warning(f"⚠️  Element at ({x1_physical}, {y1_physical}) is out of bounds (exceeds screen {screen_width_physical}x{screen_height_physical})! Skipping.")
                return None

            # Debug: Log conversion for debugging (INFO level for visibility)
            if x1_css > 1000 or dpr > 1.5 or x1_physical > 1080:
                logger.info(f"🔍 Coord: CSS=({x1_css},{y1_css}) scroll=({scroll_x},{scroll_y}) "
                           f"viewport_CSS=({x1_viewport_css},{y1_viewport_css}) DPR={dpr:.2f} "
                           f"chrome_height={browser_chrome_height}px "
                           f"→ physical=({x1_physical},{y1_physical}) [viewport:{viewport_width_css}x{viewport_height_css} CSS]")

            return {
                "x": x1_physical,
                "y": y1_physical,
                "width": width_physical,
                "height": height_physical,
            }

        except Exception as e:
            logger.debug(f"Failed to get coordinates for node {node_id}: {e}")
            return None

    async def _get_text_via_js(self, node_id: int) -> str:
        """
        Get text content using JavaScript via object ID

        Args:
            node_id: Node ID

        Returns:
            Text content
        """
        try:
            # Resolve node to runtime object
            resolve_result = await self.cdp.send_command("DOM.resolveNode", {
                "nodeId": node_id
            })

            if "object" not in resolve_result:
                return ""

            object_id = resolve_result["object"].get("objectId")
            if not object_id:
                return ""

            # Get textContent property
            props_result = await self.cdp.send_command("Runtime.getProperties", {
                "objectId": object_id,
                "ownProperties": False
            })

            for prop in props_result.get("result", []):
                if prop.get("name") == "textContent":
                    value = prop.get("value", {})
                    text = value.get("value", "")
                    if text:
                        return str(text).strip()[:200]

            return ""

        except Exception as e:
            logger.debug(f"Failed to get text for node {node_id}: {e}")
            return ""

    def clear_cache(self) -> None:
        """Clear node cache (compatibility method)"""
        pass

    def __repr__(self) -> str:
        return f"HTMLParser(cdp={self.cdp})"

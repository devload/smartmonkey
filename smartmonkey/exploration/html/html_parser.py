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
        Get element screen coordinates

        Args:
            node_id: Node ID

        Returns:
            Dictionary with x, y, width, height or None
        """
        try:
            box_model = await self.cdp.get_box_model(node_id)
            model = box_model.get("model", {})

            # Get content area
            content = model.get("content", [])

            if not content or len(content) < 8:
                return None

            # Content area: [x1, y1, x2, y1, x2, y2, x1, y2]
            x1, y1 = int(content[0]), int(content[1])
            x2, y2 = int(content[4]), int(content[5])

            width = max(0, x2 - x1)
            height = max(0, y2 - y1)

            return {
                "x": x1,
                "y": y1,
                "width": width,
                "height": height,
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

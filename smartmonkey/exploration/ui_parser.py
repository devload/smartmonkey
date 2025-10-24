"""UI hierarchy parser"""

import re
from typing import List, Optional
from lxml import etree
from ..device.device import Device
from .element import UIElement, Rect
from ..utils.logger import get_logger
from ..utils.exceptions import UIParseError

logger = get_logger(__name__)


class UIParser:
    """Parses UI hierarchy from uiautomator dump"""

    def __init__(self, device: Device):
        """
        Initialize UI parser

        Args:
            device: Target device
        """
        self.device = device
        self._device_dump_path = "/sdcard/smartmonkey_uidump.xml"

    def dump_hierarchy(self) -> List[UIElement]:
        """
        Dump UI hierarchy and parse elements

        Returns:
            List of UI elements

        Raises:
            UIParseError: If parsing fails
        """
        try:
            # Dump UI hierarchy to device
            dump_cmd = f"uiautomator dump {self._device_dump_path}"
            self.device.adb.shell(dump_cmd)

            # Read dumped XML
            cat_cmd = f"cat {self._device_dump_path}"
            xml_content = self.device.adb.shell(cat_cmd)

            # Clean up
            self.device.adb.shell(f"rm {self._device_dump_path}")

            # Parse XML
            return self.parse(xml_content)

        except Exception as e:
            logger.error(f"Failed to dump UI hierarchy: {e}")
            raise UIParseError(f"UI dump failed: {str(e)}")

    def parse(self, xml_content: str) -> List[UIElement]:
        """
        Parse UI hierarchy XML

        Args:
            xml_content: UI hierarchy XML string

        Returns:
            List of UI elements
        """
        try:
            elements = []

            # Parse XML
            root = etree.fromstring(xml_content.encode())

            # Recursively parse nodes
            self._parse_node(root, elements, index=0)

            logger.debug(f"Parsed {len(elements)} UI elements")
            return elements

        except Exception as e:
            logger.error(f"Failed to parse UI XML: {e}")
            raise UIParseError(f"XML parsing failed: {str(e)}")

    def _parse_node(self, node, elements: List[UIElement], index: int) -> int:
        """
        Recursively parse XML node

        Args:
            node: XML node
            elements: List to append elements to
            index: Current element index

        Returns:
            Updated index
        """
        # Parse current node
        element = self._parse_element(node, index)
        if element:
            elements.append(element)
            index += 1

        # Parse children
        for child in node:
            index = self._parse_node(child, elements, index)

        return index

    def _parse_element(self, node, index: int) -> Optional[UIElement]:
        """
        Parse single XML node to UIElement

        Args:
            node: XML node
            index: Element index

        Returns:
            UIElement or None
        """
        try:
            # Get attributes
            resource_id = node.get('resource-id', '')
            class_name = node.get('class', '')
            text = node.get('text', '')
            content_desc = node.get('content-desc', '')
            package = node.get('package', '')
            clickable = node.get('clickable', 'false') == 'true'
            scrollable = node.get('scrollable', 'false') == 'true'
            enabled = node.get('enabled', 'true') == 'true'
            # 'displayed' attribute is not always present, check bounds instead
            visible = node.get('displayed', 'true') == 'true'

            # Parse bounds: "[left,top][right,bottom]"
            bounds_str = node.get('bounds', '[0,0][0,0]')
            bounds = self._parse_bounds(bounds_str)

            # Create element
            element = UIElement(
                resource_id=resource_id,
                class_name=class_name,
                text=text if text else None,
                content_desc=content_desc if content_desc else None,
                bounds=bounds,
                clickable=clickable and enabled,
                scrollable=scrollable and enabled,
                visible=visible,
                package=package,
                index=index
            )

            return element

        except Exception as e:
            logger.warning(f"Failed to parse element: {e}")
            return None

    def _parse_bounds(self, bounds_str: str) -> Rect:
        """
        Parse bounds string to Rect

        Args:
            bounds_str: Bounds string like "[0,0][1080,2400]"

        Returns:
            Rect object
        """
        try:
            # Extract coordinates using regex
            pattern = r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]'
            match = re.match(pattern, bounds_str)

            if match:
                left, top, right, bottom = map(int, match.groups())
                return Rect(left, top, right, bottom)

        except Exception as e:
            logger.warning(f"Failed to parse bounds '{bounds_str}': {e}")

        # Return default bounds if parsing fails
        return Rect(0, 0, 0, 0)

    def get_clickable_elements(self, elements: List[UIElement]) -> List[UIElement]:
        """
        Filter clickable elements

        Args:
            elements: All UI elements

        Returns:
            List of clickable elements
        """
        return [e for e in elements if e.clickable and e.visible and e.bounds.width > 0]

    def get_scrollable_elements(self, elements: List[UIElement]) -> List[UIElement]:
        """
        Filter scrollable elements

        Args:
            elements: All UI elements

        Returns:
            List of scrollable elements
        """
        return [e for e in elements if e.scrollable and e.visible]

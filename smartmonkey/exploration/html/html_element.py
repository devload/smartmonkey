"""HTML Element adapter to UIElement interface"""

from typing import Optional
from ..element import UIElement, Rect


class HTMLElement(UIElement):
    """
    Adapter class that converts DOMNode to UIElement interface.

    This allows HTML elements from Chrome browser to be used with
    existing SmartMonkey exploration strategies without modification.
    """

    def __init__(self, dom_node, package: str = "chrome"):
        """
        Initialize HTMLElement from DOMNode.

        Args:
            dom_node: DOMNode object from HTMLParser
            package: Package name (default: "chrome")
        """
        # Extract attributes
        attrs = dom_node.attributes if hasattr(dom_node, 'attributes') else {}

        # Create Rect from DOMNode coordinates
        # DOMNode has coordinates dict {x, y, width, height}
        coords = dom_node.coordinates if dom_node.coordinates else {"x": 0, "y": 0, "width": 0, "height": 0}

        bounds = Rect(
            left=coords["x"],
            top=coords["y"],
            right=coords["x"] + coords["width"],
            bottom=coords["y"] + coords["height"]
        )

        # Extract resource_id from 'id' attribute
        resource_id = attrs.get('id', '')

        # Create class_name from tag_name (e.g., "html.button", "html.a")
        class_name = f"html.{dom_node.tag_name}"

        # Extract text content
        text = dom_node.text_content.strip() if dom_node.text_content else None

        # Extract content description from 'title' or 'aria-label' attributes
        content_desc = attrs.get('aria-label') or attrs.get('title') or None

        # HTML elements are always clickable by definition
        # (since we query only clickable elements)
        clickable = True

        # HTML elements are not scrollable (use page scroll instead)
        scrollable = False

        # HTML elements are visible (CDP filters invisible elements)
        visible = True

        # Initialize parent UIElement
        super().__init__(
            resource_id=resource_id,
            class_name=class_name,
            text=text,
            content_desc=content_desc,
            bounds=bounds,
            clickable=clickable,
            scrollable=scrollable,
            visible=visible,
            package=package,
            index=0,
            visit_count=0
        )

        # Store original DOMNode for reference
        self._dom_node = dom_node
        self._attributes = attrs

    @property
    def tag_name(self) -> str:
        """Get HTML tag name (e.g., 'a', 'button', 'input')"""
        return self._dom_node.tag_name

    @property
    def node_id(self) -> int:
        """Get CDP node ID for element manipulation"""
        return self._dom_node.node_id

    @property
    def attributes(self) -> dict:
        """Get all HTML attributes"""
        return self._attributes

    def get_attribute(self, name: str, default: Optional[str] = None) -> Optional[str]:
        """Get specific HTML attribute by name"""
        return self._attributes.get(name, default)

    @property
    def href(self) -> Optional[str]:
        """Get href attribute (for links)"""
        return self.get_attribute('href')

    @property
    def css_classes(self) -> list:
        """Get CSS classes as list"""
        class_attr = self.get_attribute('class', '')
        return class_attr.split() if class_attr else []

    def __repr__(self) -> str:
        return f"HTMLElement({self.tag_name}, text='{self.text}', clickable={self.clickable})"

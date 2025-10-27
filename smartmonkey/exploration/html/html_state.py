"""HTML State adapter to AppState interface"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from ..state import AppState
from ...utils.helpers import calculate_hash


@dataclass
class HTMLState(AppState):
    """
    Adapter class that represents HTML page state as AppState.

    This allows HTML web pages to be used with existing SmartMonkey
    exploration strategies without modification.
    """

    def __init__(self, url: str, elements: List,
                 cdp, screenshot_path: Optional[str] = None):
        """
        Initialize HTMLState from URL and DOM elements.

        Args:
            url: Current page URL (used as activity name)
            elements: List of DOMNode objects from HTMLParser
            cdp: ChromeDevToolsManager instance
            screenshot_path: Path to screenshot (optional)
        """
        # Use URL as "activity" name for HTML pages
        activity = url

        # Initialize parent AppState
        super().__init__(
            activity=activity,
            elements=elements,
            screenshot_path=screenshot_path,
            timestamp=datetime.now(),
            _state_hash=None
        )

        # Store CDP manager for additional operations
        self._cdp = cdp
        self._url = url

    @property
    def url(self) -> str:
        """Get current page URL"""
        return self._url

    @property
    def state_hash(self) -> str:
        """
        Get state hash for comparison.

        For HTML pages, we use URL + element count as signature
        since DOM structure can be very large.

        Returns:
            MD5 hash of state
        """
        if not self._state_hash:
            # Create simpler signature for HTML (URL + element count + first 10 element texts)
            signature = f"{self.url}|{len(self.elements)}|"

            # Add text content of first 10 elements for better uniqueness
            text_samples = [
                e.text_content[:20] if hasattr(e, 'text_content') and e.text_content else ""
                for e in self.elements[:10]
            ]
            signature += "|".join(text_samples)

            self._state_hash = calculate_hash(signature)

        return self._state_hash

    def get_links(self) -> List:
        """Get all link elements (anchor tags) - returns DOMNode objects"""
        return [e for e in self.elements if e.tag_name == 'a']

    def get_buttons(self) -> List:
        """Get all button elements - returns DOMNode objects"""
        return [e for e in self.elements if e.tag_name == 'button']

    def get_inputs(self) -> List:
        """Get all input elements - returns DOMNode objects"""
        return [e for e in self.elements if e.tag_name == 'input']

    def get_elements_by_tag(self, tag_name: str) -> List:
        """Get all elements with specific HTML tag - returns DOMNode objects"""
        return [e for e in self.elements if e.tag_name == tag_name]

    def get_elements_by_class(self, class_name: str) -> List:
        """Get all elements with specific CSS class - returns DOMNode objects"""
        return [e for e in self.elements
                if hasattr(e, 'attributes') and 'class' in e.attributes
                and class_name in e.attributes['class']]

    async def get_page_title(self) -> str:
        """Get page title from CDP"""
        if self._cdp:
            return await self._cdp.evaluate_js("document.title")
        return ""

    async def get_page_url(self) -> str:
        """Get current page URL from CDP"""
        if self._cdp:
            return await self._cdp.evaluate_js("document.URL")
        return self._url

    async def scroll_page(self, direction: str = "down", distance: int = 500):
        """
        Scroll the page.

        Args:
            direction: "up" or "down"
            distance: Pixels to scroll
        """
        if self._cdp:
            scroll_y = distance if direction == "down" else -distance
            await self._cdp.evaluate_js(f"window.scrollBy(0, {scroll_y})")

    def __repr__(self) -> str:
        return f"HTMLState(url={self.url}, elements={len(self.elements)}, hash={self.state_hash[:8]})"

"""UI Element representation"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class Rect:
    """Rectangle bounds"""
    left: int
    top: int
    right: int
    bottom: int

    @property
    def center(self) -> tuple:
        """Get center point"""
        return ((self.left + self.right) // 2, (self.top + self.bottom) // 2)

    @property
    def width(self) -> int:
        """Get width"""
        return self.right - self.left

    @property
    def height(self) -> int:
        """Get height"""
        return self.bottom - self.top


@dataclass
class UIElement:
    """Represents a UI element"""
    resource_id: str
    class_name: str
    text: Optional[str]
    content_desc: Optional[str]
    bounds: Rect
    clickable: bool
    scrollable: bool
    visible: bool
    package: str
    index: int = 0
    visit_count: int = 0

    @property
    def center(self) -> tuple:
        """Get center point for tapping"""
        return self.bounds.center

    def is_interactive(self) -> bool:
        """Check if element is interactive"""
        return self.clickable or self.scrollable

    def __repr__(self) -> str:
        return f"UIElement({self.class_name}, text='{self.text}', clickable={self.clickable})"

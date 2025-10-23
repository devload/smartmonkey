"""Application state representation"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from .element import UIElement
from ..utils.helpers import calculate_hash


@dataclass
class AppState:
    """Represents an application state"""
    activity: str
    elements: List[UIElement]
    screenshot_path: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    _state_hash: Optional[str] = None

    @property
    def state_hash(self) -> str:
        """
        Get state hash for comparison

        Returns:
            MD5 hash of state
        """
        if not self._state_hash:
            # Create state signature from activity and elements
            signature = f"{self.activity}|"
            signature += "|".join([
                f"{e.class_name}:{e.text}:{e.resource_id}"
                for e in sorted(self.elements, key=lambda x: x.index)
            ])
            self._state_hash = calculate_hash(signature)

        return self._state_hash

    def get_clickable_elements(self) -> List[UIElement]:
        """Get all clickable elements"""
        return [e for e in self.elements if e.clickable and e.visible]

    def get_scrollable_elements(self) -> List[UIElement]:
        """Get all scrollable elements"""
        return [e for e in self.elements if e.scrollable and e.visible]

    def __repr__(self) -> str:
        return f"AppState(activity={self.activity}, elements={len(self.elements)}, hash={self.state_hash[:8]})"

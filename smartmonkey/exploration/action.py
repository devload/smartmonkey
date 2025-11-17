"""Action representations"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Optional
from ..device.device import Device
from ..device.event_injector import EventInjector
from .element import UIElement
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ActionType(Enum):
    """Types of actions"""
    TAP = "tap"
    SWIPE = "swipe"
    BACK = "back"
    HOME = "home"
    TEXT_INPUT = "text_input"


class Action(ABC):
    """Base class for actions"""

    def __init__(self, action_type: ActionType):
        self.action_type = action_type
        # AI metadata (optional)
        self.ai_reason: Optional[str] = None
        self.ai_expected_effect: Optional[str] = None
        self.ai_confidence: Optional[float] = None

    @abstractmethod
    def execute(self, device: Device) -> bool:
        """
        Execute action on device

        Args:
            device: Target device

        Returns:
            True if successful
        """
        pass

    @abstractmethod
    def __repr__(self) -> str:
        pass

    @abstractmethod
    def to_dict(self) -> dict:
        """
        Convert action to dictionary for JSON serialization

        Returns:
            Dictionary representation of action
        """
        pass


class TapAction(Action):
    """Tap action"""

    def __init__(self, element: Optional[UIElement] = None, x: Optional[int] = None, y: Optional[int] = None):
        """
        Initialize tap action

        Args:
            element: UI element to tap (or provide x, y directly)
            x: X coordinate
            y: Y coordinate
        """
        super().__init__(ActionType.TAP)
        self.element = element

        if element:
            self.x, self.y = element.center
        elif x is not None and y is not None:
            self.x, self.y = x, y
        else:
            raise ValueError("Must provide either element or coordinates")

    def execute(self, device: Device) -> bool:
        injector = EventInjector(device)
        if self.element:
            self.element.visit_count += 1
        return injector.tap(self.x, self.y)

    def __repr__(self) -> str:
        if self.element:
            return f"TapAction(element={self.element.class_name}, text='{self.element.text}')"
        return f"TapAction(x={self.x}, y={self.y})"

    def to_dict(self) -> dict:
        """Convert to dictionary with detailed info"""
        result = {
            "type": self.action_type.value,
            "coordinates": {"x": self.x, "y": self.y}
        }

        if self.element:
            result["element"] = {
                "class": self.element.class_name,
                "text": self.element.text,
                "resource_id": self.element.resource_id,
                "content_desc": self.element.content_desc,
                "bounds": {
                    "left": self.element.bounds.left,
                    "top": self.element.bounds.top,
                    "right": self.element.bounds.right,
                    "bottom": self.element.bounds.bottom
                },
                "rect": {
                    "x1": self.element.bounds.left,
                    "y1": self.element.bounds.top,
                    "x2": self.element.bounds.right,
                    "y2": self.element.bounds.bottom
                }
            }

        # Add AI metadata if available
        if self.ai_reason or self.ai_expected_effect or self.ai_confidence:
            result["ai_metadata"] = {}
            if self.ai_reason:
                result["ai_metadata"]["reason"] = self.ai_reason
            if self.ai_expected_effect:
                result["ai_metadata"]["expected_effect"] = self.ai_expected_effect
            if self.ai_confidence is not None:
                result["ai_metadata"]["confidence"] = self.ai_confidence

        return result


class SwipeAction(Action):
    """Swipe action"""

    def __init__(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
        super().__init__(ActionType.SWIPE)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.duration = duration
        # Add aliases for compatibility
        self.start_x = x1
        self.start_y = y1
        self.end_x = x2
        self.end_y = y2

    def execute(self, device: Device) -> bool:
        injector = EventInjector(device)
        return injector.swipe(self.x1, self.y1, self.x2, self.y2, self.duration)

    def __repr__(self) -> str:
        return f"SwipeAction(from=({self.x1},{self.y1}), to=({self.x2},{self.y2}))"

    def to_dict(self) -> dict:
        """Convert to dictionary with detailed info"""
        return {
            "type": self.action_type.value,
            "from": {"x": self.x1, "y": self.y1},
            "to": {"x": self.x2, "y": self.y2},
            "duration_ms": self.duration
        }


class BackAction(Action):
    """Back button action"""

    def __init__(self):
        super().__init__(ActionType.BACK)

    def execute(self, device: Device) -> bool:
        injector = EventInjector(device)
        return injector.press_back()

    def __repr__(self) -> str:
        return "BackAction()"

    def to_dict(self) -> dict:
        """Convert to dictionary with detailed info"""
        return {
            "type": self.action_type.value,
            "description": "Press back button"
        }


class HomeAction(Action):
    """Home button action"""

    def __init__(self):
        super().__init__(ActionType.HOME)

    def execute(self, device: Device) -> bool:
        injector = EventInjector(device)
        return injector.press_home()

    def __repr__(self) -> str:
        return "HomeAction()"

    def to_dict(self) -> dict:
        """Convert to dictionary with detailed info"""
        return {
            "type": self.action_type.value,
            "description": "Press home button"
        }


class TextInputAction(Action):
    """Text input action"""

    def __init__(self, text: str):
        super().__init__(ActionType.TEXT_INPUT)
        self.text = text

    def execute(self, device: Device) -> bool:
        injector = EventInjector(device)
        return injector.input_text(self.text)

    def __repr__(self) -> str:
        return f"TextInputAction(text='{self.text}')"

    def to_dict(self) -> dict:
        """Convert to dictionary with detailed info"""
        return {
            "type": self.action_type.value,
            "text": self.text,
            "description": f"Input text: '{self.text}'"
        }

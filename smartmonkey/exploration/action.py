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


class SwipeAction(Action):
    """Swipe action"""

    def __init__(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300):
        super().__init__(ActionType.SWIPE)
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.duration = duration

    def execute(self, device: Device) -> bool:
        injector = EventInjector(device)
        return injector.swipe(self.x1, self.y1, self.x2, self.y2, self.duration)

    def __repr__(self) -> str:
        return f"SwipeAction(from=({self.x1},{self.y1}), to=({self.x2},{self.y2}))"


class BackAction(Action):
    """Back button action"""

    def __init__(self):
        super().__init__(ActionType.BACK)

    def execute(self, device: Device) -> bool:
        injector = EventInjector(device)
        return injector.press_back()

    def __repr__(self) -> str:
        return "BackAction()"


class HomeAction(Action):
    """Home button action"""

    def __init__(self):
        super().__init__(ActionType.HOME)

    def execute(self, device: Device) -> bool:
        injector = EventInjector(device)
        return injector.press_home()

    def __repr__(self) -> str:
        return "HomeAction()"


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

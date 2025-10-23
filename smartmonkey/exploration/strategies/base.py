"""Base exploration strategy"""

from abc import ABC, abstractmethod
from typing import Optional
from ..state import AppState
from ..action import Action


class ExplorationStrategy(ABC):
    """Base class for exploration strategies"""

    def __init__(self, name: str):
        """
        Initialize strategy

        Args:
            name: Strategy name
        """
        self.name = name

    @abstractmethod
    def next_action(self, state: AppState) -> Optional[Action]:
        """
        Select next action based on current state

        Args:
            state: Current application state

        Returns:
            Next action to execute, or None if no action available
        """
        pass

    def reset(self) -> None:
        """Reset strategy state"""
        pass

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}()"

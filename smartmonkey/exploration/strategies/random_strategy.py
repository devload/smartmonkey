"""Random exploration strategy"""

import random
from typing import Optional
from .base import ExplorationStrategy
from ..state import AppState
from ..action import Action, TapAction, BackAction
from ...utils.logger import get_logger

logger = get_logger(__name__)


class RandomStrategy(ExplorationStrategy):
    """Randomly select actions"""

    def __init__(self, back_probability: float = 0.1):
        """
        Initialize random strategy

        Args:
            back_probability: Probability of pressing back button
        """
        super().__init__("Random")
        self.back_probability = back_probability

    def next_action(self, state: AppState) -> Optional[Action]:
        """Select random action"""
        # Get clickable elements
        clickable = state.get_clickable_elements()

        if not clickable:
            logger.debug("No clickable elements, pressing back")
            return BackAction()

        # Random chance to press back
        if random.random() < self.back_probability:
            logger.debug("Random back action")
            return BackAction()

        # Random tap on clickable element
        element = random.choice(clickable)
        logger.debug(f"Random tap on {element}")
        return TapAction(element)

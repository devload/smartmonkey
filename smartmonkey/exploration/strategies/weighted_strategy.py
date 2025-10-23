"""Weighted exploration strategy - prioritizes unvisited elements"""

import random
from typing import Optional
from .base import ExplorationStrategy
from ..state import AppState
from ..action import Action, TapAction, BackAction
from ...utils.logger import get_logger

logger = get_logger(__name__)


class WeightedStrategy(ExplorationStrategy):
    """Prioritize unvisited elements"""

    def __init__(self, back_probability: float = 0.05):
        """
        Initialize weighted strategy

        Args:
            back_probability: Probability of pressing back button
        """
        super().__init__("Weighted")
        self.back_probability = back_probability

    def next_action(self, state: AppState) -> Optional[Action]:
        """Select action with weighted probability"""
        # Get clickable elements
        clickable = state.get_clickable_elements()

        if not clickable:
            logger.debug("No clickable elements, pressing back")
            return BackAction()

        # Random chance to press back
        if random.random() < self.back_probability:
            logger.debug("Weighted back action")
            return BackAction()

        # Calculate weights
        weights = []
        for element in clickable:
            if element.visit_count == 0:
                weight = 10.0  # High priority for unvisited
            else:
                weight = 1.0 / (1 + element.visit_count)  # Decreasing weight

            # Boost certain element types
            if 'Button' in element.class_name or 'ImageButton' in element.class_name:
                weight *= 1.5
            elif element.text and any(keyword in element.text.lower() for keyword in ['submit', 'ok', 'yes', 'confirm']):
                weight *= 2.0

            weights.append(weight)

        # Select element based on weights
        element = random.choices(clickable, weights=weights)[0]
        logger.debug(f"Weighted tap on {element} (visit_count={element.visit_count})")
        return TapAction(element)

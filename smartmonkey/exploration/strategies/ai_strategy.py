"""AI-based exploration strategy using Claude Code workspace"""

from typing import Optional
from datetime import datetime
from .base import ExplorationStrategy
from ..state import AppState
from ..action import Action, TapAction, BackAction, SwipeAction
from ...ai.workspace_provider import WorkspaceAIProvider
from ...utils.logger import get_logger

logger = get_logger(__name__)


class AIStrategy(ExplorationStrategy):
    """
    AI-driven exploration strategy using workspace-based Claude Code communication.

    This strategy creates a workspace with CLAUDE.md, screenshots, and UI elements,
    then waits for Claude Code to analyze and provide the next action.
    """

    def __init__(
        self,
        workspace_dir: str,
        test_goal: str,
        test_config: dict,
        package_name: str
    ):
        """
        Initialize AI strategy

        Args:
            workspace_dir: Directory for AI workspace
            test_goal: Natural language test goal
            test_config: Test configuration (credentials, scenario type, etc.)
            package_name: Android app package name
        """
        super().__init__("AI-Workspace")
        self.provider = WorkspaceAIProvider(
            workspace_dir=workspace_dir,
            test_goal=test_goal,
            test_config=test_config,
            package_name=package_name
        )
        self.step = 0
        self.max_steps = 100
        self.history = []

    def set_max_steps(self, max_steps: int):
        """Set maximum steps for this test run"""
        self.max_steps = max_steps

    def next_action(self, state: AppState) -> Optional[Action]:
        """
        Request next action from AI

        Args:
            state: Current app state

        Returns:
            Action to perform, or None if goal achieved
        """

        # Request AI analysis and wait for response
        try:
            response = self.provider.analyze_and_wait(
                state=state,
                step=self.step,
                max_steps=self.max_steps,
                history=self.history
            )
        except TimeoutError as e:
            logger.error(f"AI timeout: {e}")
            logger.info("Falling back to back action")
            return BackAction()

        # Parse response into Action
        action = self._parse_response(response, state)

        # Add to history
        self.history.append({
            "step": self.step,
            "action_type": response.get("action_type"),
            "reasoning": response.get("reasoning"),
            "confidence": response.get("confidence"),
            "target_element_index": response.get("target_element_index"),
            "input_text": response.get("input_text"),
            "timestamp": datetime.now().isoformat()
        })

        self.step += 1

        # Check if goal achieved
        if response.get("goal_achieved"):
            logger.info("🎉 Goal achieved! Stopping exploration.")
            return None

        return action

    def _parse_response(self, response: dict, state: AppState) -> Optional[Action]:
        """
        Parse AI response into Action object

        Args:
            response: AI response dictionary
            state: Current app state

        Returns:
            Action object or None
        """

        action_type = response.get("action_type")

        if action_type == "tap":
            element_index = response.get("target_element_index")
            clickable = state.get_clickable_elements()
            if element_index is not None and element_index < len(clickable):
                element = clickable[element_index]
                logger.info(f"→ Tapping element {element_index}: {element.text or element.class_name}")
                return TapAction(element)
            else:
                logger.warning(f"Invalid element index: {element_index}, available: {len(clickable)}")
                return BackAction()

        elif action_type == "input":
            element_index = response.get("target_element_index")
            input_text = response.get("input_text")
            clickable = state.get_clickable_elements()
            if element_index is not None and element_index < len(clickable) and input_text:
                element = clickable[element_index]
                logger.info(f"→ Inputting text into element {element_index}: '{input_text}'")
                # For now, we'll tap the element (full input action needs implementation)
                return TapAction(element)
            else:
                logger.warning(f"Invalid input action: index={element_index}, text={input_text}")
                return BackAction()

        elif action_type == "swipe_up":
            logger.info("→ Swiping up")
            return SwipeAction(direction="up")

        elif action_type == "swipe_down":
            logger.info("→ Swiping down")
            return SwipeAction(direction="down")

        elif action_type == "back":
            logger.info("→ Pressing back")
            return BackAction()

        elif action_type == "done":
            logger.info("→ Test complete (done)")
            return None

        else:
            logger.warning(f"Unknown action type: {action_type}, using back")
            return BackAction()

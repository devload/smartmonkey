"""AI-driven exploration strategy using Claude Code CLI"""

import os
import asyncio
from typing import Optional
from .base import ExplorationStrategy as BaseStrategy
from ..action import TapAction, BackAction
from ...ai.claude_code_client import ClaudeCodeClient
from ...utils.logger import get_logger

logger = get_logger(__name__)


class AIStrategy(BaseStrategy):
    """Claude Code를 사용한 AI 기반 탐색 전략"""

    def __init__(self, mission: str, workspace_dir: str = None):
        """
        Initialize AI strategy

        Args:
            mission: 달성할 미션 (예: "상품 검색하고 장바구니 담기")
            workspace_dir: Claude Code 워크스페이스 경로
        """
        super().__init__(name="ai")
        self.mission = mission
        self.claude = ClaudeCodeClient(workspace_dir)
        self.action_history = []
        self.failed_elements = set()
        self.step_count = 0
        self.device = None  # Will be set by select_action

        logger.info(f"🤖 AI Strategy initialized with mission: {mission}")

    def next_action(self, state):
        """
        Synchronous wrapper for select_action (required by base class)

        Note: This is not used in async web testing
        """
        return None
    
    async def select_action(self, state, device):
        """AI가 다음 액션을 추천"""
        
        self.step_count += 1
        logger.info(f"\n{'='*70}")
        logger.info(f"🤖 AI Step {self.step_count}: Analyzing screen...")
        logger.info(f"{'='*70}")
        
        # 1. 현재 화면 스크린샷 캡처
        screenshot_dir = "./reports/ai_screenshots"
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = f"{screenshot_dir}/step_{self.step_count:04d}.png"
        
        logger.info(f"📸 Capturing screenshot...")
        await device.capture_screenshot(screenshot_path)
        logger.info(f"   ✅ Screenshot saved: {screenshot_path}")
        
        # 2. 요소가 없으면 Back 또는 종료
        if not state.elements or len(state.elements) == 0:
            logger.warning("⚠️  No elements found, pressing BACK")
            return BackAction()
        
        # 3. Claude Code에게 분석 요청
        try:
            logger.info(f"🧠 Requesting AI analysis from Claude Code...")
            logger.info(f"   Mission: {self.mission}")
            logger.info(f"   Current URL: {state.url}")
            logger.info(f"   Available elements: {len(state.elements)}")
            
            recommendation = await self.claude.analyze_screen(
                screenshot_path=screenshot_path,
                elements=state.elements,
                mission=self.mission,
                history=self.action_history,
                current_url=state.url
            )
            
            logger.info(f"\n{'='*70}")
            logger.info(f"🎯 AI Recommendation:")
            logger.info(f"{'='*70}")
            logger.info(f"   Element ID: {recommendation.get('element_id')}")
            logger.info(f"   Position: ({recommendation['x']}, {recommendation['y']})")
            logger.info(f"   Reason: {recommendation['reason']}")
            logger.info(f"   Expected Effect: {recommendation.get('expected_effect', 'N/A')}")
            logger.info(f"   Confidence: {recommendation.get('confidence', 'N/A')}")
            logger.info(f"{'='*70}\n")
            
            # 4. 추천된 요소가 유효한지 확인
            element_id = recommendation.get('element_id')

            # element_id가 정수인지 확인
            if element_id is not None and isinstance(element_id, int) and 0 <= element_id < len(state.elements):
                selected_elem = state.elements[element_id]
                x = recommendation.get('x', selected_elem.center_x)
                y = recommendation.get('y', selected_elem.center_y)

                logger.info(f"✅ Using element #{element_id}: {selected_elem.text_content[:50] if selected_elem.text_content else 'No text'}")
            else:
                # 좌표만 주어진 경우 또는 element_id가 "back" 같은 문자열인 경우
                if element_id is not None and not isinstance(element_id, int):
                    logger.warning(f"⚠️  element_id is not an integer: {element_id}, using coordinates only")
                x = recommendation['x']
                y = recommendation['y']
                logger.info(f"✅ Using coordinates from AI: ({x}, {y})")
            
            action = TapAction(x=x, y=y)

            # AI 메타데이터 설정
            action.ai_reason = recommendation.get('reason')
            action.ai_expected_effect = recommendation.get('expected_effect', 'Page navigation or UI state change')
            action.ai_confidence = recommendation.get('confidence')

            # 5. 히스토리 저장
            self.action_history.append({
                'step': self.step_count,
                'action_type': 'tap',
                'x': x,
                'y': y,
                'reason': recommendation['reason'],
                'expected_effect': action.ai_expected_effect,
                'url': state.url,
                'element_id': element_id,
                'confidence': recommendation.get('confidence')
            })
            
            return action
            
        except Exception as e:
            logger.error(f"❌ AI analysis failed: {e}")
            logger.error(f"   Falling back to random selection")
            
            # AI 실패 시 fallback: 랜덤 선택
            import random
            if state.elements:
                selected = random.choice(state.elements)
                x = selected.center_x
                y = selected.center_y
                
                logger.info(f"🎲 Fallback: Random element at ({x}, {y})")
                
                action = TapAction(x=x, y=y)
                
                self.action_history.append({
                    'step': self.step_count,
                    'action_type': 'tap',
                    'x': x,
                    'y': y,
                    'reason': f'Fallback after AI error: {str(e)[:100]}',
                    'url': state.url,
                    'element_id': None
                })
                
                return action
            else:
                logger.warning("No elements available, pressing BACK")
                return BackAction()
    
    def get_name(self) -> str:
        return "ai"

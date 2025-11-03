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
        self.workspace_dir = workspace_dir or os.getcwd()
        self.claude = ClaudeCodeClient(self.workspace_dir)
        self.action_history = []
        self.failed_elements = set()
        self.step_count = 0
        self.device = None  # Will be set by select_action

        logger.info(f"🤖 AI Strategy initialized with mission: {mission}")
        logger.info(f"📁 Workspace directory: {self.workspace_dir}")

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
        
        # 1. 현재 화면 스크린샷 캡처 (workspace 내 screenshots 폴더에 저장)
        screenshot_dir = os.path.join(self.workspace_dir, "screenshots")
        os.makedirs(screenshot_dir, exist_ok=True)
        screenshot_path = os.path.join(screenshot_dir, f"step_{self.step_count:04d}.png")

        logger.info(f"📸 Capturing screenshot...")
        await device.capture_screenshot(screenshot_path)

        # 절대 경로로 변환
        screenshot_abs_path = os.path.abspath(screenshot_path)
        logger.info(f"   ✅ Screenshot saved: {screenshot_path}")
        logger.info(f"   📁 Absolute path: {screenshot_abs_path}")

        # 2. 요소 리스트 확인 (앱 모드에서는 빈 리스트도 OK - 이미지만 분석)
        elements_list = state.elements if state.elements else []
        if len(elements_list) == 0:
            logger.info("📱 App mode detected: Using image-only analysis (no XML parsing)")
        else:
            logger.info(f"🌐 Web mode detected: Using {len(elements_list)} elements from HTML")

        # 3. Claude Code에게 분석 요청
        try:
            logger.info(f"🧠 Requesting AI analysis from Claude Code...")
            logger.info(f"   Mission: {self.mission}")
            logger.info(f"   Current URL: {state.url}")
            logger.info(f"   Available elements: {len(elements_list)}")

            recommendation = await self.claude.analyze_screen(
                screenshot_path=screenshot_abs_path,
                elements=elements_list,
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

            # 웹 모드: element_id가 정수이고 유효한 범위 내인지 확인
            if element_id is not None and isinstance(element_id, int) and len(elements_list) > 0 and 0 <= element_id < len(elements_list):
                selected_elem = elements_list[element_id]
                x = recommendation.get('x', selected_elem.center_x)
                y = recommendation.get('y', selected_elem.center_y)

                logger.info(f"✅ Using element #{element_id}: {selected_elem.text_content[:50] if selected_elem.text_content else 'No text'}")
            else:
                # 앱 모드 또는 좌표만 주어진 경우
                if len(elements_list) == 0:
                    logger.info(f"📱 App mode: Using coordinates from visual analysis")
                elif element_id is not None and not isinstance(element_id, int):
                    logger.warning(f"⚠️  element_id is not an integer: {element_id}, using coordinates only")
                x = recommendation['x']
                y = recommendation['y']
                logger.info(f"✅ Tap coordinates: ({x}, {y})")

            # 🔍 권한 다이얼로그 자동 감지 및 수정
            # 권한 다이얼로그만 자동 보정 (시스템 필수 요소이므로)
            if len(elements_list) == 0 and "권한" in recommendation.get('reason', ''):
                logger.info(f"🔍 Permission dialog detected in reason, verifying with UI hierarchy...")
                corrected_coords = self._find_permission_button_coords(device)
                if corrected_coords:
                    x, y = corrected_coords
                    logger.info(f"✅ Corrected coordinates using UI hierarchy: ({x}, {y})")
                else:
                    logger.warning(f"⚠️  Could not find permission button in UI hierarchy, using AI coordinates")

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

            # AI 실패 시 fallback
            if len(elements_list) > 0:
                # 웹 모드: 랜덤 요소 선택
                logger.error(f"   Falling back to random element selection")
                import random
                selected = random.choice(elements_list)
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
                # 앱 모드: 요소 없을 때는 Back 액션
                logger.error(f"   App mode with no elements - pressing BACK")
                return BackAction()
    
    def get_name(self) -> str:
        return "ai"

    def _find_permission_button_coords(self, device) -> Optional[tuple]:
        """
        UI hierarchy에서 권한 다이얼로그의 확인 버튼 좌표를 찾습니다.

        Returns:
            (x, y) 튜플 또는 None
        """
        try:
            import xml.etree.ElementTree as ET
            import tempfile

            # UI hierarchy XML 파일 생성
            ui_xml = device.adb.shell("uiautomator dump /sdcard/ui_temp.xml")
            with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
                xml_content = device.adb.shell("cat /sdcard/ui_temp.xml")
                f.write(xml_content)
                temp_path = f.name

            # XML 파싱
            tree = ET.parse(temp_path)
            root = tree.getroot()

            # 확인 버튼 찾기 (여러 패턴 시도)
            button_patterns = [
                ".//node[@text='확인'][@clickable='true']",
                ".//node[@resource-id='com.coupang.mobile:id/confirm_button']",
                ".//node[@class='android.widget.Button'][@clickable='true']"
            ]

            for pattern in button_patterns:
                button = root.find(pattern)
                if button is not None:
                    bounds = button.get('bounds')
                    if bounds:
                        # bounds 형식: [left,top][right,bottom]
                        import re
                        match = re.match(r'\[(\d+),(\d+)\]\[(\d+),(\d+)\]', bounds)
                        if match:
                            left, top, right, bottom = map(int, match.groups())
                            center_x = (left + right) // 2
                            center_y = (top + bottom) // 2
                            logger.info(f"   Found button: {button.get('text', 'No text')} at bounds={bounds}")
                            logger.info(f"   Calculated center: ({center_x}, {center_y})")
                            return (center_x, center_y)

            return None

        except Exception as e:
            logger.error(f"   Failed to parse UI hierarchy: {e}")
            return None


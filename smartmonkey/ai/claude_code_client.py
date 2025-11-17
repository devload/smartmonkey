"""Claude Code CLI client for AI-driven testing"""

import subprocess
import json
import tempfile
import os
from typing import List, Dict, Any
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ClaudeCodeClient:
    """Claude Code CLI를 subprocess로 실행하여 AI 분석 수행"""
    
    def __init__(self, workspace_dir: str = None):
        """
        Initialize Claude Code client
        
        Args:
            workspace_dir: Claude Code workspace directory
        """
        self.workspace_dir = workspace_dir or os.getcwd()
        logger.info(f"Claude Code client initialized with workspace: {self.workspace_dir}")
    
    async def analyze_screen(
        self, 
        screenshot_path: str, 
        elements: List[Any], 
        mission: str, 
        history: List[Dict],
        current_url: str
    ) -> Dict[str, Any]:
        """
        Claude Code에게 화면 분석 요청
        
        Args:
            screenshot_path: 스크린샷 파일 경로
            elements: 클릭 가능한 요소 리스트
            mission: 달성할 미션
            history: 이전 액션 히스토리
            current_url: 현재 URL
            
        Returns:
            추천 액션 dict: {element_id, x, y, reason, confidence}
        """
        logger.info(f"🤖 Requesting AI analysis for mission: {mission}")
        
        # 1. 프롬프트 생성
        prompt = self._build_prompt(screenshot_path, elements, mission, history, current_url)
        prompt_file = self._create_temp_prompt_file(prompt)
        
        # 2. Claude Code CLI 실행
        try:
            logger.info(f"📝 Prompt file: {prompt_file}")
            logger.info(f"🚀 Executing Claude Code CLI...")
            
            # Claude CLI는 stdin으로 프롬프트를 받습니다
            with open(prompt_file, 'r', encoding='utf-8') as f:
                prompt_content = f.read()

            # subprocess 환경 설정: ANTHROPIC_API_KEY 제거하여 구독 인증 사용
            env = os.environ.copy()
            if 'ANTHROPIC_API_KEY' in env:
                del env['ANTHROPIC_API_KEY']
                logger.debug("Removed ANTHROPIC_API_KEY from subprocess env to use subscription auth")

            # PATH에 /opt/homebrew/bin 추가 (claude CLI 위치)
            if '/opt/homebrew/bin' not in env.get('PATH', ''):
                env['PATH'] = f"/opt/homebrew/bin:{env.get('PATH', '')}"

            result = subprocess.run(
                ['claude', '-p'],  # -p for non-interactive (chat 명령어 불필요)
                input=prompt_content,
                capture_output=True,
                text=True,
                timeout=60,  # 60초 타임아웃
                cwd=self.workspace_dir,
                env=env  # 수정된 환경 변수 사용
            )
            
            if result.returncode != 0:
                logger.error(f"Claude Code CLI failed: {result.stderr}")
                raise RuntimeError(f"Claude Code CLI error: {result.stderr}")
            
            logger.info(f"✅ Claude Code response received")
            logger.debug(f"Raw response: {result.stdout[:500]}...")
            
            # 3. 응답 파싱
            response = self._parse_response(result.stdout)
            logger.info(f"✅ Parsed response: element_id={response.get('element_id')}, confidence={response.get('confidence')}")
            
            return response
            
        except subprocess.TimeoutExpired:
            logger.error("Claude Code CLI timeout (60s)")
            raise RuntimeError("Claude Code CLI timeout")
        except Exception as e:
            logger.error(f"Claude Code CLI error: {e}")
            raise
        finally:
            # 임시 파일 정리
            if os.path.exists(prompt_file):
                os.remove(prompt_file)
                logger.debug(f"Cleaned up prompt file: {prompt_file}")
    
    def _build_prompt(
        self,
        screenshot_path: str,
        elements: List[Any],
        mission: str,
        history: List[Dict],
        current_url: str
    ) -> str:
        """AI에게 전달할 프롬프트 생성"""

        # 앱 모드 vs 웹 모드 감지
        is_app_mode = not elements or len(elements) == 0

        # 히스토리 포맷
        history_text = "\n".join([
            f"- Step {i+1}: {action.get('action_type', 'unknown')} at ({action.get('x', 'N/A')}, {action.get('y', 'N/A')}) - {action.get('reason', 'N/A')}"
            for i, action in enumerate(history[-5:])  # 최근 5개만
        ])

        # 앱 모드 - 이미지만 사용
        if is_app_mode:
            return self._build_app_prompt(screenshot_path, mission, history_text, current_url)

        # 웹 모드 - 기존 방식 (요소 리스트 포함)
        return self._build_web_prompt(screenshot_path, elements, mission, history_text, current_url)

    def _build_app_prompt(
        self,
        screenshot_path: str,
        mission: str,
        history_text: str,
        current_url: str
    ) -> str:
        """앱 모드 프롬프트 (이미지만 사용)"""

        prompt = f"""🎯 **미션**: {mission}

📍 **현재 화면**: Android 앱

📸 **스크린샷**: {screenshot_path}
(위 경로의 스크린샷을 확인해주세요)

📜 **이전 액션 히스토리** (최근 5개):
{history_text if history_text else "(없음 - 첫 액션)"}

---

**당신의 역할**: 위 스크린샷을 보고, 미션을 달성하기 위해 다음으로 어떤 UI 요소를 클릭해야 할지 판단해주세요.

**중요 규칙**:
1. 스크린샷에서 시각적으로 보이는 UI 요소를 분석하세요
2. 이미 클릭한 위치는 피하세요 (히스토리 참고)
3. 미션과 가장 관련 있는 UI 요소를 선택하세요
4. 상단 상태바/시스템 UI (y < 100)는 클릭하지 마세요
5. 네비게이션 버튼, 텍스트, 이미지, 아이콘 등 클릭 가능한 모든 요소를 고려하세요

**응답 형식** (반드시 이 JSON 형식으로만 응답):
```json
{{
  "element_id": null,
  "x": 540,
  "y": 1200,
  "reason": "왜 이 위치를 선택했는지 구체적으로 설명 (한글, 1-2문장)",
  "expected_effect": "이 액션의 기대 효과 (예: 상품 상세 페이지로 이동, 카테고리 열림, 검색 시작 등, 한글, 1문장)",
  "confidence": 0.9
}}
```

**주의**:
- element_id는 null로 설정하세요 (앱 모드에서는 사용 안 함)
- x, y는 클릭할 화면 좌표입니다 (픽셀 단위)
- reason은 선택 이유를 구체적으로 설명 (1-2문장)
- expected_effect는 클릭 후 예상되는 결과를 명확하게 기술 (1문장)
- confidence는 0.0~1.0 사이 값입니다

**지금 추천해주세요!**
"""
        return prompt

    def _build_web_prompt(
        self,
        screenshot_path: str,
        elements: List[Any],
        mission: str,
        history_text: str,
        current_url: str
    ) -> str:
        """웹 모드 프롬프트 (요소 리스트 포함)"""

        # 요소 정보를 읽기 쉽게 포맷
        element_info = []
        for i, elem in enumerate(elements[:30]):  # 최대 30개만
            element_info.append({
                "id": i,
                "text": (elem.text_content[:80] if elem.text_content else "").strip(),
                "type": elem.tag_name,
                "position": f"({elem.center_x}, {elem.center_y})"
            })

        # 워크스페이스의 CLAUDE.md에서 UI 가이드 읽기
        ui_guide = self._load_ui_guide_from_claude_md()

        prompt = f"""🎯 **미션**: {mission}

📍 **현재 URL**: {current_url}

📸 **스크린샷**: {screenshot_path}
(위 경로의 스크린샷을 확인해주세요)

🔍 **클릭 가능한 요소들** (총 {len(elements)}개 중 상위 {len(element_info)}개):
```json
{json.dumps(element_info, indent=2, ensure_ascii=False)}
```

📜 **이전 액션 히스토리** (최근 5개):
{history_text if history_text else "(없음 - 첫 액션)"}

---

**당신의 역할**: 위 스크린샷과 요소 정보를 보고, 미션을 달성하기 위해 다음으로 어떤 액션을 취해야 할지 추천해주세요.

{ui_guide}

**중요 규칙**:
1. 이미 클릭한 요소는 피하세요 (히스토리 참고)
2. 미션과 가장 관련 있는 요소를 선택하세요
3. 스크린샷에서 시각적으로 확인 가능한 요소를 우선하세요
4. URL 바 영역(y < 150)은 클릭하지 마세요
5. 광고나 프로모션보다 실제 콘텐츠를 우선하세요
6. 위 웹사이트 가이드를 참고하여 UI 요소의 기능을 이해하세요
7. 미션 달성을 위한 최적의 경로를 선택하세요

**응답 형식** (반드시 이 JSON 형식으로만 응답):
```json
{{
  "element_id": 3,
  "x": 540,
  "y": 1200,
  "reason": "왜 이 요소를 선택했는지 구체적으로 설명 (한글, 1-2문장)",
  "expected_effect": "이 액션의 기대 효과 (예: 상품 상세 페이지로 이동, 검색 결과 표시, 카테고리 목록 열림 등, 한글, 1문장)",
  "confidence": 0.9
}}
```

**주의**:
- element_id는 위 요소 리스트의 id 값입니다 (0부터 시작)
- x, y는 해당 요소의 position 값을 사용하세요
- reason은 선택 이유를 구체적으로 설명 (1-2문장)
- expected_effect는 클릭 후 예상되는 결과를 명확하게 기술 (1문장)
- confidence는 0.0~1.0 사이 값입니다

**지금 추천해주세요!**
"""
        return prompt
    
    def _load_ui_guide_from_claude_md(self) -> str:
        """워크스페이스의 CLAUDE.md에서 UI 가이드 읽기"""
        claude_md_path = os.path.join(self.workspace_dir, 'CLAUDE.md')

        if not os.path.exists(claude_md_path):
            logger.warning(f"CLAUDE.md not found at {claude_md_path}")
            return "**웹사이트 UI 가이드**: (없음 - CLAUDE.md 파일을 생성하세요)"

        try:
            with open(claude_md_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # "웹사이트 UI 가이드" 섹션 추출
            if '## 🌐' in content or '웹사이트 UI 가이드' in content:
                # UI 가이드 섹션 찾기
                lines = content.split('\n')
                ui_section = []
                in_ui_section = False

                for line in lines:
                    if '웹사이트 UI 가이드' in line or '주요 UI 요소' in line:
                        in_ui_section = True
                        ui_section.append(line)
                    elif in_ui_section:
                        # 다음 주요 섹션(##)을 만나면 종료
                        if line.startswith('## ') and '🤖' not in line:
                            break
                        ui_section.append(line)

                if ui_section:
                    return '\n'.join(ui_section)

            logger.warning("UI 가이드 섹션을 CLAUDE.md에서 찾을 수 없습니다")
            return "**웹사이트 UI 가이드**: (CLAUDE.md에 UI 가이드 섹션 추가 필요)"

        except Exception as e:
            logger.error(f"CLAUDE.md 읽기 실패: {e}")
            return "**웹사이트 UI 가이드**: (로드 실패)"

    def _create_temp_prompt_file(self, prompt: str) -> str:
        """임시 프롬프트 파일 생성"""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.md',
            delete=False,
            encoding='utf-8',
            dir='/tmp'
        ) as f:
            f.write(prompt)
            return f.name
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Claude Code 응답에서 JSON 추출"""
        import re

        logger.debug(f"Parsing response (length: {len(response_text)})")

        # JSON 블록 찾기 (```json ... ``` 또는 {...})
        json_match = re.search(
            r'```json\s*(\{.*?\})\s*```',
            response_text,
            re.DOTALL
        )

        if json_match:
            json_str = json_match.group(1)
            logger.debug("Found JSON in markdown code block")
        else:
            # 순수 JSON 찾기 (element_id 또는 x, y 포함)
            json_match = re.search(r'\{[^{}]*"x"[^{}]*"y"[^{}]*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                logger.debug("Found JSON without markdown")
            else:
                logger.error(f"No JSON found in response:\n{response_text[:500]}")
                raise ValueError(f"AI 응답에서 JSON을 찾을 수 없습니다:\n{response_text[:500]}...")

        try:
            parsed = json.loads(json_str)

            # 필수 필드 검증 (element_id는 optional - 앱 모드에서는 null)
            required_fields = ['x', 'y', 'reason']
            missing = [f for f in required_fields if f not in parsed]
            if missing:
                raise ValueError(f"Missing required fields: {missing}")

            return parsed

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {e}\nJSON string: {json_str}")
            raise ValueError(f"JSON 파싱 실패: {e}\n원본: {json_str}")

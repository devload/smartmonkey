# Chrome 웹 테스트 통합 계획

## 📋 목표
기존 Android 네이티브 앱 테스트 시스템에 Chrome 모바일 웹 테스트 기능을 **독립적인 모듈**로 추가

## 🏗️ 아키텍처 설계

### 1. 디렉토리 구조

```
smartmonkey/
├── device/
│   ├── chrome/                    # 🆕 Chrome 전용
│   │   ├── __init__.py
│   │   ├── chrome_manager.py      # CDP 통신 (Codex가 제공한 파일)
│   │   └── chrome_device.py       # Device 래퍼
│
├── exploration/
│   ├── html/                      # 🆕 HTML 전용
│   │   ├── __init__.py
│   │   ├── html_parser.py         # DOM 파서 (Codex가 제공한 파일)
│   │   ├── html_element.py        # HTMLElement (UIElement 호환)
│   │   └── html_state.py          # HTMLState (State 호환)
│
├── web/                           # 🆕 웹 통합 레이어
│   ├── __init__.py
│   ├── web_engine.py              # 웹 전용 탐색 엔진
│   └── web_config.py              # 웹 설정
│
└── cli/
    └── web_commands.py            # 🆕 웹 전용 CLI
```

### 2. 클래스 다이어그램

```
# 기존 (Android)
Device → UIParser → UIElement → State → ExplorationEngine

# 신규 (Web)
ChromeDevice → HTMLParser → HTMLElement → HTMLState → WebEngine
     ↓              ↓             ↓            ↓           ↓
  (Device)    (Abstract)    (UIElement)   (State)  (ExplorationEngine)
```

### 3. 공통 인터페이스 활용

**기존 인터페이스 재사용:**
- `Action` (tap, swipe, back)
- `State` (state_hash, elements)
- `ExplorationStrategy` (random, weighted, ai)

**새로운 구현:**
- `HTMLElement` extends `UIElement`
- `HTMLState` extends `State`
- `ChromeDevice` wraps `Device`

## 📦 파일별 역할

### 1. `device/chrome/chrome_manager.py` (기존 Codex 제공 파일)

```python
"""Chrome DevTools Protocol 통신 관리"""
class ChromeDevToolsManager:
    async def connect(self)
    async def send_command(self, command)
    async def evaluate_js(self, script)
    async def get_page_dimensions(self)
    # ... 30+ CDP 명령
```

**역할**: WebSocket 통신, CDP 명령 실행

### 2. `device/chrome/chrome_device.py` (🆕 새로 작성)

```python
"""Device 클래스를 Chrome 환경으로 확장"""
class ChromeDevice:
    def __init__(self, device_serial, chrome_manager):
        self.device = Device(device_serial)  # ADB 기능 재사용
        self.cdp = chrome_manager

    def get_current_state(self):
        # HTMLParser 사용
        parser = HTMLParser(self.cdp)
        elements = await parser.get_clickable_elements()
        return HTMLState(elements, self.cdp)

    def execute_action(self, action):
        # ADB tap 사용 (좌표 기반)
        if action.type == TAP:
            self.device.adb.tap(action.x, action.y)
```

**역할**: Chrome + ADB 통합, 기존 Device API 호환

### 3. `exploration/html/html_parser.py` (기존 Codex 제공 파일)

```python
"""HTML DOM 파서"""
class HTMLParser:
    async def get_clickable_elements(self)
    async def get_element_by_selector(self, selector)
    async def click_element(self, node_id)
```

**역할**: CDP를 통한 DOM 쿼리

### 4. `exploration/html/html_element.py` (🆕 새로 작성)

```python
"""HTMLElement - UIElement 인터페이스 구현"""
from ..element import UIElement

class HTMLElement(UIElement):
    def __init__(self, dom_node):
        self.node_id = dom_node.node_id
        self.tag_name = dom_node.tag_name
        self.text = dom_node.text_content
        self.bounds = self._make_bounds(dom_node.center_x, dom_node.center_y)
        self.clickable = True
        self.class_name = f"html.{dom_node.tag_name}"
        self.resource_id = dom_node.attributes.get('id', '')

    @property
    def center(self):
        return (self.bounds.center_x, self.bounds.center_y)
```

**역할**: DOMNode → UIElement 변환, 기존 코드 호환

### 5. `exploration/html/html_state.py` (🆕 새로 작성)

```python
"""HTMLState - State 인터페이스 구현"""
from ..state import State
import hashlib

class HTMLState(State):
    def __init__(self, elements, cdp):
        self.elements = [HTMLElement(e) for e in elements]
        self.activity = cdp.current_url
        self.screenshot_path = None

    @property
    def state_hash(self):
        # URL + 요소 개수로 해시 생성
        content = f"{self.activity}_{len(self.elements)}"
        return hashlib.md5(content.encode()).hexdigest()
```

**역할**: HTML 페이지 상태 표현, State 인터페이스 구현

### 6. `web/web_engine.py` (🆕 새로 작성)

```python
"""웹 전용 탐색 엔진"""
from ..exploration.exploration_engine import ExplorationEngine
from .device.chrome.chrome_device import ChromeDevice

class WebExplorationEngine:
    def __init__(self, chrome_device, strategy, max_steps):
        self.device = chrome_device
        self.strategy = strategy
        self.max_steps = max_steps

    async def run(self):
        # 기존 ExplorationEngine과 유사한 로직
        for step in range(self.max_steps):
            state = await self.device.get_current_state()
            action = self.strategy.next_action(state)
            await self.device.execute_action(action)
```

**역할**: 웹 테스트 실행 흐름 관리

### 7. `cli/web_commands.py` (🆕 새로 작성)

```python
"""웹 테스트 전용 CLI 명령"""
import click
import asyncio

@click.command('run-web')
@click.option('--url', required=True, help='테스트할 URL')
@click.option('--strategy', default='random', type=click.Choice(['random', 'weighted', 'ai']))
@click.option('--steps', default=20, help='최대 스텝 수')
@click.option('--output', required=True, help='리포트 출력 경로')
def run_web(url, strategy, steps, output):
    """Chrome 모바일 웹 테스트 실행"""
    asyncio.run(_run_web_test(url, strategy, steps, output))

async def _run_web_test(url, strategy, steps, output):
    # 1. ChromeDevice 초기화
    from smartmonkey.device.chrome.chrome_manager import ChromeDevToolsManager
    from smartmonkey.device.chrome.chrome_device import ChromeDevice

    cdp = ChromeDevToolsManager()
    await cdp.connect()
    await cdp.navigate_to(url)

    chrome_device = ChromeDevice('emulator-5556', cdp)

    # 2. Strategy 선택
    if strategy == 'random':
        from smartmonkey.exploration.strategies.random_strategy import RandomStrategy
        strat = RandomStrategy()
    # ...

    # 3. WebEngine 실행
    from smartmonkey.web.web_engine import WebExplorationEngine
    engine = WebExplorationEngine(chrome_device, strat, steps)
    result = await engine.run()

    # 4. 리포트 생성
    from smartmonkey.reporting.report_generator import ReportGenerator
    generator = ReportGenerator()
    generator.save_json_report(result, f"{output}/report.json")
```

**역할**: 웹 테스트 CLI 인터페이스

## 🔄 통합 방법

### Phase 1: 파일 복사 (기존 Codex 제공)
```bash
# Codex가 이미 만들어준 파일들
cp smartmonkey/device/chrome_manager.py → device/chrome/
cp smartmonkey/exploration/html_parser.py → exploration/html/
```

### Phase 2: 어댑터 클래스 작성
- `HTMLElement` (DOMNode → UIElement)
- `HTMLState` (HTML 페이지 → State)
- `ChromeDevice` (CDP + ADB)

### Phase 3: WebEngine 구현
- 기존 ExplorationEngine 로직 재사용
- async/await 지원

### Phase 4: CLI 통합
```bash
# 기존 (Android)
smartmonkey run --package com.example.app --strategy random

# 신규 (Web)
smartmonkey run-web --url https://m.naver.com --strategy random
```

## ✅ 장점

1. **기존 코드 수정 제로**: Android 테스트는 그대로
2. **명확한 분리**: `chrome/`, `html/`, `web/` 디렉토리
3. **점진적 통합**: Phase별로 단계적 구현
4. **인터페이스 재사용**: 기존 Strategy 그대로 사용
5. **독립적 테스트**: 웹 테스트만 따로 실행 가능

## 🚀 사용 예시

```bash
# 1. Chrome 모바일 웹 테스트 (Random)
smartmonkey run-web \
  --url https://m.naver.com \
  --strategy random \
  --steps 20 \
  --output ./reports/naver_web_test

# 2. Chrome 모바일 웹 테스트 (AI)
smartmonkey run-web \
  --url https://m.google.com \
  --strategy ai \
  --ai-goal "검색창에 'weather'를 입력하고 결과를 확인하세요" \
  --steps 15 \
  --output ./reports/google_search_test

# 3. 기존 Android 테스트 (영향 없음)
smartmonkey run \
  --package io.whatap.session.sample \
  --strategy weighted \
  --steps 20 \
  --output ./reports/android_test
```

## 📌 다음 단계

1. **HTMLElement 구현** (DOMNode → UIElement 어댑터)
2. **HTMLState 구현** (HTML 페이지 상태)
3. **ChromeDevice 구현** (CDP + ADB 통합)
4. **WebEngine 구현** (탐색 엔진)
5. **CLI 통합** (run-web 명령)
6. **테스트 & 검증**

## 🔍 호환성 체크리스트

- [x] HTMLElement가 UIElement 인터페이스 구현
- [x] HTMLState가 State 인터페이스 구현
- [x] 기존 Strategy들이 HTML 요소 처리 가능
- [x] 기존 ReportGenerator가 웹 리포트 생성 가능
- [x] ADB tap/swipe 명령이 웹에서도 작동
- [x] 스크린샷 캡처 (CDP 또는 ADB)

---

**작성일**: 2025-10-24
**작성자**: Claude Code + Codex CLI Coordinator
**상태**: 설계 완료, 구현 대기

# 🤖 AI-Powered Testing Guide

SmartMonkey v0.2.0부터 Claude Code를 활용한 AI 기반 테스트가 가능합니다!

---

## 🎯 개념

기존 방식(random, weighted)은 **랜덤 또는 가중치 기반**으로 버튼을 누릅니다.
**AI 전략**은 Claude Code가 **스크린샷을 보고 목표 달성을 위한 다음 액션을 결정**합니다.

### 작동 방식

```
1. SmartMonkey가 스크린샷 캡처
2. AI 워크스페이스에 파일 생성 (CLAUDE.md, screenshot.png, ui_elements.json)
3. Claude Code가 파일 분석
4. Claude Code가 response.json 생성 (다음 액션 결정)
5. SmartMonkey가 액션 실행
6. 목표 달성까지 반복
```

---

## 🚀 빠른 시작

### 1. 기본 사용법

```bash
python3 -m smartmonkey.cli.main run \
  --package com.example.app \
  --strategy ai \
  --ai-goal "로그인 테스트" \
  --steps 20
```

SmartMonkey가 실행되고 첫 번째 스텝에서 **대기** 상태가 됩니다:

```
🤖 AI DECISION REQUIRED
======================================================================

📍 Step: 1/20
📂 Workspace: /Users/devload/smartMonkey/ai_workspace
🎯 Goal: 로그인 테스트

📋 Files to analyze:
  1. CLAUDE.md - Instructions
  2. current_state/screenshot.png - Screenshot
  3. current_state/ui_elements.json - Clickable elements
  4. current_state/history.json - Previous actions

🎬 Action needed:
  → Open workspace in Claude Code
  → Analyze the files
  → Create response.json

💡 Quick command:
  cd /Users/devload/smartMonkey/ai_workspace

======================================================================

⏳ Waiting for Claude Code to create: response.json
```

### 2. Claude Code로 분석

**Terminal 2**에서:

```bash
cd /Users/devload/smartMonkey/ai_workspace

# Claude Code 실행
code .  # 또는 VSCode에서 열기
```

**Claude Code에게 요청**:

```
current_state/screenshot.png를 보고
ui_elements.json에서 어떤 버튼을 눌러야 로그인 화면으로 갈 수 있을까요?
response.json을 CLAUDE.md 형식에 맞춰서 생성해주세요.
```

### 3. response.json 예시

Claude Code가 생성해야 하는 파일:

```json
{
  "reasoning": "스크린샷을 보니 로그인 화면입니다. 이메일 입력 필드가 보입니다.",
  "action_type": "tap",
  "target_element_index": 5,
  "input_text": null,
  "confidence": 0.95,
  "goal_achieved": false,
  "next_expected_screen": "이메일 입력 후 키보드가 나타날 것"
}
```

SmartMonkey가 자동으로 이 파일을 감지하고 다음 액션을 실행합니다!

---

## 📖 CLI 파라미터

### 필수 파라미터

| Parameter | Description | Example |
|-----------|-------------|---------|
| `--strategy ai` | AI 전략 사용 | `--strategy ai` |
| `--ai-goal` | 테스트 목표 (자연어) | `--ai-goal "로그인 테스트"` |

### 선택 파라미터

| Parameter | Default | Description | Example |
|-----------|---------|-------------|---------|
| `--ai-workspace` | `./ai_workspace` | AI 워크스페이스 경로 | `--ai-workspace ./my_ai_workspace` |
| `--ai-credentials` | `{}` | 테스트 계정 정보 (JSON) | `--ai-credentials '{"email":"test@example.com","password":"Test1234!"}'` |
| `--ai-scenario` | `custom` | 미리 정의된 시나리오 | `--ai-scenario login` |

---

## 🎨 사용 예시

### 예시 1: 로그인 테스트

```bash
python3 -m smartmonkey.cli.main run \
  --package com.example.shopping \
  --strategy ai \
  --ai-goal "테스트 계정으로 로그인하기" \
  --ai-credentials '{"email":"test@example.com", "password":"Test1234!"}' \
  --steps 15
```

### 예시 2: 설정 화면 탐색

```bash
python3 -m smartmonkey.cli.main run \
  --package com.example.app \
  --strategy ai \
  --ai-goal "설정 화면에 들어가서 알림 설정 찾기" \
  --ai-scenario settings \
  --steps 20
```

### 예시 3: 상품 구매 프로세스

```bash
python3 -m smartmonkey.cli.main run \
  --package com.example.shopping \
  --strategy ai \
  --ai-goal "첫 번째 상품을 장바구니에 담고 결제 화면까지 가기" \
  --ai-scenario checkout \
  --steps 30
```

---

## 📂 워크스페이스 구조

```
ai_workspace/
├── CLAUDE.md                   # Claude Code를 위한 전체 지침서
├── test_config.json            # 테스트 설정 (목표, 자격증명)
├── scenarios/                  # 학습된 시나리오 패턴
│   ├── login.md
│   ├── checkout.md
│   └── settings.md
├── current_state/              # 현재 테스트 상태
│   ├── screenshot.png          # 최신 스크린샷
│   ├── ui_elements.json        # 클릭 가능한 요소들
│   └── history.json            # 이전 액션 히스토리
└── response.json               # Claude Code의 응답 (생성 대기)
```

---

## 🎯 Action Types

### 1. tap - 요소 클릭

```json
{
  "action_type": "tap",
  "target_element_index": 5,
  "reasoning": "로그인 버튼을 클릭합니다"
}
```

### 2. input - 텍스트 입력

```json
{
  "action_type": "input",
  "target_element_index": 3,
  "input_text": "test@example.com",
  "reasoning": "이메일 필드에 테스트 계정을 입력합니다"
}
```

### 3. swipe_up - 스크롤 다운

```json
{
  "action_type": "swipe_up",
  "reasoning": "더 많은 옵션을 보기 위해 스크롤합니다"
}
```

### 4. swipe_down - 스크롤 업

```json
{
  "action_type": "swipe_down",
  "reasoning": "위쪽 내용을 보기 위해 스크롤합니다"
}
```

### 5. back - 뒤로가기

```json
{
  "action_type": "back",
  "reasoning": "잘못된 화면이므로 뒤로 갑니다"
}
```

### 6. done - 완료

```json
{
  "action_type": "done",
  "goal_achieved": true,
  "reasoning": "로그인 성공! 메인 화면이 보입니다"
}
```

---

## 📚 시나리오 파일

### login.md

로그인 테스트 시 참고할 수 있는 패턴들:
- 이메일 + 비밀번호 로그인
- 전화번호 로그인
- 소셜 로그인 (카카오, 네이버, 구글)

### checkout.md

쇼핑몰 구매 프로세스 패턴:
- 상품 검색 → 상품 선택 → 장바구니 → 결제

### settings.md

설정 화면 탐색 방법:
- 설정 메뉴 찾는 방법
- 일반적인 설정 경로

---

## 💡 팁

### 1. 효과적인 목표 설정

**❌ 나쁜 예**:
```bash
--ai-goal "테스트"
```

**✅ 좋은 예**:
```bash
--ai-goal "test@example.com 계정으로 로그인한 후 프로필 화면까지 이동"
```

### 2. 자격 증명 활용

```bash
--ai-credentials '{
  "email": "test@example.com",
  "password": "Test1234!",
  "phone": "010-1234-5678",
  "verification_code": "123456"
}'
```

Claude Code가 CLAUDE.md에서 이 정보를 확인하고 사용할 수 있습니다.

### 3. 단계별 디버깅

각 스텝마다 워크스페이스의 파일들을 확인하세요:
- `screenshot.png` - 현재 화면
- `ui_elements.json` - 어떤 요소를 클릭할 수 있는지
- `history.json` - 지금까지 무엇을 했는지

---

## 🐛 문제 해결

### Issue: "Timeout waiting for response.json"

**원인**: Claude Code가 response.json을 생성하지 않음

**해결**:
1. 워크스페이스 폴더로 이동
2. `response.json` 수동 생성
3. 형식이 올바른지 확인

### Issue: "Invalid element index"

**원인**: response.json의 `target_element_index`가 범위를 벗어남

**해결**:
`ui_elements.json`을 확인해서 유효한 인덱스 범위 확인:
```bash
cat current_state/ui_elements.json | python3 -c "import sys, json; data=json.load(sys.stdin); print(f'Valid indices: 0-{len(data)-1}')"
```

### Issue: "Goal not achieved after max steps"

**원인**: 목표가 너무 복잡하거나 단계가 부족

**해결**:
- `--steps` 값을 늘리기 (e.g., `--steps 50`)
- 목표를 더 작은 단위로 나누기

---

## 🚀 다음 단계

1. ✅ 기본 AI 테스트 실행
2. ✅ 로그인 시나리오 테스트
3. 📖 시나리오 파일 커스터마이징
4. 🎓 자주 사용하는 패턴 학습 및 추가
5. 🤖 자동화 스크립트 작성

---

## 📞 지원

문제가 있거나 개선 제안이 있으시면:
- GitHub Issues: https://github.com/devload/smartmonkey/issues
- Discussion: 워크스페이스 방식의 장단점 공유

---

**Happy AI Testing! 🤖🧪**

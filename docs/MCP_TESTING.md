# SmartMonkey MCP 테스트 가이드

## ⚠️ 사전 요구사항

**Python 3.10 이상** 필요 (현재: Python 3.9.6)

### Python 업그레이드 방법

#### 방법 1: Homebrew (권장)
```bash
# Python 3.12 설치
brew install python@3.12

# 설치 확인
python3.12 --version

# 가상환경 생성 (권장)
python3.12 -m venv ~/.venv/smartmonkey-mcp
source ~/.venv/smartmonkey-mcp/bin/activate

# MCP SDK 설치
pip install mcp
```

#### 방법 2: pyenv
```bash
# pyenv 설치 (없다면)
brew install pyenv

# Python 3.12 설치
pyenv install 3.12.0
pyenv global 3.12.0

# 설치 확인
python3 --version

# MCP SDK 설치
pip install mcp
```

---

## 🧪 MCP 서버 테스트 방법

### 테스트 1: 서버 실행 확인

**가장 간단한 테스트:**
```bash
# SmartMonkey 디렉토리에서
cd /Users/devload/smartMonkey

# MCP 서버 실행 (stdio 모드)
python3 -m smartmonkey.mcp.server
```

**정상 실행 시:**
- 서버가 시작되고 stdin/stdout을 통해 통신 대기
- 아무 출력 없이 대기 상태 = 정상
- Ctrl+C로 종료

**오류 발생 시:**
- Import 오류: Python 버전 또는 mcp 미설치
- 기타 오류: 코드 문제

---

### 테스트 2: MCP Inspector (추천)

**MCP Inspector는 MCP 서버를 시각적으로 테스트하는 도구입니다.**

```bash
# MCP Inspector 설치
npm install -g @modelcontextprotocol/inspector

# SmartMonkey MCP 서버 테스트
mcp-inspector python3 -m smartmonkey.mcp.server
```

**Inspector에서 확인할 것:**
1. **Tools 탭**: 4개 tool 표시 확인
   - `list_devices`
   - `run_ai_test`
   - `run_mobile_test`
   - `run_web_test`

2. **각 Tool 실행:**
   - `list_devices` 클릭 → 연결된 디바이스 목록
   - `run_ai_test` 클릭 → mission 입력 후 실행 → test_id 반환
   - 결과 확인: `./reports/<test_id>/` 디렉토리

---

### 테스트 3: Claude Desktop 연동 (실전)

**1. Claude Desktop Config 설정:**
```bash
# macOS
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**2. SmartMonkey 서버 추가:**
```json
{
  "mcpServers": {
    "smartmonkey": {
      "command": "python3.12",
      "args": ["-m", "smartmonkey.mcp.server"],
      "env": {
        "PYTHONPATH": "/Users/devload/smartMonkey"
      }
    }
  }
}
```

**⚠️ 주의:** `python3.12`는 업그레이드한 Python 버전으로 변경

**3. Claude Desktop 재시작:**
```bash
# Claude Desktop 완전 종료 후 재시작
killall Claude
open -a Claude
```

**4. 테스트:**
```
User: "What SmartMonkey tools do you have?"
Claude: [Should list 4 tools]

User: "List my Android devices"
Claude: [Calls list_devices, shows connected devices]

User: "Test Coupang app with mission: browse products"
Claude: [Calls run_ai_test, returns test_id]
```

---

### 테스트 4: 수동 JSON-RPC 테스트 (고급)

**직접 JSON-RPC 메시지 전송:**
```bash
cd /Users/devload/smartMonkey

# 서버 실행 후 stdin으로 입력
python3 -m smartmonkey.mcp.server

# 입력 (JSON-RPC 형식):
{"jsonrpc":"2.0","method":"tools/list","id":1}

# 예상 출력: 4개 tool 정의 반환
```

---

## 📊 테스트 체크리스트

### 기본 동작
- [ ] Python 3.10+ 설치 확인
- [ ] MCP SDK 설치 확인 (`pip list | grep mcp`)
- [ ] 서버 실행 성공 (`python3 -m smartmonkey.mcp.server`)

### Inspector 테스트
- [ ] MCP Inspector 설치
- [ ] Inspector로 서버 연결
- [ ] 4개 tool 표시 확인
- [ ] `list_devices` 실행 → 디바이스 목록 확인
- [ ] `run_ai_test` 실행 → test_id 반환 확인
- [ ] `./reports/` 디렉토리에 결과 생성 확인

### Claude Desktop 테스트
- [ ] `claude_desktop_config.json` 설정
- [ ] Claude Desktop 재시작
- [ ] SmartMonkey tools 인식 확인
- [ ] Natural language 명령 테스트
- [ ] 실제 테스트 실행 확인

---

## 🐛 트러블슈팅

### 문제: ModuleNotFoundError: No module named 'mcp'
**원인:** MCP SDK 미설치 또는 잘못된 Python 환경
**해결:**
```bash
pip install mcp
# 또는 가상환경에서
source ~/.venv/smartmonkey-mcp/bin/activate
pip install mcp
```

### 문제: ERROR: Requires-Python >=3.10
**원인:** Python 버전 3.9 이하
**해결:** Python 3.10+ 업그레이드 (위 방법 참고)

### 문제: Claude Desktop에서 tools 안 보임
**원인:** Config 설정 오류 또는 서버 시작 실패
**해결:**
1. Config 파일 경로 확인
2. Python 경로 확인 (`which python3.12`)
3. PYTHONPATH 확인
4. Claude Desktop 로그 확인

### 문제: Test 실행 후 결과 없음
**원인:** Background execution 중이거나 권한 문제
**해결:**
1. `./reports/` 디렉토리 확인
2. 테스트 완료 대기 (몇 분 소요)
3. ADB 연결 확인 (`adb devices`)

---

## 💡 빠른 시작 (Quick Start)

```bash
# 1. Python 업그레이드
brew install python@3.12

# 2. 가상환경 생성
python3.12 -m venv ~/.venv/smartmonkey-mcp
source ~/.venv/smartmonkey-mcp/bin/activate

# 3. MCP SDK 설치
pip install mcp

# 4. 서버 테스트
cd /Users/devload/smartMonkey
python3 -m smartmonkey.mcp.server
# Ctrl+C로 종료

# 5. Inspector 테스트 (optional)
npm install -g @modelcontextprotocol/inspector
mcp-inspector python3 -m smartmonkey.mcp.server

# 6. Claude Desktop 설정
# Config 파일 수정 후 Claude 재시작
```

---

## 📚 참고 자료

- MCP 공식 문서: https://modelcontextprotocol.io
- SmartMonkey MCP Setup: `/Users/devload/smartMonkey/docs/MCP_SETUP.md`
- Python 설치: https://www.python.org/downloads/
- MCP Inspector: https://github.com/modelcontextprotocol/inspector

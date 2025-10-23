# SmartMonkey - Claude Development Environment

## 📍 Project Overview

**Project Name**: SmartMonkey
**Workspace Path**: `/Users/devload/smartMonkey`
**Created Date**: 2025-10-23

## 🎯 Project Mission

이 프로젝트는 **Android 앱 자동화 테스트를 위한 SmartMonkey 도구**를 개발하는 것을 목표로 합니다.

### 주요 목표
- Android 앱의 자동화된 UI 테스트 수행
- 지능형 탐색 및 테스트 시나리오 생성
- 버그 및 크래시 자동 감지
- 테스트 결과 리포팅

## 📂 Key Directories & Files

### Workspace Structure
```
/Users/devload/smartMonkey/
├── CLAUDE.md                    # 이 문서 (프로젝트 설정 및 가이드)
├── pyproject.toml               # 프로젝트 메타데이터 및 의존성
├── requirements.txt             # Python 의존성
│
├── smartmonkey/                 # 메인 패키지
│   ├── core/                    # 핵심 엔진
│   ├── device/                  # 디바이스 통신 레이어
│   ├── exploration/             # UI 분석 및 탐색
│   ├── detection/               # 버그 감지 레이어
│   ├── reporting/               # 리포팅 및 분석
│   ├── utils/                   # 유틸리티
│   └── cli/                     # CLI 인터페이스
│
├── tests/                       # 테스트 디렉토리
│   ├── unit/                    # 단위 테스트
│   └── integration/             # 통합 테스트
│
├── docs/                        # 프로젝트 문서
│   ├── design/                  # 설계 문서
│   │   ├── ARCHITECTURE.md      # 아키텍처 설계
│   │   ├── MODULE_STRUCTURE.md  # 모듈 구조
│   │   └── ROADMAP.md           # 구현 로드맵
│   ├── api/                     # API 문서
│   ├── user_guide/              # 사용자 가이드
│   └── developer_guide/         # 개발자 가이드
│
└── examples/                    # 예제 설정 파일
```

## 🔗 Related Workspaces

### WhatAp Android Agent Workspace
**Path**: `/Users/devload/whatap/android_workspace/androidAgent`
**Purpose**: Android Agent 개발 및 BOM 빌드

### WhatAp WebView Sample App
**Path**: `/Users/devload/whatap/android_workspace/whatap-webview-sample/android-app`
**Purpose**: Android Agent 테스트용 샘플 앱

## 🤖 AI Assistant Guidelines

### Tool Selection Rules
- **Simple edits (1-2 files)**: Use Cursor CLI
- **Build/Config issues**: Use Claude Code (this tool)
- **Code analysis**: Use Codex CLI
- **Multi-file changes**: Use Claude Code
- **Performance issues**: Use Codex CLI
- **Security checks**: Use Codex CLI

### Development Workflow
1. **Planning**: Use TodoWrite tool for task management
2. **Implementation**: Choose appropriate AI tool based on task type
3. **Testing**: Run tests after significant changes
4. **Documentation**: Update CLAUDE.md with new findings

## 📱 Test Devices

### Connected Devices
- **VIVO**: `3062821163005VC` - Model `V2041`
- **Samsung**: `RFCX919P8ZF` - Model `SM-A356N`
- **REDMI**: `KNKN6DJJ65X4VGBU` - Model `2409BRN2CL` (currently disconnected)

### ADB Commands
```bash
# VIVO
adb -s 3062821163005VC shell

# Samsung
adb -s RFCX919P8ZF shell

# REDMI (when connected)
adb -s KNKN6DJJ65X4VGBU shell
```

## 🛠️ Development Environment

### System Information
- **Platform**: macOS (Darwin 24.5.0)
- **Working Directory**: `/Users/devload/smartMonkey`
- **Git Repository**: Not initialized yet

### Required Tools
- Android SDK
- ADB (Android Debug Bridge)
- Python 3.x (for automation scripts)
- Java Development Kit (JDK)

## 📝 Development Notes

### Initial Setup
- Project created on 2025-10-23
- CLAUDE.md initialized with project structure
- Workspace location: `/Users/devload/smartMonkey`

### Design Phase (2025-10-23)
- ✅ Architecture design completed (`docs/design/ARCHITECTURE.md`)
- ✅ Module structure defined (`docs/design/MODULE_STRUCTURE.md`)
- ✅ Implementation roadmap created (`docs/design/ROADMAP.md`)

### Design Decisions

#### Architecture Pattern
- **Selected**: Modular Plugin-Based Architecture
- **Rationale**:
  - Modularity for independent development and testing
  - Extensibility via plugins for strategies, detectors, exporters
  - Scalability for distributed testing
  - Clear separation of concerns

#### Technology Stack
- **Language**: Python 3.9+
  - Rich ecosystem for automation
  - Excellent ADB libraries
  - Rapid prototyping
  - Strong async support
- **Key Libraries**:
  - `adb-shell`: Pure Python ADB implementation
  - `lxml`: Fast XML parsing for UI hierarchy
  - `networkx`: State graph representation
  - `click`: CLI framework
  - `jinja2`: HTML report templates
  - `matplotlib`: Data visualization

#### Core Modules (5 layers)
1. **Device Layer**: ADB communication, event injection, screen capture
2. **Exploration Layer**: UI parsing, state management, exploration strategies
3. **Detection Layer**: Crash/ANR detection, performance monitoring
4. **Reporting Layer**: Data collection, report generation, visualization
5. **Core Layer**: Engine orchestration, scheduling, configuration

#### Exploration Strategies
1. Random (baseline)
2. Depth-First Search (DFS)
3. Breadth-First Search (BFS)
4. Weighted (prioritize unvisited elements)
5. ML-based (future enhancement)

#### Implementation Timeline
- **Phase 1**: Foundation (Weeks 1-3) - Device layer
- **Phase 2**: Exploration (Weeks 4-6) - UI analysis and strategies
- **Phase 3**: Detection (Weeks 7-8) - Bug detection and monitoring
- **Phase 4**: Reporting (Weeks 9-10) - Reports and analytics
- **Phase 5**: Integration (Weeks 11-12) - CLI and polish
- **Target**: v1.0 release in 12 weeks

### Next Steps
- [ ] Initialize git repository
- [ ] Set up `pyproject.toml` with dependencies
- [ ] Create project directory structure
- [ ] Implement device layer (Week 2-3)
- [ ] Set up pytest and CI pipeline

## 🔍 Reference Documents

### External Documentation
- Android Debug Bridge (ADB): https://developer.android.com/tools/adb
- Android UI Testing: https://developer.android.com/training/testing/ui-testing
- Monkey Test Tool: https://developer.android.com/studio/test/other-testing-tools/monkey

### Internal Documentation
- Main Claude Workspace: `/Users/devload/CLAUDE.md`
- WhatAp Development Guidelines: (referenced from main CLAUDE.md)
- SmartMonkey Architecture: `docs/design/ARCHITECTURE.md`
- Module Structure: `docs/design/MODULE_STRUCTURE.md`
- Implementation Roadmap: `docs/design/ROADMAP.md`

## 📊 Project Status

**Current Phase**: Prototype Complete ✅
**Last Updated**: 2025-10-23
**Version**: 0.1.0
**Status**: Fully functional prototype ready for use

### Completed ✅

**Design Phase**:
- ✅ Architecture design (docs/design/ARCHITECTURE.md)
- ✅ Module structure definition (docs/design/MODULE_STRUCTURE.md)
- ✅ Implementation roadmap (docs/design/ROADMAP.md)
- ✅ Technology stack selection

**Implementation Phase**:
- ✅ Phase 1: Project setup and infrastructure
- ✅ Phase 2: Device communication layer (5 modules, 699 lines)
- ✅ Phase 3: UI analysis & exploration (7 modules, 613 lines)
- ✅ Phase 4: Reporting (JSON + Text)
- ✅ Phase 5: CLI integration (Click framework)
- ✅ Phase 6: End-to-end testing on real devices
- ✅ Phase 7: Final documentation

**Testing Results**:
- ✅ Successfully tested on Samsung SM-A356N (Android 15)
- ✅ Multi-device support verified (VIVO, Samsung, Emulator)
- ✅ 10 steps exploration completed in 74.9 seconds
- ✅ 3 unique states discovered
- ✅ 10 screenshots captured
- ✅ JSON and text reports generated

### Project Metrics

**Code Statistics**:
- Total source files: 17
- Total lines of code: 1,782
- Modules: device (5), exploration (7), reporting (1), utils (3), cli (1)

**Features Implemented**:
- ✅ ADB device communication with retry logic
- ✅ Touch/swipe/key event injection
- ✅ Screenshot capture and compression
- ✅ UI hierarchy parsing (uiautomator)
- ✅ State detection with MD5 hashing
- ✅ Random exploration strategy
- ✅ Weighted exploration strategy (prioritizes unvisited elements)
- ✅ JSON and text report generation
- ✅ CLI with list-devices and run commands

### How to Use

**List devices**:
```bash
export PYTHONPATH=/Users/devload/smartMonkey:$PYTHONPATH
python3 -m smartmonkey.cli.main list-devices
```

**Run exploration**:
```bash
export PYTHONPATH=/Users/devload/smartMonkey:$PYTHONPATH
python3 -m smartmonkey.cli.main run \
  --package com.android.settings \
  --steps 20 \
  --strategy weighted \
  --output ./reports/test_run
```

### Next Steps (Future Versions)

**Version 0.2.0** (Planned):
- [ ] Bug detection layer (crashes, ANRs)
- [ ] HTML report with visualizations
- [ ] DFS and BFS exploration strategies

**Version 0.3.0** (Planned):
- [ ] Performance monitoring (FPS, memory, CPU)
- [ ] Configuration file support (YAML)
- [ ] Code coverage tracking

**Version 0.4.0+** (Future):
- [ ] ML-based exploration strategy
- [ ] CI/CD integration
- [ ] Cloud testing support

---

**Note**: This CLAUDE.md is specific to the SmartMonkey project workspace at `/Users/devload/smartMonkey`. For general development environment settings and AI tool usage guidelines, refer to `/Users/devload/CLAUDE.md`.

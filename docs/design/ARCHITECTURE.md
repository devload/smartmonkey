# SmartMonkey Architecture Design Document

**Version**: 1.0
**Date**: 2025-10-23
**Status**: Draft

---

## 1. Executive Summary

SmartMonkey is an intelligent Android app automation testing tool that performs smarter UI exploration compared to Google's Monkey tool. It uses AI-driven strategies to discover app functionality, detect bugs, and generate comprehensive test reports.

### Key Differentiators
- **Intelligent Exploration**: Uses UI hierarchy analysis and learned patterns instead of random events
- **Multi-Device Support**: Parallel testing across multiple Android devices
- **Bug Detection**: Automatic crash, ANR, and UI freeze detection
- **Rich Reporting**: Detailed test reports with screenshots and reproduction steps

---

## 2. Architecture Pattern

### 2.1 Selected Pattern: **Modular Plugin-Based Architecture**

**Rationale**:
- **Modularity**: Each component (ADB, UI analysis, test execution) is independently developed and testable
- **Extensibility**: New exploration strategies, report formats, and device types can be added as plugins
- **Maintainability**: Clear separation of concerns makes debugging and updates easier
- **Scalability**: Modules can be distributed across multiple processes/machines

### 2.2 Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        SmartMonkey Core                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   CLI/API    │  │  Scheduler   │  │   Config     │          │
│  │  Interface   │  │   Manager    │  │   Manager    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
├─────────────────────────────────────────────────────────────────┤
│                        Plugin Layer                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Device Communication Layer                   │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  • ADB Manager       • Device Pool      • Screen Capture │  │
│  │  • Event Injector    • App Manager      • Logcat Monitor │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              UI Analysis & Exploration Layer              │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  • UI Hierarchy Parser   • Element Detector              │  │
│  │  • State Manager         • Exploration Strategies        │  │
│  │  • Action Generator      • Coverage Tracker              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Bug Detection & Monitoring Layer             │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  • Crash Detector    • ANR Detector    • Memory Monitor  │  │
│  │  • UI Freeze Checker • Exception Parser • Performance Mon│  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Reporting & Analytics Layer                  │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │  • Report Generator  • Data Collector  • Visualization   │  │
│  │  • Statistics        • Export Formats  • Comparison Tool │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
    ┌─────────┐          ┌─────────┐         ┌─────────┐
    │ Device  │          │ Device  │         │ Device  │
    │   #1    │          │   #2    │         │   #N    │
    └─────────┘          └─────────┘         └─────────┘
```

---

## 3. Core Modules

### 3.1 Device Communication Layer

**Responsibilities**:
- Manage ADB connections to multiple devices
- Execute ADB commands with proper error handling
- Inject touch/swipe/key events
- Capture screenshots and screen recordings
- Monitor logcat output in real-time
- Install/uninstall/launch apps

**Key Components**:
- `ADBManager`: Central ADB command executor
- `DevicePool`: Multi-device connection manager
- `EventInjector`: Touch/gesture event generator
- `ScreenCapture`: Screenshot and recording handler
- `LogcatMonitor`: Real-time log parsing
- `AppManager`: App installation and lifecycle control

**Technology**:
- Python `subprocess` for ADB commands
- `adb-shell` library for programmatic ADB access
- `asyncio` for concurrent device operations

### 3.2 UI Analysis & Exploration Layer

**Responsibilities**:
- Parse UI hierarchy from `uiautomator dump`
- Identify interactive elements (buttons, text fields, etc.)
- Track application state and visited screens
- Generate intelligent action sequences
- Implement exploration strategies (DFS, BFS, ML-based)
- Track code/UI coverage

**Key Components**:
- `UIHierarchyParser`: Parse XML UI dump into object model
- `ElementDetector`: Identify clickable/interactive elements
- `StateManager`: Track application states and transitions
- `ExplorationEngine`: Core exploration algorithm
- `ActionGenerator`: Generate context-aware actions
- `CoverageTracker`: Monitor exploration coverage

**Exploration Strategies**:
1. **Random Strategy** (baseline)
2. **Depth-First Strategy** (explore deeply before backtracking)
3. **Breadth-First Strategy** (explore all options at each level)
4. **Weight-Based Strategy** (prioritize unvisited/rare elements)
5. **ML-Based Strategy** (learn from successful test patterns)

**Technology**:
- `lxml` for XML parsing
- `networkx` for state graph representation
- `scikit-learn` for ML-based exploration (future)

### 3.3 Bug Detection & Monitoring Layer

**Responsibilities**:
- Detect crashes from logcat
- Identify ANR (Application Not Responding) events
- Monitor memory usage and detect leaks
- Detect UI freezes and slow rendering
- Parse and categorize exceptions
- Track performance metrics

**Key Components**:
- `CrashDetector`: Parse crash logs and stack traces
- `ANRDetector`: Detect ANR events from logcat
- `MemoryMonitor`: Track heap usage and detect leaks
- `PerformanceMonitor`: FPS, frame drops, jank detection
- `ExceptionParser`: Categorize and group exceptions
- `UIFreezeChecker`: Detect unresponsive UI

**Detection Rules**:
- Crash: `FATAL EXCEPTION` in logcat
- ANR: `ANR in` or `Broadcast of Intent` timeout
- Memory leak: Heap usage consistently increasing
- UI freeze: No UI updates for >5 seconds
- Slow rendering: Frame time >16ms (60fps) or >11ms (90fps)

**Technology**:
- Regex patterns for log parsing
- `psutil` for system resource monitoring
- Custom performance metrics collection

### 3.4 Reporting & Analytics Layer

**Responsibilities**:
- Collect all test execution data
- Generate comprehensive test reports
- Create visualizations (coverage graphs, crash timelines)
- Export in multiple formats (HTML, JSON, XML)
- Compare test runs
- Calculate statistics and metrics

**Key Components**:
- `DataCollector`: Centralize all test data
- `ReportGenerator`: Create formatted reports
- `Visualization`: Generate charts and graphs
- `ExportEngine`: Support multiple output formats
- `StatisticsCalculator`: Compute test metrics
- `ComparisonTool`: Compare multiple test runs

**Report Contents**:
- Test summary (duration, events, coverage)
- Discovered bugs (crashes, ANRs, exceptions)
- Screenshots of each state explored
- Action sequence for each bug reproduction
- Performance metrics (CPU, memory, FPS)
- Code coverage (if available)

**Technology**:
- `jinja2` for HTML report templates
- `matplotlib` for visualizations
- `pandas` for data analysis
- JSON/XML standard libraries

---

## 4. Technology Stack

### 4.1 Programming Language: **Python 3.9+**

**Rationale**:
- Rich ecosystem for system automation
- Excellent ADB libraries
- Easy XML/JSON parsing
- Rapid prototyping and development
- Great for data analysis and reporting
- Strong asyncio support for concurrency

### 4.2 Core Dependencies

**Device Communication**:
- `adb-shell`: Pure Python ADB implementation
- `pure-python-adb`: Alternative ADB library
- `subprocess`: Native ADB command execution

**UI Analysis**:
- `lxml`: Fast XML parsing
- `beautifulsoup4`: Alternative HTML/XML parser
- `networkx`: Graph representation for state management

**Bug Detection**:
- `re`: Regex for log parsing
- `psutil`: System resource monitoring

**Reporting**:
- `jinja2`: HTML template engine
- `matplotlib`: Data visualization
- `pandas`: Data analysis
- `Pillow`: Image processing for screenshots

**Testing & Quality**:
- `pytest`: Unit and integration testing
- `black`: Code formatting
- `pylint`: Code linting
- `mypy`: Static type checking

**Utilities**:
- `click`: CLI framework
- `pyyaml`: Configuration files
- `loguru`: Advanced logging
- `tqdm`: Progress bars

### 4.3 Optional Dependencies (Future)

**Machine Learning** (for ML-based exploration):
- `scikit-learn`: ML algorithms
- `tensorflow` or `pytorch`: Deep learning

**Cloud/Distributed Testing**:
- `celery`: Distributed task queue
- `redis`: Task broker and cache

---

## 5. Design Patterns

### 5.1 Command Pattern
**Use**: ADB operations and device commands

```python
class Command(ABC):
    @abstractmethod
    def execute(self, device: Device) -> Result:
        pass

class TapCommand(Command):
    def __init__(self, x: int, y: int):
        self.x, self.y = x, y

    def execute(self, device: Device) -> Result:
        return device.tap(self.x, self.y)

class SwipeCommand(Command):
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        self.x1, self.y1, self.x2, self.y2 = x1, y1, x2, y2

    def execute(self, device: Device) -> Result:
        return device.swipe(self.x1, self.y1, self.x2, self.y2)
```

### 5.2 Strategy Pattern
**Use**: Exploration algorithms

```python
class ExplorationStrategy(ABC):
    @abstractmethod
    def next_action(self, state: AppState) -> Action:
        pass

class RandomStrategy(ExplorationStrategy):
    def next_action(self, state: AppState) -> Action:
        return random.choice(state.available_actions())

class DFSStrategy(ExplorationStrategy):
    def next_action(self, state: AppState) -> Action:
        # Depth-first exploration logic
        pass

class MLStrategy(ExplorationStrategy):
    def next_action(self, state: AppState) -> Action:
        # ML-based action selection
        pass
```

### 5.3 Observer Pattern
**Use**: Event monitoring and notifications

```python
class EventObserver(ABC):
    @abstractmethod
    def on_event(self, event: Event):
        pass

class CrashObserver(EventObserver):
    def on_event(self, event: Event):
        if event.type == EventType.CRASH:
            self.report_crash(event)

class ANRObserver(EventObserver):
    def on_event(self, event: Event):
        if event.type == EventType.ANR:
            self.report_anr(event)
```

### 5.4 Factory Pattern
**Use**: Device and component creation

```python
class DeviceFactory:
    @staticmethod
    def create_device(serial: str) -> Device:
        device_type = DeviceFactory.detect_device_type(serial)
        if device_type == "emulator":
            return EmulatorDevice(serial)
        elif device_type == "physical":
            return PhysicalDevice(serial)
        else:
            raise UnsupportedDeviceError(serial)
```

### 5.5 Singleton Pattern
**Use**: Configuration and global state management

```python
class ConfigManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
```

---

## 6. Module Structure

```
smartmonkey/
├── core/                       # Core engine
│   ├── __init__.py
│   ├── engine.py              # Main SmartMonkey engine
│   ├── scheduler.py           # Test scheduling
│   └── config.py              # Configuration management
│
├── device/                    # Device communication layer
│   ├── __init__.py
│   ├── adb_manager.py         # ADB command executor
│   ├── device_pool.py         # Multi-device manager
│   ├── event_injector.py      # Event injection
│   ├── screen_capture.py      # Screenshot/recording
│   ├── logcat_monitor.py      # Logcat monitoring
│   └── app_manager.py         # App lifecycle management
│
├── exploration/               # UI analysis & exploration
│   ├── __init__.py
│   ├── ui_parser.py           # UI hierarchy parser
│   ├── element_detector.py    # Interactive element detection
│   ├── state_manager.py       # Application state tracking
│   ├── exploration_engine.py  # Core exploration logic
│   ├── action_generator.py    # Action generation
│   ├── coverage_tracker.py    # Coverage monitoring
│   └── strategies/            # Exploration strategies
│       ├── __init__.py
│       ├── random_strategy.py
│       ├── dfs_strategy.py
│       ├── bfs_strategy.py
│       ├── weighted_strategy.py
│       └── ml_strategy.py
│
├── detection/                 # Bug detection layer
│   ├── __init__.py
│   ├── crash_detector.py      # Crash detection
│   ├── anr_detector.py        # ANR detection
│   ├── memory_monitor.py      # Memory monitoring
│   ├── performance_monitor.py # Performance metrics
│   ├── exception_parser.py    # Exception categorization
│   └── ui_freeze_checker.py   # UI freeze detection
│
├── reporting/                 # Reporting & analytics
│   ├── __init__.py
│   ├── data_collector.py      # Data collection
│   ├── report_generator.py    # Report generation
│   ├── visualization.py       # Charts and graphs
│   ├── export_engine.py       # Export in various formats
│   ├── statistics.py          # Statistics calculation
│   └── templates/             # Report templates
│       ├── html_report.j2
│       └── json_schema.json
│
├── utils/                     # Utilities
│   ├── __init__.py
│   ├── logger.py              # Logging configuration
│   ├── exceptions.py          # Custom exceptions
│   └── helpers.py             # Helper functions
│
├── cli/                       # CLI interface
│   ├── __init__.py
│   └── main.py                # CLI entry point
│
└── tests/                     # Unit tests
    ├── __init__.py
    ├── test_device/
    ├── test_exploration/
    ├── test_detection/
    └── test_reporting/
```

---

## 7. Data Flow

### 7.1 Test Execution Flow

```
1. User starts SmartMonkey
   ↓
2. CLI parses arguments and loads configuration
   ↓
3. Engine initializes modules and connects to device(s)
   ↓
4. App Manager installs/launches target app
   ↓
5. Exploration Engine starts exploration loop:
   a. UI Parser dumps UI hierarchy
   b. State Manager tracks current state
   c. Strategy selects next action
   d. Event Injector executes action
   e. Screen Capture takes screenshot
   f. Bug Detectors monitor for issues
   g. Coverage Tracker updates metrics
   ↓
6. Repeat step 5 until:
   - Maximum events reached
   - Time limit exceeded
   - User stops test
   - Critical bug found (optional)
   ↓
7. Data Collector aggregates all test data
   ↓
8. Report Generator creates final report
   ↓
9. Export Engine saves report in desired format
   ↓
10. Engine cleanup and shutdown
```

### 7.2 Bug Detection Flow

```
┌─────────────────┐
│ Logcat Monitor  │ (continuously running)
└────────┬────────┘
         │
         ├─> Crash Detector ──> Report crash with stack trace
         ├─> ANR Detector ───> Report ANR with thread dump
         └─> Exception Parser ─> Categorize and count exceptions

┌─────────────────┐
│ Memory Monitor  │ (periodic polling)
└────────┬────────┘
         │
         └─> Memory Leak Detector ─> Report memory leak

┌─────────────────┐
│ Performance Mon │ (periodic polling)
└────────┬────────┘
         │
         ├─> FPS Monitor ──────> Report slow rendering
         └─> UI Freeze Checker ─> Report UI freeze
```

---

## 8. Key Algorithms

### 8.1 Intelligent Exploration Algorithm (Weighted Strategy)

```python
def next_action(state: AppState) -> Action:
    """
    Select next action based on weighted priorities:
    - Unvisited elements: highest priority
    - Rare elements: medium priority
    - Previously visited: lowest priority
    """
    elements = state.interactive_elements()

    # Calculate weights for each element
    weights = []
    for element in elements:
        if not element.visited:
            weight = 10.0  # Unvisited gets highest weight
        else:
            # Weight decreases with visit count
            weight = 1.0 / (1 + element.visit_count)

        # Boost weight for certain element types
        if element.type in ['Button', 'ImageButton']:
            weight *= 1.5
        elif element.text and 'submit' in element.text.lower():
            weight *= 2.0

        weights.append(weight)

    # Select element based on weighted probability
    selected = random.choices(elements, weights=weights)[0]
    return TapAction(selected.x, selected.y)
```

### 8.2 State Similarity Detection

```python
def is_similar_state(state1: AppState, state2: AppState) -> bool:
    """
    Determine if two app states are similar to avoid revisiting.
    Uses UI hierarchy structure and element content.
    """
    # Compare activity names
    if state1.activity != state2.activity:
        return False

    # Compare element count (with tolerance)
    count1, count2 = len(state1.elements), len(state2.elements)
    if abs(count1 - count2) > 3:  # Allow small variations
        return False

    # Compare element types and text
    elements1 = sorted([(e.type, e.text) for e in state1.elements])
    elements2 = sorted([(e.type, e.text) for e in state2.elements])

    # Calculate similarity score
    matches = sum(1 for e1, e2 in zip(elements1, elements2) if e1 == e2)
    similarity = matches / max(count1, count2)

    return similarity > 0.85  # 85% similarity threshold
```

---

## 9. Performance Considerations

### 9.1 Concurrency
- Use `asyncio` for concurrent device operations
- Thread pool for CPU-bound tasks (image processing, XML parsing)
- Process pool for multi-device testing

### 9.2 Resource Management
- Limit screenshot retention (keep last N or compress)
- Stream logcat to file instead of memory
- Periodic cleanup of temporary files

### 9.3 Optimization Targets
- UI dump parsing: <100ms per dump
- State comparison: <50ms per comparison
- Screenshot capture: <500ms per screenshot
- Event injection: <50ms per event

---

## 10. Error Handling

### 10.1 Device Disconnection
- Detect disconnection via ADB heartbeat
- Attempt reconnection (3 retries with exponential backoff)
- Gracefully save current state and continue with other devices
- Generate partial report for disconnected device

### 10.2 App Crashes
- Capture crash immediately
- Save UI state before crash
- Attempt to restart app (if configured)
- Record reproduction steps

### 10.3 ADB Failures
- Retry ADB commands up to 3 times
- Fall back to alternative ADB implementation if available
- Log failures for debugging
- Provide clear error messages to user

---

## 11. Security & Privacy

### 11.1 Data Handling
- Screenshots may contain sensitive data (PII, credentials)
- Option to blur/mask sensitive UI elements
- Secure storage of test artifacts
- Option to disable screenshot capture

### 11.2 Permissions
- Minimal required permissions
- Clear documentation of why each permission is needed
- No network access unless explicitly enabled (for cloud reporting)

---

## 12. Future Enhancements

### 12.1 Phase 2 Features
- [ ] Machine learning-based exploration
- [ ] Integration with CI/CD pipelines
- [ ] Cloud-based distributed testing
- [ ] iOS support via XCUITest
- [ ] Visual regression testing
- [ ] Accessibility testing

### 12.2 Phase 3 Features
- [ ] Custom test scenario recording and replay
- [ ] Integration with bug tracking systems (Jira, GitHub Issues)
- [ ] Real-time dashboard for test monitoring
- [ ] Automated test case generation from exploration
- [ ] Code coverage integration (with instrumentation)

---

## 13. References

### 13.1 Similar Tools
- **Google Monkey**: Random event generator
  - Limitation: Purely random, no intelligence
  - Lesson: Need structured exploration

- **MonkeyRunner**: Scriptable testing tool
  - Limitation: Requires manual scripting
  - Lesson: Automation is key

- **Appium**: Cross-platform testing framework
  - Strength: Plugin architecture, multi-platform
  - Lesson: Modular design is essential

- **UIAutomator2**: Android UI testing framework
  - Strength: Direct access to UI hierarchy
  - Lesson: Leverage native Android tools

### 13.2 Research Papers
- "Automated Test Input Generation for Android: Towards Getting There in an Industrial Case"
- "Systematic Testing for Machine Learning Applications"
- "PUMA: Programmable UI-Automation for Large-Scale Dynamic Analysis of Mobile Apps"

---

## Appendix A: Configuration File Format

```yaml
# smartmonkey_config.yaml

general:
  app_package: "com.example.app"
  max_events: 1000
  timeout_seconds: 3600
  exploration_strategy: "weighted"  # random, dfs, bfs, weighted, ml

devices:
  - serial: "3062821163005VC"
    nickname: "VIVO"
  - serial: "RFCX919P8ZF"
    nickname: "Samsung"

exploration:
  enable_text_input: true
  text_input_samples:
    - "test@example.com"
    - "password123"
    - "John Doe"
  enable_swipe: true
  swipe_probability: 0.2
  back_button_probability: 0.1

detection:
  monitor_crashes: true
  monitor_anrs: true
  monitor_memory: true
  memory_threshold_mb: 512
  monitor_performance: true
  fps_threshold: 30

reporting:
  output_dir: "./reports"
  formats: ["html", "json"]
  include_screenshots: true
  max_screenshots: 100
  screenshot_compression: 0.8
  include_logcat: true

advanced:
  enable_coverage_tracking: false
  coverage_file: "./coverage.ec"
  seed: 42  # For reproducibility
  verbose_logging: true
```

---

**Document Owner**: SmartMonkey Development Team
**Last Updated**: 2025-10-23
**Next Review**: TBD

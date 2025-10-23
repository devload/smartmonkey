# SmartMonkey Module Structure & Dependencies

**Version**: 1.0
**Date**: 2025-10-23

---

## 1. Project Structure

```
smartmonkey/
├── pyproject.toml              # Project metadata and dependencies
├── setup.py                    # Installation script
├── README.md                   # Project overview
├── CLAUDE.md                   # Development environment guide
├── requirements.txt            # Python dependencies
├── requirements-dev.txt        # Development dependencies
│
├── smartmonkey/                # Main package
│   ├── __init__.py
│   ├── __version__.py
│   │
│   ├── core/                   # Core engine
│   │   ├── __init__.py
│   │   ├── engine.py           # Main SmartMonkey engine
│   │   ├── scheduler.py        # Test scheduling and coordination
│   │   └── config.py           # Configuration management
│   │
│   ├── device/                 # Device communication layer
│   │   ├── __init__.py
│   │   ├── adb_manager.py      # ADB command executor
│   │   ├── device.py           # Device abstraction
│   │   ├── device_pool.py      # Multi-device manager
│   │   ├── event_injector.py   # Event injection (tap, swipe, etc.)
│   │   ├── screen_capture.py   # Screenshot/recording
│   │   ├── logcat_monitor.py   # Logcat monitoring
│   │   └── app_manager.py      # App lifecycle management
│   │
│   ├── exploration/            # UI analysis & exploration
│   │   ├── __init__.py
│   │   ├── ui_parser.py        # UI hierarchy parser
│   │   ├── element.py          # UI element representation
│   │   ├── element_detector.py # Interactive element detection
│   │   ├── state.py            # Application state representation
│   │   ├── state_manager.py    # Application state tracking
│   │   ├── exploration_engine.py  # Core exploration logic
│   │   ├── action.py           # Action representation
│   │   ├── action_generator.py # Action generation
│   │   ├── coverage_tracker.py # Coverage monitoring
│   │   └── strategies/         # Exploration strategies
│   │       ├── __init__.py
│   │       ├── base.py         # Base strategy interface
│   │       ├── random_strategy.py
│   │       ├── dfs_strategy.py
│   │       ├── bfs_strategy.py
│   │       ├── weighted_strategy.py
│   │       └── ml_strategy.py
│   │
│   ├── detection/              # Bug detection layer
│   │   ├── __init__.py
│   │   ├── base_detector.py    # Base detector interface
│   │   ├── crash_detector.py   # Crash detection
│   │   ├── anr_detector.py     # ANR detection
│   │   ├── memory_monitor.py   # Memory monitoring
│   │   ├── performance_monitor.py  # Performance metrics
│   │   ├── exception_parser.py # Exception categorization
│   │   └── ui_freeze_checker.py    # UI freeze detection
│   │
│   ├── reporting/              # Reporting & analytics
│   │   ├── __init__.py
│   │   ├── data_collector.py   # Data collection
│   │   ├── report.py           # Report data structure
│   │   ├── report_generator.py # Report generation
│   │   ├── visualization.py    # Charts and graphs
│   │   ├── export_engine.py    # Export in various formats
│   │   ├── statistics.py       # Statistics calculation
│   │   └── templates/          # Report templates
│   │       ├── html_report.j2
│   │       ├── markdown_report.j2
│   │       └── json_schema.json
│   │
│   ├── utils/                  # Utilities
│   │   ├── __init__.py
│   │   ├── logger.py           # Logging configuration
│   │   ├── exceptions.py       # Custom exceptions
│   │   ├── helpers.py          # Helper functions
│   │   └── constants.py        # Constants and enums
│   │
│   └── cli/                    # CLI interface
│       ├── __init__.py
│       └── main.py             # CLI entry point
│
├── tests/                      # Unit and integration tests
│   ├── __init__.py
│   ├── conftest.py             # pytest fixtures
│   ├── unit/                   # Unit tests
│   │   ├── test_core/
│   │   ├── test_device/
│   │   ├── test_exploration/
│   │   ├── test_detection/
│   │   └── test_reporting/
│   └── integration/            # Integration tests
│       ├── test_e2e_exploration.py
│       └── test_multi_device.py
│
├── docs/                       # Documentation
│   ├── design/                 # Design documents
│   │   ├── ARCHITECTURE.md
│   │   └── MODULE_STRUCTURE.md (this file)
│   ├── api/                    # API documentation
│   ├── user_guide/             # User guides
│   └── developer_guide/        # Developer guides
│
├── examples/                   # Example configurations
│   ├── basic_config.yaml
│   ├── advanced_config.yaml
│   └── multi_device_config.yaml
│
└── scripts/                    # Utility scripts
    ├── install.sh              # Installation script
    ├── run_tests.sh            # Test runner
    └── build_docs.sh           # Documentation builder
```

---

## 2. Module Dependencies

### 2.1 Dependency Graph

```
┌──────────────┐
│     CLI      │
└──────┬───────┘
       │
       ▼
┌──────────────┐
│  Core Engine │
└──────┬───────┘
       │
       ├───────────────────────────────┐
       │                               │
       ▼                               ▼
┌──────────────┐              ┌──────────────┐
│   Device     │◄─────────────│ Exploration  │
│   Layer      │              │   Engine     │
└──────┬───────┘              └──────┬───────┘
       │                             │
       ├─────────────────────────────┤
       │                             │
       ▼                             ▼
┌──────────────┐              ┌──────────────┐
│  Detection   │              │  Reporting   │
│   Layer      │              │    Layer     │
└──────────────┘              └──────────────┘
       │                             │
       └─────────────┬───────────────┘
                     ▼
              ┌──────────────┐
              │   Utils      │
              └──────────────┘
```

### 2.2 Layer Dependencies

**Level 0: Utilities** (no dependencies)
- `utils/`

**Level 1: Device Communication** (depends on utils)
- `device/` → `utils/`

**Level 2: Detection & Exploration** (depends on device + utils)
- `detection/` → `device/`, `utils/`
- `exploration/` → `device/`, `utils/`

**Level 3: Reporting** (depends on all lower layers)
- `reporting/` → `exploration/`, `detection/`, `device/`, `utils/`

**Level 4: Core** (orchestrates all layers)
- `core/` → `exploration/`, `detection/`, `reporting/`, `device/`, `utils/`

**Level 5: CLI** (depends on core)
- `cli/` → `core/`, `utils/`

---

## 3. Module Details

### 3.1 Core Module (`smartmonkey.core`)

**Purpose**: Orchestrate all components and manage test execution lifecycle

**Public API**:
```python
# engine.py
class SmartMonkeyEngine:
    def __init__(self, config: Config)
    def start(self) -> None
    def stop(self) -> None
    def run(self) -> Report
    def get_status(self) -> Status

# scheduler.py
class TestScheduler:
    def schedule_test(self, device: Device, app: App) -> None
    def get_next_task(self) -> Optional[Task]
    def mark_complete(self, task: Task) -> None

# config.py
class Config:
    def __init__(self, config_file: str)
    @classmethod
    def from_dict(cls, data: dict) -> Config
    @classmethod
    def from_yaml(cls, path: str) -> Config
    def validate(self) -> bool
```

**Dependencies**:
- Internal: `device`, `exploration`, `detection`, `reporting`, `utils`
- External: `pyyaml`, `loguru`

---

### 3.2 Device Module (`smartmonkey.device`)

**Purpose**: Abstract device communication and ADB operations

**Public API**:
```python
# device.py
class Device:
    def __init__(self, serial: str)
    @property
    def serial(self) -> str
    @property
    def model(self) -> str
    def connect(self) -> bool
    def disconnect(self) -> None
    def is_connected(self) -> bool

# adb_manager.py
class ADBManager:
    def execute(self, command: str, timeout: int = 30) -> str
    def shell(self, command: str) -> str
    def get_devices(self) -> List[str]
    def install_app(self, apk_path: str) -> bool
    def uninstall_app(self, package: str) -> bool

# event_injector.py
class EventInjector:
    def tap(self, x: int, y: int) -> bool
    def swipe(self, x1: int, y1: int, x2: int, y2: int, duration: int = 300) -> bool
    def press_key(self, keycode: int) -> bool
    def input_text(self, text: str) -> bool

# screen_capture.py
class ScreenCapture:
    def take_screenshot(self, output_path: str) -> bool
    def start_recording(self, output_path: str) -> bool
    def stop_recording(self) -> bool

# logcat_monitor.py
class LogcatMonitor:
    def start(self) -> None
    def stop(self) -> None
    def get_logs(self, since: datetime = None) -> List[str]
    def add_filter(self, tag: str, priority: str) -> None
    def clear_filters(self) -> None

# app_manager.py
class AppManager:
    def launch_app(self, package: str, activity: str = None) -> bool
    def stop_app(self, package: str) -> bool
    def clear_app_data(self, package: str) -> bool
    def get_current_activity(self) -> str
    def is_app_running(self, package: str) -> bool
```

**Dependencies**:
- Internal: `utils`
- External: `adb-shell` or `pure-python-adb`, `subprocess`

---

### 3.3 Exploration Module (`smartmonkey.exploration`)

**Purpose**: Analyze UI and intelligently explore app functionality

**Public API**:
```python
# ui_parser.py
class UIParser:
    def parse(self, xml_content: str) -> UIHierarchy
    def dump_hierarchy(self, device: Device) -> UIHierarchy

# element.py
class UIElement:
    resource_id: str
    class_name: str
    text: str
    content_desc: str
    bounds: Rect
    clickable: bool
    scrollable: bool
    visible: bool

# state.py
class AppState:
    activity: str
    elements: List[UIElement]
    screenshot_path: str
    timestamp: datetime

# state_manager.py
class StateManager:
    def add_state(self, state: AppState) -> None
    def get_current_state(self) -> AppState
    def is_visited(self, state: AppState) -> bool
    def get_state_graph(self) -> nx.DiGraph

# action.py
class Action(ABC):
    @abstractmethod
    def execute(self, device: Device) -> bool

class TapAction(Action):
    def __init__(self, element: UIElement)

class SwipeAction(Action):
    def __init__(self, direction: Direction)

# exploration_engine.py
class ExplorationEngine:
    def __init__(self, device: Device, strategy: ExplorationStrategy)
    def explore(self, max_steps: int = 1000) -> ExplorationResult
    def step(self) -> Action

# strategies/base.py
class ExplorationStrategy(ABC):
    @abstractmethod
    def next_action(self, state: AppState) -> Action

# coverage_tracker.py
class CoverageTracker:
    def track_action(self, action: Action) -> None
    def get_coverage(self) -> float
    def get_coverage_report(self) -> dict
```

**Dependencies**:
- Internal: `device`, `utils`
- External: `lxml`, `networkx`

---

### 3.4 Detection Module (`smartmonkey.detection`)

**Purpose**: Monitor app health and detect bugs

**Public API**:
```python
# base_detector.py
class BaseDetector(ABC):
    @abstractmethod
    def detect(self, context: DetectionContext) -> List[Bug]

# crash_detector.py
class CrashDetector(BaseDetector):
    def detect(self, context: DetectionContext) -> List[Crash]
    def parse_stack_trace(self, logcat_lines: List[str]) -> StackTrace

# anr_detector.py
class ANRDetector(BaseDetector):
    def detect(self, context: DetectionContext) -> List[ANR]

# memory_monitor.py
class MemoryMonitor:
    def get_memory_usage(self, package: str) -> MemoryInfo
    def detect_leak(self) -> Optional[MemoryLeak]
    def start_monitoring(self) -> None
    def stop_monitoring(self) -> MemoryReport

# performance_monitor.py
class PerformanceMonitor:
    def get_fps(self) -> float
    def get_frame_stats(self) -> FrameStats
    def detect_jank(self) -> List[JankEvent]

# exception_parser.py
class ExceptionParser:
    def parse(self, log_line: str) -> Optional[Exception]
    def categorize(self, exception: Exception) -> ExceptionCategory
    def group_similar(self, exceptions: List[Exception]) -> List[ExceptionGroup]
```

**Dependencies**:
- Internal: `device`, `utils`
- External: `psutil`, `re`

---

### 3.5 Reporting Module (`smartmonkey.reporting`)

**Purpose**: Collect data and generate comprehensive reports

**Public API**:
```python
# data_collector.py
class DataCollector:
    def collect_event(self, event: Event) -> None
    def collect_bug(self, bug: Bug) -> None
    def collect_metric(self, metric: Metric) -> None
    def get_all_data(self) -> TestData

# report.py
class Report:
    summary: ReportSummary
    bugs: List[Bug]
    coverage: CoverageInfo
    performance: PerformanceInfo
    screenshots: List[str]

# report_generator.py
class ReportGenerator:
    def generate(self, data: TestData) -> Report
    def generate_html(self, report: Report, output_path: str) -> None
    def generate_json(self, report: Report, output_path: str) -> None
    def generate_markdown(self, report: Report, output_path: str) -> None

# visualization.py
class Visualization:
    def create_coverage_chart(self, coverage: CoverageInfo) -> Figure
    def create_timeline(self, events: List[Event]) -> Figure
    def create_bug_distribution(self, bugs: List[Bug]) -> Figure

# export_engine.py
class ExportEngine:
    def export(self, report: Report, format: str, output_path: str) -> None
    def register_exporter(self, format: str, exporter: Exporter) -> None

# statistics.py
class Statistics:
    def calculate_coverage(self, data: TestData) -> float
    def calculate_bug_density(self, data: TestData) -> float
    def calculate_exploration_efficiency(self, data: TestData) -> float
```

**Dependencies**:
- Internal: `exploration`, `detection`, `device`, `utils`
- External: `jinja2`, `matplotlib`, `pandas`

---

### 3.6 Utils Module (`smartmonkey.utils`)

**Purpose**: Common utilities and helpers

**Public API**:
```python
# logger.py
def setup_logger(level: str = "INFO") -> Logger
def get_logger(name: str) -> Logger

# exceptions.py
class SmartMonkeyException(Exception)
class DeviceConnectionError(SmartMonkeyException)
class ADBCommandError(SmartMonkeyException)
class UIParseError(SmartMonkeyException)
class ConfigurationError(SmartMonkeyException)

# helpers.py
def ensure_dir(path: str) -> None
def get_timestamp() -> str
def calculate_similarity(str1: str, str2: str) -> float
def compress_image(image_path: str, quality: int = 80) -> None

# constants.py
class EventType(Enum)
class BugType(Enum)
class ExplorationStrategy(Enum)
class DeviceState(Enum)
```

**Dependencies**:
- External: `loguru`, `pathlib`

---

### 3.7 CLI Module (`smartmonkey.cli`)

**Purpose**: Command-line interface for SmartMonkey

**Public API**:
```python
# main.py
@click.group()
def cli():
    """SmartMonkey - Intelligent Android App Testing"""

@cli.command()
@click.option('--config', '-c', help='Configuration file')
@click.option('--device', '-d', help='Device serial')
@click.option('--app', '-a', help='App package name')
def run(config, device, app):
    """Run SmartMonkey test"""

@cli.command()
@click.option('--device', '-d', help='Device serial')
def list_devices(device):
    """List connected devices"""

@cli.command()
@click.argument('report_path')
def view_report(report_path):
    """View test report"""
```

**Dependencies**:
- Internal: `core`, `utils`
- External: `click`

---

## 4. External Dependencies

### 4.1 Core Dependencies

```toml
# pyproject.toml

[tool.poetry.dependencies]
python = "^3.9"
adb-shell = "^0.4.3"           # Pure Python ADB implementation
lxml = "^4.9.3"                 # XML parsing
networkx = "^3.1"               # Graph representation
click = "^8.1.7"                # CLI framework
pyyaml = "^6.0.1"               # YAML configuration
loguru = "^0.7.0"               # Logging
jinja2 = "^3.1.2"               # Template engine
matplotlib = "^3.7.2"           # Visualization
pandas = "^2.0.3"               # Data analysis
Pillow = "^10.0.0"              # Image processing
psutil = "^5.9.5"               # System monitoring
tqdm = "^4.66.1"                # Progress bars
```

### 4.2 Development Dependencies

```toml
[tool.poetry.group.dev.dependencies]
pytest = "^7.4.0"               # Testing framework
pytest-cov = "^4.1.0"           # Test coverage
pytest-asyncio = "^0.21.1"      # Async testing
black = "^23.7.0"               # Code formatting
pylint = "^2.17.5"              # Linting
mypy = "^1.5.0"                 # Type checking
sphinx = "^7.1.2"               # Documentation
```

---

## 5. Module Interfaces

### 5.1 Plugin Interface

```python
# smartmonkey/core/plugin.py

class Plugin(ABC):
    """Base class for all SmartMonkey plugins"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name"""

    @property
    @abstractmethod
    def version(self) -> str:
        """Plugin version"""

    @abstractmethod
    def initialize(self, context: PluginContext) -> None:
        """Initialize plugin with context"""

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup plugin resources"""


class ExplorationStrategyPlugin(Plugin):
    """Plugin interface for custom exploration strategies"""

    @abstractmethod
    def next_action(self, state: AppState) -> Action:
        """Select next action based on current state"""


class DetectorPlugin(Plugin):
    """Plugin interface for custom bug detectors"""

    @abstractmethod
    def detect(self, context: DetectionContext) -> List[Bug]:
        """Detect bugs from current context"""


class ReportExporterPlugin(Plugin):
    """Plugin interface for custom report exporters"""

    @abstractmethod
    def export(self, report: Report, output_path: str) -> None:
        """Export report in custom format"""
```

---

## 6. Data Models

### 6.1 Core Data Structures

```python
# smartmonkey/models/

@dataclass
class Rect:
    left: int
    top: int
    right: int
    bottom: int

    @property
    def center(self) -> Tuple[int, int]:
        return ((self.left + self.right) // 2, (self.top + self.bottom) // 2)


@dataclass
class UIElement:
    resource_id: str
    class_name: str
    text: Optional[str]
    content_desc: Optional[str]
    bounds: Rect
    clickable: bool
    scrollable: bool
    visible: bool
    package: str
    index: int
    visit_count: int = 0


@dataclass
class AppState:
    activity: str
    elements: List[UIElement]
    screenshot_path: Optional[str]
    timestamp: datetime
    state_hash: str


@dataclass
class Bug:
    type: BugType
    severity: Severity
    title: str
    description: str
    stack_trace: Optional[str]
    screenshot_path: Optional[str]
    reproduction_steps: List[Action]
    timestamp: datetime


@dataclass
class TestData:
    start_time: datetime
    end_time: datetime
    device_info: DeviceInfo
    app_info: AppInfo
    events: List[Event]
    bugs: List[Bug]
    states: List[AppState]
    coverage: CoverageInfo
    performance: PerformanceInfo
```

---

## 7. Configuration Management

### 7.1 Configuration Hierarchy

```
Default Config (hardcoded)
    ↓
User Config File (~/.smartmonkey/config.yaml)
    ↓
Project Config (./smartmonkey_config.yaml)
    ↓
CLI Arguments (--option value)
    ↓
Final Merged Config
```

### 7.2 Configuration Schema

```python
# smartmonkey/core/config_schema.py

CONFIG_SCHEMA = {
    "general": {
        "app_package": {"type": str, "required": True},
        "max_events": {"type": int, "default": 1000},
        "timeout_seconds": {"type": int, "default": 3600},
        "exploration_strategy": {"type": str, "default": "weighted"}
    },
    "devices": {
        "type": list,
        "items": {
            "serial": {"type": str, "required": True},
            "nickname": {"type": str, "required": False}
        }
    },
    "exploration": {
        "enable_text_input": {"type": bool, "default": True},
        "text_input_samples": {"type": list, "default": []},
        "enable_swipe": {"type": bool, "default": True},
        "swipe_probability": {"type": float, "default": 0.2}
    },
    "detection": {
        "monitor_crashes": {"type": bool, "default": True},
        "monitor_anrs": {"type": bool, "default": True},
        "monitor_memory": {"type": bool, "default": True}
    },
    "reporting": {
        "output_dir": {"type": str, "default": "./reports"},
        "formats": {"type": list, "default": ["html", "json"]},
        "include_screenshots": {"type": bool, "default": True}
    }
}
```

---

## 8. Testing Strategy

### 8.1 Unit Tests
- Each module has dedicated unit tests
- Mock external dependencies (ADB, device)
- Aim for >80% code coverage

### 8.2 Integration Tests
- Test module interactions
- Use real or emulated Android devices
- Test end-to-end workflows

### 8.3 System Tests
- Full SmartMonkey execution on real apps
- Performance benchmarks
- Multi-device scenarios

---

## 9. Documentation Requirements

### 9.1 Code Documentation
- Docstrings for all public APIs (Google style)
- Type hints for all function signatures
- Inline comments for complex logic

### 9.2 API Documentation
- Auto-generated from docstrings using Sphinx
- API reference for all public modules
- Code examples for common use cases

### 9.3 User Documentation
- Installation guide
- Quick start tutorial
- Configuration reference
- Troubleshooting guide

---

**Next Steps**:
1. Set up project skeleton with directories
2. Create `pyproject.toml` with dependencies
3. Implement base classes and interfaces
4. Start with device layer implementation
5. Add unit tests incrementally

---

**Document Owner**: SmartMonkey Development Team
**Last Updated**: 2025-10-23

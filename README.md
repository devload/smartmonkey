<div align="center">

# SmartMonkey 🐵🧠

**Intelligent Android App Testing Tool with AI-Driven Testing & Grafana Dashboards**

[![Version](https://img.shields.io/badge/version-0.2.0-blue.svg)](https://github.com/yourusername/smartmonkey/releases/tag/v0.2.0)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Android-brightgreen.svg)](https://www.android.com/)
[![AI](https://img.shields.io/badge/AI-Claude_Code-purple.svg)](https://claude.ai/)

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Grafana Setup](#-grafana-dashboard-setup) • [Documentation](#-documentation)

</div>

---

## 🎯 What is SmartMonkey?

SmartMonkey is an **intelligent Android app testing tool** that goes beyond traditional random monkey testing. It supports **three testing modes**: **Native Mobile Apps**, **Web Apps**, and **AI-Driven Testing** powered by Claude Code. SmartMonkey intelligently tests your applications with beautiful **Grafana dashboards** for visualization.

### 🤖 How It Works

**Traditional Testing:**
- **📊 Weighted Strategy**: Prioritizes unvisited UI elements (10x weight) to maximize code coverage
- **🎯 Smart Targeting**: Bonus scoring for buttons (1.5x) and submit actions (2x)
- **🔍 State Detection**: MD5 hashing to avoid duplicate states
- **💥 Crash Detection**: Automatically detects when app exits or moves to background
- **📸 Visual Documentation**: Screenshots at every step with Grafana gallery

**AI-Driven Testing (NEW! 🚀):**
- **🧠 Vision-Based Analysis**: Claude Code analyzes screenshots to understand UI context
- **🎯 Mission-Oriented**: AI follows specific missions like "Browse products and add to cart"
- **🤝 Smart Decision Making**: Judges popup/ad relevance based on mission context
- **🔧 Auto-Correction**: Automatic coordinate correction for system permission dialogs
- **📱 Universal Support**: Works with both native apps and web apps

---

## ✨ Features

### 🤖 AI-Driven Testing (NEW! v0.2.0)
- **Claude Code Integration**: Vision-based screen analysis using Claude Code CLI
- **Mission-Oriented Testing**: Define testing goals like "Search and add products to cart"
- **Intelligent Popup Handling**: AI judges if popups/ads are relevant to mission
- **Hybrid Precision**: Combines AI vision with UI hierarchy for accurate coordinates
- **Context-Aware Decisions**: AI reads screen content and makes smart navigation choices
- **Dual Mode Support**: Works with native Android apps AND web applications

### 📱 Native Mobile App Testing
- **Weighted Strategy**: Unvisited elements get 10x priority
- **Context-Aware**: Recognizes buttons, text fields, and interactive elements
- **State Hashing**: Avoids testing duplicate UI states
- **ADB Integration**: Direct device communication via Android Debug Bridge

### 🌐 Web App Testing
- **Chrome DevTools Protocol**: Direct DOM inspection and manipulation
- **Visual Markers**: Click positions (red crosshair) and swipe gestures
- **Smart Scrolling**: Automatic scroll when elements are off-screen
- **Overlay Detection**: Detects and closes modals/menus automatically

### 💥 Crash Detection
- **Real-time Monitoring**: Detects when app stops running or moves to background
- **Empty State Detection**: Identifies UI deadlocks
- **Detailed Reports**: Full crash context with screenshots

### 📊 Grafana Dashboard Integration
- **Beautiful Visualizations**: Interactive test result dashboards
- **Screenshot Gallery**: Scrollable gallery of all test screenshots
- **Test History**: Track multiple test runs over time
- **Drill-Down Navigation**: Click test ID to view detailed results

### 🔧 Developer-Friendly
- **Full CLI Parameters**: Device, package, steps, strategy all configurable
- **Multi-device Support**: Works with physical devices and emulators
- **JSON & Text Reports**: Both machine and human-readable formats
- **Dual Mode**: Native Android apps + Web apps testing

---

## 📸 Screenshots

### Grafana Dashboard - Test Runs Overview
![Main Dashboard](docs/images/grafana-main-dashboard.png)
*View all test runs with status, duration, and crash detection*

### Grafana Dashboard - Test Detail with Screenshot Gallery
![Detail Dashboard](docs/images/grafana-detail-dashboard.png)
*Interactive screenshot gallery and detailed test metrics*

---

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- Android SDK with ADB installed
- At least one Android device or emulator connected

### Install SmartMonkey

```bash
# Clone the repository
git clone https://github.com/yourusername/smartmonkey.git
cd smartmonkey

# Install dependencies
pip install -r requirements.txt

# Set PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH

# Verify installation
python3 -m smartmonkey.cli.main --version
```

---

## 🏃 Quick Start

### 1. List Connected Devices

```bash
python3 -m smartmonkey.cli.main devices
```

**Output:**
```
Available devices:
  - emulator-5556 (sdk_gphone64_arm64)
  - RFCX919P8ZF (Samsung SM-A356N)
```

### 2. Run AI-Driven Testing (NEW! 🚀)

**Test a Native Android App:**
```bash
python3 -m smartmonkey.cli.main ai \
  --device emulator-5556 \
  --package com.coupang.mobile \
  --mission "쿠팡에서 다양한 상품을 둘러보기" \
  --steps 10
```

**Test a Mobile Website:**
```bash
python3 -m smartmonkey.cli.main ai \
  --device emulator-5556 \
  --url https://www.coupang.com \
  --mission "상품 검색하고 장바구니 담기" \
  --steps 10
```

**How AI Testing Works:**
- 🧠 AI analyzes screenshots to understand the current screen
- 🎯 Makes decisions based on the mission you provide
- 🤝 Smart popup handling: Closes irrelevant ads, explores relevant content
- 🔧 Auto-corrects coordinates for system permission dialogs
- 📝 Generates detailed action history with reasoning

### 3. Run a Native App Test (Traditional)

```bash
python3 -m smartmonkey.cli.main mobile \
  --device emulator-5556 \
  --package com.android.settings \
  --steps 20
```

### 4. Run a Web App Test (Traditional)

```bash
# Test a mobile website
python3 -m smartmonkey.cli.main web \
  --device emulator-5556 \
  --url https://m.naver.com \
  --steps 10
```

**Features:**
- ✅ Captures starting page before any actions
- ✅ Visual markers on screenshots (clicks & swipes)
- ✅ Smart scrolling when elements are off-screen
- ✅ Detects and closes overlays/modals automatically

### 5. Run Multiple Tests

```bash
# Run 5 tests with 20 steps each
for i in {1..5}; do
  python3 -m smartmonkey.cli.main mobile \
    --device emulator-5556 \
    --package io.whatap.session.sample \
    --steps 20 \
    --output ./reports/test_run_$(printf "%03d" $i)
  sleep 2
done
```

---

## 📖 CLI Parameters

### AI-Driven Testing (NEW! 🚀)

**Full Command Syntax:**
```bash
python3 -m smartmonkey.cli.main ai [OPTIONS]
```

**Available Options:**

| Parameter | Short | Description | Default | Required |
|-----------|-------|-------------|---------|----------|
| `--device` | `-d` | Device serial number | `emulator-5554` | No |
| `--package` | `-pkg` | App package name (for app testing) | - | One of `--package` or `--url` required |
| `--url` | `-u` | Starting URL (for web testing) | - | One of `--package` or `--url` required |
| `--mission` | `-m` | Mission to accomplish | - | **Yes** |
| `--steps` | `-s` | Maximum number of steps | 5 | No |
| `--port` | `-p` | Chrome DevTools port (web mode only) | 9222 | No |
| `--output` | `-o` | Output directory path | `./reports` | No |

**Mission Examples:**
- `"쿠팡에서 다양한 상품을 둘러보기"`
- `"상품 검색하고 장바구니 담기"`
- `"Browse products and add to cart"`
- `"네이버에서 뉴스 읽기"`

**AI Testing Features:**
- 🧠 **Vision-Based**: AI analyzes screenshots to understand UI
- 🎯 **Mission-Oriented**: Follows your specific testing goals
- 🤝 **Smart Decisions**: Judges popup relevance to mission
- 🔧 **Auto-Correction**: Fixes permission dialog coordinates
- 📝 **Detailed Logging**: Explains reasoning for each action

### Native Mobile App Testing

**Full Command Syntax:**
```bash
python3 -m smartmonkey.cli.main mobile [OPTIONS]
```

**Available Options:**

| Parameter | Short | Description | Default | Required |
|-----------|-------|-------------|---------|----------|
| `--device` | `-d` | Device serial number | Auto-detect | No* |
| `--package` | `-p` | App package name | - | **Yes** |
| `--steps` | `-s` | Maximum number of steps | 50 | No |
| `--output` | `-o` | Output directory path | `./reports/<timestamp>` | No |

\* Required if multiple devices are connected

### Web App Testing

**Full Command Syntax:**
```bash
python3 -m smartmonkey.cli.main web [OPTIONS]
```

**Available Options:**

| Parameter | Short | Description | Default | Required |
|-----------|-------|-------------|---------|----------|
| `--device` | `-d` | Device serial number | Auto-detect | No* |
| `--url` | `-u` | Starting URL to test | - | **Yes** |
| `--steps` | `-s` | Maximum number of actions | 10 | No |
| `--output` | `-o` | Output directory path | `./reports` | No |

\* Required if multiple devices are connected

**Web Testing Features:**
- 📸 **Initial Screenshot**: Captures starting page before any actions
- 🎯 **Visual Markers**: Red crosshair for clicks, green→blue arrow for swipes
- 📜 **Smart Scrolling**: Auto-scrolls when elements are off-screen
- 🚪 **Overlay Detection**: Detects and closes modals/menus automatically
- 📊 **Independent Steps**: Swipes count as separate steps with their own screenshots

### Examples

#### AI - Test Native Android App
```bash
# E-commerce app testing
python3 -m smartmonkey.cli.main ai \
  -d emulator-5556 \
  -pkg com.coupang.mobile \
  -m "쿠팡에서 다양한 상품을 둘러보기" \
  -s 10

# Settings exploration
python3 -m smartmonkey.cli.main ai \
  -d emulator-5556 \
  -pkg com.android.settings \
  -m "앱 설정 둘러보기" \
  -s 5
```

#### AI - Test Mobile Website
```bash
# E-commerce site
python3 -m smartmonkey.cli.main ai \
  -d emulator-5556 \
  -u https://www.coupang.com \
  -m "상품 검색하고 장바구니 담기" \
  -s 10

# News site
python3 -m smartmonkey.cli.main ai \
  -d emulator-5556 \
  -u https://m.naver.com \
  -m "네이버에서 뉴스 읽기" \
  -s 5
```

#### Native App - Basic Test (Auto-detect device)
```bash
python3 -m smartmonkey.cli.main mobile -p com.example.app
```

#### Native App - Specify All Parameters
```bash
python3 -m smartmonkey.cli.main mobile \
  --device emulator-5556 \
  --package com.example.app \
  --steps 100 \
  --output ./my_test_results
```

#### Web - Test Mobile Website
```bash
# Basic web test
python3 -m smartmonkey.cli.main web -d emulator-5556 -u https://m.naver.com -s 10

# Test e-commerce site
python3 -m smartmonkey.cli.main web -d emulator-5556 -u https://m.shopping.naver.com -s 20

# Test with custom output directory
python3 -m smartmonkey.cli.main web \
  --device emulator-5556 \
  --url https://m.naver.com \
  --steps 15 \
  --output ./web_tests/naver_test
```

---

## 📊 Grafana Dashboard Setup

### Step 1: Install Grafana

```bash
# macOS
brew install grafana
brew services start grafana

# Linux (Ubuntu/Debian)
sudo apt-get install -y adduser libfontconfig1
wget https://dl.grafana.com/oss/release/grafana_10.0.0_amd64.deb
sudo dpkg -i grafana_10.0.0_amd64.deb
sudo systemctl start grafana-server

# Access Grafana
open http://localhost:3000  # Default: admin/admin
```

### Step 2: Install Required Plugins

1. Go to **Configuration** → **Plugins**
2. Install **Infinity Data Source** plugin
3. Install **HTML Graphics Panel** plugin (gapit-htmlgraphics-panel)

### Step 3: Configure Data Source

1. Go to **Connections** → **Data sources** → **Add data source**
2. Search and select **Infinity**
3. Name it (e.g., "SmartMonkey Reports")
4. Click **Save & Test**

### Step 4: Start HTTP Server for Reports

```bash
cd /path/to/smartmonkey/reports
python3 -m http.server 8000
```

Keep this running in a separate terminal.

### Step 5: Import Dashboards

#### Import Main Dashboard (Test List)

1. Go to **Dashboards** → **Import**
2. Click **Upload JSON file**
3. Select `grafana/dashboard-main.json`
4. Select your Infinity data source
5. Click **Import**

#### Import Detail Dashboard (Test Results)

1. Go to **Dashboards** → **Import**
2. Click **Upload JSON file**
3. Select `grafana/dashboard-detail.json`
4. Select your Infinity data source
5. Click **Import**

### Step 6: View Results

1. Open **SmartMonkey - Test Runs** dashboard
2. You'll see a list of all test runs
3. Click on any **Test ID** to drill down to detailed results
4. Browse the screenshot gallery and test metrics

---

## 📂 Project Structure

```
smartmonkey/
├── smartmonkey/              # Main package
│   ├── cli/                  # CLI interface
│   │   ├── main.py          # Command-line entry point
│   │   └── commands/        # CLI command modules
│   │       ├── ai_command.py      # AI-driven testing (NEW!)
│   │       ├── mobile_command.py  # Native app testing
│   │       └── web_command.py     # Web app testing
│   ├── ai/                   # AI-driven testing (NEW! 🚀)
│   │   ├── claude_code_client.py  # Claude Code CLI integration
│   │   └── templates/       # AI prompt templates
│   │       ├── app_claude.md      # Android app testing guide
│   │       └── web_claude.md      # Web testing guide
│   ├── device/               # Device communication (ADB)
│   │   ├── adb_manager.py   # ADB wrapper
│   │   ├── app_manager.py   # App lifecycle management
│   │   ├── device.py        # Device abstraction
│   │   └── event_manager.py # Touch/swipe events
│   ├── exploration/          # UI exploration & strategies
│   │   ├── element.py       # UI element representation
│   │   ├── exploration_engine.py  # Main exploration logic
│   │   ├── state.py         # UI state management
│   │   ├── ui_parser.py     # UIAutomator parser
│   │   └── strategies/      # Exploration strategies
│   │       ├── base.py           # Base strategy
│   │       ├── random.py         # Random strategy
│   │       ├── weighted.py       # Weighted strategy
│   │       └── ai_strategy.py    # AI strategy (NEW!)
│   ├── web/                  # Web testing (Chrome DevTools)
│   │   ├── chrome_controller.py  # Chrome DevTools Protocol
│   │   └── web_navigator.py      # Web navigation logic
│   ├── reporting/            # Report generation
│   │   └── report_generator.py  # JSON/Text reports
│   └── utils/                # Utilities
│       ├── logger.py        # Logging setup
│       ├── helpers.py       # Helper functions
│       └── exceptions.py    # Custom exceptions
├── grafana/                  # Grafana dashboard configs
│   ├── dashboard-main.json   # Test list dashboard
│   └── dashboard-detail.json # Test detail dashboard
├── docs/                     # Documentation
│   ├── design/               # Design documents
│   └── images/               # Screenshots
├── reports/                  # Generated test reports (gitignored)
├── requirements.txt          # Python dependencies
├── pyproject.toml            # Project metadata
├── .gitignore                # Git ignore rules
└── README.md                 # This file
```

---

## 🧪 Test Report Structure

### Generated Files

After running a test, the following structure is created:

```
reports/
├── index.json                     # Test runs index (for Grafana)
└── test_run_001/
    ├── report.json                # Structured test data
    ├── report.txt                 # Human-readable summary
    └── screenshots/
        ├── screenshot_0000.png    # Step 0 screenshot
        ├── screenshot_0001.png    # Step 1 screenshot
        └── ...
```

### report.json Schema

```json
{
  "start_time": "2025-10-24T10:33:31.743373",
  "end_time": "2025-10-24T10:35:00.084500",
  "duration_seconds": 88.341127,
  "total_events": 20,
  "unique_states": 13,
  "total_states": 20,
  "crash_detected": false,
  "crash_info": null,
  "states": [
    {
      "step": 0,
      "timestamp": 1761201226.080551,
      "datetime": "2025-10-24T10:33:31.743373",
      "activity": "io.whatap.session.sample.Screen1Activity",
      "element_count": 17,
      "state_hash": "f0d3dd1f...",
      "screenshot": "./screenshots/screenshot_0000.png",
      "screenshot_url": "http://localhost:8000/test_run_001/screenshots/screenshot_0000.png"
    }
  ],
  "actions": [
    {
      "step": 0,
      "timestamp": 1761201227.0,
      "type": "tap",
      "repr": "TapAction(element=Button, text='GO TO SCREEN 2')"
    }
  ]
}
```

### report.txt Example

```
============================================================
SmartMonkey Exploration Report
============================================================

Start Time: 2025-10-24 10:33:31
End Time: 2025-10-24 10:35:00
Duration: 88.3 seconds

Total Events: 20
Unique States: 13
Total States Visited: 20

States Explored:
------------------------------------------------------------
  1. Screen1Activity (2 elements)
  2. Screen2Activity (3 elements)
  3. Screen3Activity (2 elements)
  ...

Actions Performed:
------------------------------------------------------------
  tap: 15
  back: 3
  swipe_up: 2
```

---

## 🎯 Exploration Strategies

### AI Strategy (NEW! 🚀)
- **Vision-based analysis**: Claude Code analyzes screenshots to understand UI context
- **Mission-oriented**: Follows specific testing goals you define
- **Context-aware decisions**: Reads text, identifies UI elements, judges relevance
- **Smart popup handling**: Closes irrelevant ads, explores mission-relevant content
- **Hybrid precision**: Combines AI vision with UI hierarchy for accurate tapping
- **Recommended for**: Complex scenarios, mission-based testing, realistic user flows
- **Use case**: E-commerce testing, onboarding flows, form completion

### Weighted Strategy (Traditional)
- **Prioritizes unvisited elements**: 10x weight for new elements
- **Better coverage**: Explores unique UI states more thoroughly
- **Smart targeting**: Bonus for buttons and submit actions
- **Recommended for**: Thorough testing and code coverage
- **Use case**: Systematic exploration of app features

### Random Strategy (Traditional)
- **Random selection**: Picks any clickable element randomly
- **Faster execution**: No state tracking overhead
- **Good for**: Quick smoke testing and chaos engineering
- **Use case**: Finding unexpected crashes

---

## 🐛 Troubleshooting

### Issue: "No devices found"

```bash
# Check ADB connection
adb devices

# If no devices shown, restart ADB
adb kill-server
adb start-server

# Check device is authorized
adb devices
# Should show "device" not "unauthorized"
```

### Issue: "App crashes immediately"

```bash
# Check app is installed
adb shell pm list packages | grep <package>

# Launch app manually first
adb shell am start -n <package>/.MainActivity

# Check logcat for errors
adb logcat | grep <package>
```

### Issue: "Grafana shows 'No data'"

1. **Check HTTP server is running**:
   ```bash
   curl http://localhost:8000/index.json
   ```

2. **Verify Data Source URL**:
   - Should be `http://localhost:8000/`
   - Check Grafana Data Source settings

3. **Check browser console**: F12 → Console tab for errors

### Issue: "Screenshots not loading in Grafana"

1. **Verify image URLs are accessible**:
   ```bash
   curl -I http://localhost:8000/test_run_001/screenshots/screenshot_0000.png
   ```

2. **Check CORS settings**: HTTP server should allow cross-origin requests

3. **Refresh Grafana dashboard**: Click refresh button or Ctrl+R

---

## 📝 Example: Real Test Results

```bash
# Test Configuration
Device: Emulator (emulator-5556)
Package: io.whatap.session.sample
Steps: 20
Strategy: weighted
Duration: 88.3 seconds

# Results
✅ Total Events: 20
✅ Unique States: 13
✅ Screenshots: 20
✅ Status: Passed

# Actions Breakdown
tap: 15 (75%)
back: 3 (15%)
swipe_up: 2 (10%)
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🗺️ Roadmap

### v0.2.0 (✅ Completed - 2025-11-03)
- ✅ AI-driven testing with Claude Code integration
- ✅ Vision-based screen analysis
- ✅ Mission-oriented testing for apps and web
- ✅ Smart popup/ad handling with context awareness
- ✅ Hybrid coordinate precision (AI + UI hierarchy)
- ✅ Native mobile app testing (refactored CLI)
- ✅ Web app testing with Chrome DevTools

### v0.3.0 (Planned)
- [ ] Enhanced AI strategies (multi-step planning)
- [ ] AI learning from test failures
- [ ] Crash/ANR detection layer enhancements
- [ ] HTML report generation with AI insights
- [ ] Performance monitoring (FPS, memory, CPU)

### v0.4.0+ (Future)
- [ ] Multi-agent AI testing (parallel exploration)
- [ ] Custom AI prompt templates
- [ ] Configuration file support (YAML)
- [ ] Code coverage tracking
- [ ] CI/CD integration (GitHub Actions, Jenkins)
- [ ] Cloud testing support

---

## 🙏 Acknowledgments

- **Claude Code (Anthropic)** - AI-driven vision-based testing and screen analysis
- **Android Debug Bridge (ADB)** - Device communication and control
- **Chrome DevTools Protocol** - Web app testing and DOM manipulation
- **UIAutomator** - UI hierarchy parsing
- **Grafana** - Data visualization platform
- **Infinity Data Source** - JSON data loading for Grafana
- **HTML Graphics Panel** - Screenshot gallery rendering

---

## 📬 Contact

- **GitHub**: [yourusername/smartmonkey](https://github.com/yourusername/smartmonkey)
- **Issues**: [Report bugs or request features](https://github.com/yourusername/smartmonkey/issues)

---

<div align="center">

**Made with ❤️ by SmartMonkey Team**

⭐ Star this repo if you find it useful!

</div>

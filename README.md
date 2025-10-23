<div align="center">

<img src="assets/logo.png" alt="SmartMonkey Logo" width="200"/>

# SmartMonkey 🐵🧠

**Intelligent Android App Testing Tool**

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Android-brightgreen.svg)](https://www.android.com/)

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation) • [Contributing](#-contributing)

</div>

---

## 🎯 What is SmartMonkey?

SmartMonkey is an **intelligent Android app testing tool** that goes beyond traditional random monkey testing. While MonkeyRunner clicks randomly, SmartMonkey uses a **weighted exploration strategy** to intelligently test your Android applications.

### 🤖 How It Works

SmartMonkey leverages Android's UIAutomator to understand your app's UI structure and makes intelligent decisions about what to test:

- **📊 Weighted Strategy**: Prioritizes unvisited UI elements (10x weight) to maximize code coverage
- **🎯 Smart Targeting**: Bonus scoring for buttons (1.5x) and submit actions (2x)
- **🔍 State Detection**: MD5 hashing to avoid duplicate states
- **💥 Crash Detection**: Automatically detects and reports app crashes
- **📸 Visual Documentation**: Screenshots at every step for debugging

### ⚡ SmartMonkey vs MonkeyRunner

| Feature | MonkeyRunner | SmartMonkey |
|---------|--------------|-------------|
| Strategy | 🎲 Random clicks | 🧠 Intelligent weighted exploration |
| Coverage | ❌ Low (repeats same paths) | ✅ High (prioritizes unvisited states) |
| Crash Detection | ❌ Continues after crash | ✅ Detects and reports crashes |
| Reporting | 📝 Basic logs | 📊 Detailed JSON/Text reports |
| Screenshots | ❌ Manual | ✅ Automatic at each step |
| Multi-device | ⚠️ Limited | ✅ Full support |

---

## ✨ Features

### 🎯 Intelligent Exploration
- **Weighted Strategy**: Unvisited elements get 10x priority
- **Context-Aware**: Recognizes buttons, text fields, and interactive elements
- **State Hashing**: Avoids testing duplicate UI states

### 💥 Crash Detection
- **Real-time Monitoring**: Detects when app stops running
- **Empty State Detection**: Identifies UI deadlocks
- **Detailed Reports**: Full crash context with screenshots

### 📊 Comprehensive Reporting
- **JSON Reports**: Machine-readable exploration data
- **Text Reports**: Human-friendly summaries
- **Screenshots**: Visual documentation of every step
- **Metrics**: States visited, actions performed, coverage stats

### 🔧 Developer-Friendly
- **Easy CLI**: Simple command-line interface
- **Multi-device Support**: Works with physical devices and emulators
- **Extensible**: Plugin-based architecture for custom strategies

---

## 🚀 Installation

### Prerequisites

- Python 3.9 or higher
- Android SDK with ADB installed
- Connected Android device or emulator with USB debugging enabled

### Install SmartMonkey

```bash
# Clone the repository
git clone https://github.com/yourusername/smartmonkey.git
cd smartmonkey

# Install dependencies
pip install click lxml loguru

# Set PYTHONPATH
export PYTHONPATH=$(pwd):$PYTHONPATH

# Verify installation
python -m smartmonkey.cli.main --version
```

---

## 🏃 Quick Start

### 1. Check Connected Devices

```bash
python -m smartmonkey.cli.main list-devices
```

**Output:**
```
Found 2 device(s):

1. emulator-5554
   Model: sdk_gphone64_arm64
   Android: 13
   Manufacturer: Google

2. RFCX919P8ZF
   Model: SM-A356N
   Android: 14
   Manufacturer: Samsung
```

### 2. Run Exploration

```bash
# Basic usage (auto-selects device if only one connected)
python -m smartmonkey.cli.main run -p com.example.myapp

# Specify device, steps, and strategy
python -m smartmonkey.cli.main run \
  --device emulator-5554 \
  --package com.example.myapp \
  --steps 100 \
  --strategy weighted \
  --output ./my-test-results
```

### 3. View Results

```bash
# Reports are saved to ./reports/<timestamp>/ by default
ls reports/

# View text report
cat reports/20251023_103454/report.txt

# View JSON report
cat reports/20251023_103454/report.json

# View screenshots
open reports/20251023_103454/screenshots/
```

---

## 📖 Documentation

### Command-Line Options

```bash
python -m smartmonkey.cli.main run --help

Options:
  -d, --device TEXT            Device serial (auto-detect if one device)
  -p, --package TEXT           App package name [required]
  -n, --steps INTEGER          Maximum steps (default: 50)
  -s, --strategy [random|weighted]  Exploration strategy (default: weighted)
  -o, --output TEXT            Output directory (default: ./reports/<timestamp>)
  --screenshots/--no-screenshots  Save screenshots (default: yes)
```

### Example Report

**Text Report:**
```
============================================================
SmartMonkey Exploration Report
============================================================

Start Time: 2025-10-23 10:34:54
End Time: 2025-10-23 10:35:02
Duration: 7.4 seconds

Total Events: 15
Unique States: 8
Total States Visited: 15

🔴 CRASH DETECTED!
------------------------------------------------------------
Crash Info: App stopped running after step 12

States Explored:
------------------------------------------------------------
  1. MainActivity (21 elements)
  2. LoginActivity (15 elements)
  3. HomeActivity (32 elements)
  ...
```

### Architecture

SmartMonkey uses a modular architecture:

```
smartmonkey/
├── device/          # ADB communication layer
├── exploration/     # UI parsing and exploration strategies
├── reporting/       # Report generation
├── utils/          # Logging and helpers
└── cli/            # Command-line interface
```

---

## 🛠️ Advanced Usage

### Custom Exploration Strategy

```python
from smartmonkey.exploration.strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def select_action(self, state, visited_states):
        # Your custom logic here
        pass
```

### Programmatic API

```python
from smartmonkey.device.device import Device
from smartmonkey.exploration.exploration_engine import ExplorationEngine
from smartmonkey.exploration.strategies.weighted_strategy import WeightedStrategy

device = Device("emulator-5554")
device.connect()

strategy = WeightedStrategy()
engine = ExplorationEngine(
    device=device,
    strategy=strategy,
    package="com.example.myapp",
    screenshot_dir="./screenshots"
)

result = engine.explore(max_steps=100)
print(f"Explored {result.unique_states} unique states")
```

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

```bash
# Clone the repo
git clone https://github.com/yourusername/smartmonkey.git
cd smartmonkey

# Set up development environment
export PYTHONPATH=$(pwd):$PYTHONPATH

# Run tests (coming soon)
pytest tests/
```

### Roadmap

- [ ] Machine learning-based exploration strategies
- [ ] Code coverage integration
- [ ] Performance profiling
- [ ] Network traffic monitoring
- [ ] CI/CD integration (GitHub Actions, Jenkins)
- [ ] Web dashboard for test results

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- Built with ❤️ using Python and ADB
- Inspired by Google's MonkeyRunner but smarter
- Logo designed with AI assistance

---

<div align="center">

**Made with 🧠 by [Your Name]**

⭐ Star this repo if you find it useful!

[Report Bug](https://github.com/yourusername/smartmonkey/issues) • [Request Feature](https://github.com/yourusername/smartmonkey/issues)

</div>

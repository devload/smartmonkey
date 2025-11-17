# Changelog

All notable changes to SmartMonkey will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.1] - 2025-11-06

### Added
- **MCP (Model Context Protocol) Integration** 🔌
  - Full MCP server implementation for Claude Desktop integration
  - Natural language testing interface: "Test Coupang app with mission: browse products"
  - 4 MCP tools:
    - `list_devices` - List connected Android devices
    - `run_ai_test` - AI-driven testing with mission
    - `run_mobile_test` - Traditional mobile app testing
    - `run_web_test` - Web app testing with Chrome DevTools
  - Background test execution with test_id tracking
  - Comprehensive MCP documentation:
    - `docs/MCP_SETUP.md` - Setup and configuration guide
    - `docs/MCP_TESTING.md` - Testing guide and troubleshooting

### Changed
- **Python Version Requirements**: Now requires Python 3.10+ (3.12+ recommended)
  - MCP SDK requires Python 3.10 or higher
  - Updated all documentation to reflect new requirements
- **Project Status**: Upgraded from Alpha to Beta
- Updated README with enhanced MCP section and examples
- Updated landing page with MCP feature card
- Enhanced documentation structure with MCP guides

### Fixed
- Fixed `handle_list_devices` handler to use correct `get_devices()` method
- Tested MCP integration with real devices (VIVO V2041, Samsung SM-A356N)

## [0.2.0] - 2025-11-03

### Added
- **AI-Driven Testing** 🤖
  - Claude Code integration for vision-based screen analysis
  - Mission-oriented testing: Define goals in natural language
  - Smart popup/ad handling based on mission context
  - Hybrid coordinate precision (AI + UI hierarchy)
  - Auto-correction for system permission dialogs
  - Support for both native apps and web apps
- **Native Mobile App Testing**
  - Refactored CLI with `mobile` command
  - Weighted exploration strategy (10x priority for unvisited elements)
  - State detection with MD5 hashing
  - Real-time crash detection
- **Web App Testing**
  - Chrome DevTools Protocol integration
  - Visual markers (red crosshair for clicks, green→blue arrows for swipes)
  - Smart scrolling for off-screen elements
  - Automatic overlay/modal detection and handling
- **Grafana Dashboard Integration**
  - Beautiful visualization of test results
  - Interactive screenshot gallery
  - Test history tracking
  - Drill-down navigation
- **Documentation**
  - Comprehensive README with all testing modes
  - AI testing prompt templates
  - Grafana setup guide
  - Landing page at https://devload.github.io/smartmonkey/

### Changed
- Restructured CLI: separate commands for `ai`, `mobile`, and `web` testing
- Enhanced reporting with both JSON and text formats
- Improved screenshot capture with visual markers for web testing

## [0.1.0] - 2025-10-23

### Added
- **Initial Release** 🎉
- Core device layer (ADB integration)
  - Device connection and management
  - Event injection (tap, swipe, back)
  - Screenshot capture and compression
- UI exploration layer
  - UI hierarchy parsing (uiautomator)
  - State management with hashing
  - Random and weighted exploration strategies
- Basic reporting
  - JSON report generation
  - Text summary reports
  - Screenshot collection
- CLI interface
  - `devices` command - List connected devices
  - `run` command - Execute tests
- Multi-device support
  - Physical devices
  - Android emulators

### Technical Details
- Python 3.9+ support
- ADB-based device communication
- UIAutomator XML parsing
- NetworkX for state graph representation

---

## Version History

- **v0.2.1** (2025-11-06) - MCP Integration & Python 3.10+ support
- **v0.2.0** (2025-11-03) - AI-Driven Testing & Grafana Dashboards
- **v0.1.0** (2025-10-23) - Initial Release

---

## Upgrade Guide

### From 0.2.0 to 0.2.1

**Python Version Update Required:**

If you're using Python 3.9, you must upgrade to Python 3.10+ to use MCP features:

```bash
# Install Python 3.12 (recommended)
brew install python@3.12

# Create new virtual environment
python3.12 -m venv ~/.venv/smartmonkey-mcp
source ~/.venv/smartmonkey-mcp/bin/activate

# Reinstall SmartMonkey
pip install -e .
```

**New MCP Features:**

To use MCP integration with Claude Desktop:

1. Install MCP SDK: `pip install 'mcp>=0.9.0'`
2. Configure Claude Desktop (see `docs/MCP_SETUP.md`)
3. Restart Claude Desktop
4. Start testing with natural language!

### From 0.1.0 to 0.2.0

**CLI Command Changes:**

The CLI structure has been reorganized:

```bash
# Old (v0.1.0)
python3 -m smartmonkey.cli.main run -p com.example.app

# New (v0.2.0+)
python3 -m smartmonkey.cli.main mobile -p com.example.app
python3 -m smartmonkey.cli.main ai -pkg com.example.app -m "Browse the app"
python3 -m smartmonkey.cli.main web -u https://example.com
```

---

## Future Roadmap

### v0.3.0 (Planned)
- [ ] Enhanced AI strategies (multi-step planning)
- [ ] AI learning from test failures
- [ ] HTML report generation with AI insights
- [ ] Performance monitoring (FPS, memory, CPU)
- [ ] MCP tools: `get_results`, `stop_test`, `get_logs`

### v0.4.0+ (Future)
- [ ] Multi-agent AI testing
- [ ] Custom AI prompt templates
- [ ] Configuration file support (YAML)
- [ ] Code coverage tracking
- [ ] CI/CD integration
- [ ] Cloud testing support

---

For full documentation, visit: https://github.com/devload/smartmonkey

# Integration Guide: Adding Chrome DOM to SmartMonkey

This guide shows how to integrate Chrome DOM extraction into SmartMonkey's existing exploration engine and CLI.

## Architecture Overview

```
SmartMonkey Core
    ├── Device Layer
    │   ├── adb_manager.py (existing)
    │   ├── device.py (existing)
    │   └── chrome_manager.py (NEW)
    │
    ├── Exploration Layer
    │   ├── ui_parser.py (existing - native UI)
    │   ├── html_parser.py (NEW - Chrome DOM)
    │   ├── exploration_engine.py (can be extended)
    │   └── strategies/
    │       ├── random_strategy.py
    │       ├── weighted_strategy.py
    │       └── web_strategy.py (NEW)
    │
    └── CLI Layer
        └── main.py (can add --web-only flag)
```

## Step 1: Extend Device Class

Add Chrome DOM support to the `Device` class:

**File:** `/Users/devload/smartMonkey/smartmonkey/device/device.py`

```python
# Add to imports
from typing import Optional, List, Union
from .chrome_manager import ChromeDevToolsManager
from ..exploration.html_parser import HTMLParser, DOMNode

# Add to Device class

async def get_chrome_elements(self) -> List[DOMNode]:
    """
    Get HTML DOM elements from Chrome browser

    Returns:
        List of clickable DOM nodes

    Raises:
        RuntimeError: If Chrome connection fails
    """
    from ..utils.logger import get_logger
    logger = get_logger(__name__)

    try:
        cdp = ChromeDevToolsManager()
        if not await cdp.connect():
            logger.error("Failed to connect to Chrome DevTools")
            return []

        try:
            parser = HTMLParser(cdp)
            elements = await parser.get_clickable_elements()
            logger.debug(f"Extracted {len(elements)} Chrome DOM elements")
            return elements
        finally:
            await cdp.disconnect()

    except Exception as e:
        logger.error(f"Failed to get Chrome elements: {e}")
        return []

def is_chrome_active(self) -> bool:
    """
    Check if Chrome is the active foreground app

    Returns:
        True if Chrome is active
    """
    try:
        current_focus = self.adb.shell(
            "dumpsys window windows | grep 'mCurrentFocus'"
        )
        return "com.android.chrome" in current_focus
    except:
        return False

def get_current_app(self) -> str:
    """
    Get current foreground application package

    Returns:
        Package name
    """
    try:
        current_focus = self.adb.shell(
            "dumpsys window windows | grep 'mCurrentFocus'"
        )
        # Extract package from output like: mCurrentFocus=Window{... com.app.name/...}
        import re
        match = re.search(r'(\S+/\S+)', current_focus)
        if match:
            return match.group(1).split('/')[0]
    except:
        pass
    return ""
```

## Step 2: Create Web Exploration Strategy

Create a new strategy specifically for web content:

**File:** `/Users/devload/smartMonkey/smartmonkey/exploration/strategies/web_strategy.py`

```python
"""Web content exploration strategy using Chrome DOM"""

import asyncio
import random
from typing import List, Optional
import logging

from .base import ExplorationStrategy
from ..html_parser import HTMLParser, DOMNode
from ...device.chrome_manager import ChromeDevToolsManager
from ...device.device import Device

logger = logging.getLogger(__name__)


class WebExplorationStrategy(ExplorationStrategy):
    """
    Exploration strategy for web content in Chrome browser

    Combines:
    - Smart element prioritization (visible, unvisited first)
    - Page state tracking
    - Scroll-based discovery
    """

    def __init__(self, device: Device, max_scrolls: int = 5):
        """
        Initialize web exploration strategy

        Args:
            device: Target device
            max_scrolls: Maximum scroll operations before giving up
        """
        super().__init__(device)
        self.device = device
        self.max_scrolls = max_scrolls
        self.cdp: Optional[ChromeDevToolsManager] = None
        self.parser: Optional[HTMLParser] = None
        self.visited_elements: set = set()
        self.page_hashes: list = []

    async def initialize(self) -> bool:
        """Initialize Chrome DevTools connection"""
        try:
            self.cdp = ChromeDevToolsManager()
            if not await self.cdp.connect():
                logger.error("Failed to connect to Chrome DevTools")
                return False

            self.parser = HTMLParser(self.cdp)
            logger.info("Web exploration strategy initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize web strategy: {e}")
            return False

    async def cleanup(self) -> None:
        """Clean up Chrome DevTools connection"""
        if self.cdp:
            await self.cdp.disconnect()

    async def get_next_action(
        self,
        elements: List,
        state_id: str
    ) -> Optional[tuple]:
        """
        Get next action for web exploration

        Strategy:
        1. Prioritize unvisited elements
        2. Prefer buttons, links, inputs
        3. Scroll if all visible elements visited
        4. Return element to interact with

        Returns:
            (action_type, element) or None
        """
        if not self.parser:
            return None

        try:
            # Get current clickable elements
            clickable = await self.parser.get_clickable_elements()

            if not clickable:
                logger.info("No clickable elements found")
                return None

            # Filter unvisited elements
            unvisited = [
                e for e in clickable
                if e.node_id not in self.visited_elements
            ]

            if unvisited:
                # Pick random unvisited element
                element = random.choice(unvisited)
                self.visited_elements.add(element.node_id)
                return ("click", element)

            # All visible elements visited - try scrolling
            scroll_attempts = len(self.page_hashes)
            if scroll_attempts < self.max_scrolls:
                logger.info(f"Scrolling (attempt {scroll_attempts + 1}/{self.max_scrolls})")

                # Get current page state
                page_hash = await self.parser.get_page_state_hash()
                if page_hash in self.page_hashes:
                    logger.info("Page not changing - stopping exploration")
                    return None

                self.page_hashes.append(page_hash)

                # Scroll down
                if await self.parser.perform_scroll(direction="down", amount=500):
                    await asyncio.sleep(1)  # Wait for content load
                    self.parser.clear_cache()  # Clear cached elements

                    # Try to get new elements
                    return await self.get_next_action(elements, state_id)

            logger.info("No more actions available")
            return None

        except Exception as e:
            logger.error(f"Failed to get next action: {e}")
            return None


class GoogleSearchStrategy(WebExplorationStrategy):
    """Strategy for testing Google Search (example)"""

    async def get_next_action(
        self,
        elements: List,
        state_id: str
    ) -> Optional[tuple]:
        """
        Custom strategy for Google Search

        Steps:
        1. Click on search box
        2. Type something
        3. Click search button
        4. Click on results
        """
        if not self.parser:
            return None

        # Implementation specific to Google
        # 1. Find search box
        search_box = await self.parser.get_element_by_selector("input[name='q']")
        if search_box and search_box.node_id not in self.visited_elements:
            self.visited_elements.add(search_box.node_id)
            return ("click", search_box)

        # 2. Find and click links
        links = await self.parser.get_elements_by_selector("a[href*='http']")
        for link in links:
            if link.node_id not in self.visited_elements:
                self.visited_elements.add(link.node_id)
                return ("click", link)

        return None
```

## Step 3: Extend Exploration Engine

Modify the exploration engine to support both native and web:

**File:** `/Users/devload/smartMonkey/smartmonkey/exploration/exploration_engine.py` (extend)

```python
# Add to imports
from typing import Union, List
from .html_parser import HTMLParser, DOMNode
from .element import UIElement

# Add to ExplorationEngine class

async def discover_interactive_elements(
    self,
    include_chrome: bool = True
) -> List[Union[UIElement, DOMNode]]:
    """
    Discover interactive elements from both native UI and Chrome DOM

    Args:
        include_chrome: Whether to include Chrome DOM elements

    Returns:
        Combined list of interactive elements
    """
    elements = []

    # 1. Get native UI elements
    try:
        logger.info("Extracting native UI elements...")
        native_elements = self.parser.get_clickable_elements(
            self.parser.dump_hierarchy()
        )
        logger.info(f"Found {len(native_elements)} native elements")
        elements.extend(native_elements)
    except Exception as e:
        logger.warning(f"Failed to get native elements: {e}")

    # 2. Get Chrome DOM elements (if enabled and Chrome is active)
    if include_chrome and self.device.is_chrome_active():
        try:
            logger.info("Extracting Chrome DOM elements...")
            chrome_elements = await self.device.get_chrome_elements()
            logger.info(f"Found {len(chrome_elements)} Chrome elements")
            elements.extend(chrome_elements)
        except Exception as e:
            logger.warning(f"Failed to get Chrome elements: {e}")

    logger.info(f"Total interactive elements: {len(elements)}")
    return elements

async def run_with_chrome_support(
    self,
    steps: int = 10,
    strategy: str = "random"
) -> dict:
    """
    Run exploration with Chrome support

    Args:
        steps: Number of exploration steps
        strategy: Exploration strategy ("random", "weighted", "web")

    Returns:
        Exploration results
    """
    from .strategies.web_strategy import WebExplorationStrategy

    # Use web strategy for Chrome, weighted for native
    if self.device.is_chrome_active() and strategy == "web":
        logger.info("Using web exploration strategy")
        exp_strategy = WebExplorationStrategy(self.device)

        if not await exp_strategy.initialize():
            logger.error("Failed to initialize web strategy")
            return {"error": "Chrome connection failed"}

        try:
            return await self._run_exploration(steps, exp_strategy)
        finally:
            await exp_strategy.cleanup()
    else:
        # Use default strategy
        return await self.run(steps=steps, strategy=strategy)

async def _run_exploration(
    self,
    steps: int,
    strategy
) -> dict:
    """Helper to run exploration with given strategy"""
    # Implementation of exploration loop using strategy
    pass
```

## Step 4: Update CLI

Add web-specific commands to the CLI:

**File:** `/Users/devload/smartMonkey/smartmonkey/cli/main.py` (extend)

```python
# Add to imports
import asyncio

# Add web exploration command

@cli.command()
@click.option("--package", "-p", default="com.android.chrome",
              help="Package to test (default: Chrome)")
@click.option("--url", "-u", required=True, help="URL to navigate to")
@click.option("--steps", "-s", type=int, default=20, help="Number of steps")
@click.option("--output", "-o", type=click.Path(), default="./reports/web_test",
              help="Output directory for reports")
def run_web(package, url, steps, output):
    """
    Run web exploration on a URL in Chrome

    Example:
        smartmonkey run-web --url "https://www.google.com" --steps 20
    """
    from smartmonkey.device.device import Device
    from smartmonkey.exploration.exploration_engine import ExplorationEngine

    try:
        # Connect to device
        device = Device("emulator-5556")
        if not device.connect():
            click.echo("ERROR: Could not connect to device")
            return

        # Launch Chrome and navigate to URL
        click.echo(f"Launching Chrome and navigating to {url}...")
        device.adb.shell(f"am start -n com.android.chrome/com.google.android.apps.chrome.Main")
        device.adb.shell(f"am start -a android.intent.action.VIEW -d {url}")

        # Wait for page load
        import time
        time.sleep(3)

        # Run exploration
        click.echo(f"Starting web exploration for {steps} steps...")
        engine = ExplorationEngine(device)

        async def run_async():
            return await engine.run_with_chrome_support(
                steps=steps,
                strategy="web"
            )

        results = asyncio.run(run_async())

        # Generate report
        click.echo(f"Exploration complete! Results saved to {output}")

    except Exception as e:
        click.echo(f"ERROR: {e}")


@cli.command()
@click.option("--package", "-p", default="com.android.chrome",
              help="Package to inspect")
def inspect_chrome(package):
    """
    Inspect Chrome DOM elements interactively

    Example:
        smartmonkey inspect-chrome
    """
    from smartmonkey.device.device import Device
    from smartmonkey.exploration.html_parser import HTMLParserSync
    from smartmonkey.device.chrome_manager import ChromeDevToolsManager

    try:
        # Connect Chrome
        cdp = ChromeDevToolsManager()

        async def inspect():
            if not await cdp.connect():
                click.echo("ERROR: Could not connect to Chrome DevTools")
                return

            try:
                parser = HTMLParserSync(cdp)

                while True:
                    click.echo("\nInspect Chrome DOM:")
                    click.echo("  1. List clickable elements")
                    click.echo("  2. Query by selector")
                    click.echo("  3. Get element coordinates")
                    click.echo("  4. Navigate to URL")
                    click.echo("  0. Exit")

                    choice = click.prompt("Select option", type=int)

                    if choice == 1:
                        elements = parser.get_clickable_elements()
                        click.echo(f"\nFound {len(elements)} clickable elements:")
                        for i, elem in enumerate(elements[:10], 1):
                            click.echo(f"  {i}. <{elem.tag_name}> {elem.text_content[:50]}")

                    elif choice == 2:
                        selector = click.prompt("CSS Selector")
                        elements = parser.get_elements_by_selector(selector)
                        click.echo(f"Found {len(elements)} elements:")
                        for elem in elements:
                            click.echo(f"  {elem}")

                    elif choice == 3:
                        elements = parser.get_clickable_elements()
                        if elements:
                            elem = elements[0]
                            click.echo(f"Coordinates: {elem.coordinates}")

                    elif choice == 4:
                        url = click.prompt("URL")
                        if await cdp.navigate_to(url):
                            click.echo("Navigation successful!")

                    elif choice == 0:
                        break

            finally:
                await cdp.disconnect()

        import asyncio
        asyncio.run(inspect())

    except Exception as e:
        click.echo(f"ERROR: {e}")
```

## Step 5: Update Requirements

Add WebSocket library to dependencies:

**File:** `/Users/devload/smartMonkey/pyproject.toml` (update)

```toml
dependencies = [
    # ...existing dependencies...
    "websockets>=11.0.0",  # Chrome DevTools Protocol
]
```

Or just install:

```bash
pip install websockets>=11.0.0
```

## Step 6: Create Integration Tests

**File:** `/Users/devload/smartMonkey/tests/integration/test_chrome_integration.py`

```python
"""Integration tests for Chrome DOM extraction"""

import pytest
import asyncio
from smartmonkey.device.device import Device
from smartmonkey.device.chrome_manager import ChromeDevToolsManager
from smartmonkey.exploration.html_parser import HTMLParser


@pytest.mark.asyncio
async def test_chrome_discovery_flow():
    """Test complete Chrome DOM discovery flow"""

    # Navigate to test page
    device = Device("emulator-5556")
    assert device.connect()

    # Check Chrome is active
    assert device.is_chrome_active()

    # Get Chrome elements
    elements = await device.get_chrome_elements()
    assert len(elements) > 0

    # Check element structure
    elem = elements[0]
    assert hasattr(elem, 'node_id')
    assert hasattr(elem, 'tag_name')
    assert hasattr(elem, 'coordinates')


@pytest.mark.asyncio
async def test_web_exploration_strategy():
    """Test web exploration strategy"""
    from smartmonkey.exploration.strategies.web_strategy import WebExplorationStrategy

    device = Device("emulator-5556")
    assert device.connect()

    strategy = WebExplorationStrategy(device)
    assert await strategy.initialize()

    # Get action
    action = await strategy.get_next_action([], "state_1")
    assert action is not None
    assert action[0] == "click"

    await strategy.cleanup()


@pytest.mark.asyncio
async def test_hybrid_element_discovery():
    """Test discovering both native and web elements"""
    from smartmonkey.exploration.exploration_engine import ExplorationEngine

    device = Device("emulator-5556")
    assert device.connect()

    engine = ExplorationEngine(device)
    elements = await engine.discover_interactive_elements(
        include_chrome=True
    )

    # Should have both native and web elements
    assert len(elements) > 0
```

## Usage Examples

### Example 1: Basic Web Testing

```python
from smartmonkey.device.device import Device
from smartmonkey.exploration.exploration_engine import ExplorationEngine
import asyncio

async def test_web_app():
    device = Device("emulator-5556")
    device.connect()

    # Launch Chrome with URL
    device.adb.shell(
        "am start -a android.intent.action.VIEW "
        "-d https://www.google.com"
    )

    # Run exploration
    engine = ExplorationEngine(device)
    results = await engine.run_with_chrome_support(
        steps=50,
        strategy="web"
    )

    print(f"Explored {len(results['states'])} states")
    print(f"Found {len(results['elements'])} unique elements")

asyncio.run(test_web_app())
```

### Example 2: Hybrid Testing (Native + Web)

```python
from smartmonkey.device.device import Device
import asyncio

async def test_hybrid_app():
    device = Device("emulator-5556")
    device.connect()

    # Start app
    device.adb.shell("am start -n com.myapp/MainActivity")

    # Discover all interactive elements
    from smartmonkey.exploration.exploration_engine import ExplorationEngine
    engine = ExplorationEngine(device)

    # Get both native UI and Chrome elements
    all_elements = await engine.discover_interactive_elements(
        include_chrome=True
    )

    print(f"Total interactive elements: {len(all_elements)}")

    for elem in all_elements[:10]:
        print(f"- {elem.tag_name if hasattr(elem, 'tag_name') else elem.class_name}")

asyncio.run(test_hybrid_app())
```

### Example 3: CLI Usage

```bash
# Run web exploration
smartmonkey run-web \
  --url "https://github.com" \
  --steps 30 \
  --output ./reports/github_test

# Inspect Chrome DOM interactively
smartmonkey inspect-chrome

# List devices
smartmonkey list-devices
```

## Migration Checklist

- [ ] Install `websockets` library
- [ ] Add `chrome_manager.py` to device package
- [ ] Add `html_parser.py` to exploration package
- [ ] Extend `device.py` with Chrome methods
- [ ] Create `web_strategy.py` strategy
- [ ] Extend `exploration_engine.py`
- [ ] Add web commands to CLI
- [ ] Update `pyproject.toml`
- [ ] Create integration tests
- [ ] Test with example pages
- [ ] Update documentation
- [ ] Update CLAUDE.md with new capabilities

## Testing Checklist

```bash
# Test imports
python3 -c "from smartmonkey.device.chrome_manager import ChromeDevToolsManager"
python3 -c "from smartmonkey.exploration.html_parser import HTMLParser"

# Test connection
python3 examples/chrome_dom_extraction_example.py

# Run integration tests
pytest tests/integration/test_chrome_integration.py -v

# Test CLI
smartmonkey run-web --url "https://www.google.com" --steps 5
```

## Troubleshooting Integration

**Issue: ModuleNotFoundError: websockets**
```bash
pip install websockets>=11.0.0
```

**Issue: Cannot import chrome_manager**
```bash
# Ensure files are in correct location
ls -la smartmonkey/device/chrome_manager.py
ls -la smartmonkey/exploration/html_parser.py
```

**Issue: Chrome connection refused**
```bash
# Check port forwarding
adb -s emulator-5556 forward tcp:9222 localabstract:chrome_devtools_remote

# Verify connection
curl http://localhost:9222/json/version
```

**Issue: Async/await errors**
```python
# Make sure to use asyncio.run() for async functions
import asyncio
asyncio.run(async_function())
```

## Summary

This integration adds:

1. **Chrome DOM extraction** - Full HTML parsing via CDP
2. **Web exploration strategy** - Specialized algorithm for web content
3. **Hybrid discovery** - Both native and web elements
4. **CLI enhancements** - Web-specific commands
5. **Backward compatibility** - Existing code unchanged

The integration is modular and can be enabled/disabled without affecting native testing capabilities.

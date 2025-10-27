# Chrome DOM Extraction - Quick Setup Guide

## Prerequisites

### 1. Device Setup

Ensure you have:
- Android emulator running (emulator-5556)
- Chrome browser installed on device
- ADB installed on host machine

```bash
# Verify device connection
adb -s emulator-5556 devices
# Expected output:
# emulator-5556          device
```

### 2. Enable Chrome Debugging

```bash
# Start Chrome with debugging enabled (usually already enabled)
adb -s emulator-5556 shell am start -n com.android.chrome/com.google.android.apps.chrome.Main

# Navigate to a website in Chrome
# (or let it load the default page)
```

### 3. Set Up Port Forwarding

```bash
# Forward Chrome DevTools port
adb -s emulator-5556 forward tcp:9222 localabstract:chrome_devtools_remote

# Verify connection
curl http://localhost:9222/json/version

# Expected output (JSON with Chrome version info)
```

## Python Setup

### 1. Install Dependencies

```bash
cd /Users/devload/smartMonkey

# Install websockets library (required for CDP communication)
pip install websockets>=11.0.0

# Or update pyproject.toml and install:
pip install -e .
```

### 2. Verify Installation

```bash
python3 -c "import websockets; print('websockets OK')"
python3 -c "from smartmonkey.device.chrome_manager import ChromeDevToolsManager; print('chrome_manager OK')"
python3 -c "from smartmonkey.exploration.html_parser import HTMLParser; print('html_parser OK')"
```

## Quick Start

### Method 1: Run Example Script (Recommended)

```bash
cd /Users/devload/smartMonkey

# Make script executable
chmod +x examples/chrome_dom_extraction_example.py

# Run with interactive menu
python3 examples/chrome_dom_extraction_example.py
```

### Method 2: Python REPL

```bash
cd /Users/devload/smartMonkey
export PYTHONPATH=/Users/devload/smartMonkey:$PYTHONPATH
python3

# In Python:
>>> import asyncio
>>> from smartmonkey.device.chrome_manager import ChromeDevToolsManager
>>> from smartmonkey.exploration.html_parser import HTMLParser
>>>
>>> async def test():
...     cdp = ChromeDevToolsManager()
...     if await cdp.connect():
...         parser = HTMLParser(cdp)
...         elements = await parser.get_clickable_elements()
...         print(f"Found {len(elements)} elements")
...         await cdp.disconnect()
...
>>> asyncio.run(test())
```

### Method 3: Direct Usage in Your Code

```python
import asyncio
from smartmonkey.device.chrome_manager import ChromeDevToolsManager
from smartmonkey.exploration.html_parser import HTMLParser

async def extract_html_elements():
    # Connect to Chrome DevTools
    cdp = ChromeDevToolsManager(ws_url="ws://localhost:9222/devtools/page/1")

    if not await cdp.connect():
        print("Failed to connect to Chrome")
        return

    try:
        # Create parser
        parser = HTMLParser(cdp)

        # Get all clickable elements
        elements = await parser.get_clickable_elements()

        # Process elements
        for elem in elements:
            print(f"Tag: {elem.tag_name}")
            print(f"Text: {elem.text_content}")
            print(f"Coordinates: {elem.coordinates}")
            print(f"Clickable: {elem.is_clickable}")
            print("---")

    finally:
        await cdp.disconnect()

# Run it
asyncio.run(extract_html_elements())
```

## Troubleshooting

### Connection Issues

**Problem:** `Cannot connect to ws://localhost:9222`

**Solutions:**
1. Check port forwarding is active:
   ```bash
   adb -s emulator-5556 forward tcp:9222 localabstract:chrome_devtools_remote
   ```

2. Check Chrome is running:
   ```bash
   adb -s emulator-5556 shell am start -n com.android.chrome/com.google.android.apps.chrome.Main
   ```

3. Verify connection:
   ```bash
   curl http://localhost:9222/json/version
   # Should return JSON (not connection refused)
   ```

### No Elements Found

**Problem:** `Found 0 clickable elements`

**Causes:**
- Page is still loading (wait a moment)
- Page has no interactive elements
- Elements are in iframes (not yet supported)

**Solutions:**
1. Navigate to a page with interactive content:
   ```python
   await cdp.navigate_to("https://www.google.com")
   await asyncio.sleep(2)  # Wait for page load
   parser.clear_cache()
   elements = await parser.get_clickable_elements()
   ```

2. Check page loaded:
   ```python
   title = await cdp.evaluate_js("document.title")
   print(f"Page title: {title}")
   ```

### Slow Element Extraction

**Problem:** Takes >5 seconds to get elements

**Optimizations:**
1. Increase timeout:
   ```python
   cdp = ChromeDevToolsManager(timeout=10.0)
   ```

2. Query specific selectors instead of all:
   ```python
   buttons = await parser.get_elements_by_selector("button")
   # instead of:
   all_elements = await parser.get_clickable_elements()
   ```

3. Reduce page complexity (remove scripts):
   ```python
   await cdp.evaluate_js("document.querySelectorAll('script').forEach(s => s.remove())")
   ```

### Coordinates Are 0,0

**Problem:** All elements have coordinates at origin

**Solution:** This is usually correct. Verify with:
```python
elem = elements[0]
print(f"Width: {elem.coordinates['width']}")
print(f"Height: {elem.coordinates['height']}")

if elem.coordinates['width'] == 0:
    # Element might be hidden
    print("Element has zero width - probably hidden")
```

## Common Tasks

### Extract All Buttons

```python
buttons = await parser.get_elements_by_selector("button")
for btn in buttons:
    print(f"Button: {btn.text_content}")
    print(f"  Coordinates: ({btn.center_x}, {btn.center_y})")
```

### Find Element by Text

```python
# Query elements and filter by text
elements = await parser.get_clickable_elements()
search_btn = next((e for e in elements if "Search" in e.text_content), None)

if search_btn:
    await parser.click_element(search_btn.node_id)
```

### Scroll and Extract

```python
# Scroll down
await parser.perform_scroll(direction="down", amount=500)

# Extract visible elements
elements = await parser.get_clickable_elements()
```

### Take Screenshot

```python
# Take screenshot of current page
screenshot_data = await cdp.take_screenshot()

if screenshot_data:
    with open("screenshot.png", "wb") as f:
        f.write(screenshot_data)
    print("Screenshot saved!")
```

### Get Page Dimensions

```python
dimensions = await cdp.get_page_dimensions()
print(f"Viewport: {dimensions['width']}x{dimensions['height']}")
print(f"Scroll position: ({dimensions['scrollX']}, {dimensions['scrollY']})")
```

## Performance Tips

1. **Reuse Connection:**
   ```python
   cdp = ChromeDevToolsManager()
   await cdp.connect()

   # Do multiple operations
   elements1 = await parser.get_clickable_elements()
   # ... click something ...
   elements2 = await parser.get_clickable_elements()

   await cdp.disconnect()
   ```

2. **Cache Elements:**
   ```python
   # Don't re-extract if nothing changed
   hash1 = await parser.get_page_state_hash()
   # ... perform action ...
   hash2 = await parser.get_page_state_hash()

   if hash1 == hash2:
       # Use cached elements
       elements = cached_elements
   else:
       # Re-extract
       elements = await parser.get_clickable_elements()
   ```

3. **Batch Operations:**
   ```python
   # Query multiple selectors in parallel
   tasks = [
       parser.get_elements_by_selector("button"),
       parser.get_elements_by_selector("a"),
       parser.get_elements_by_selector("input"),
   ]
   buttons, links, inputs = await asyncio.gather(*tasks)
   ```

## Integration with SmartMonkey

Add Chrome DOM extraction to exploration engine:

```python
# In smartmonkey/exploration/exploration_engine.py

from smartmonkey.device.chrome_manager import ChromeDevToolsManager
from smartmonkey.exploration.html_parser import HTMLParser

class ExplorationEngine:
    async def get_available_actions(self, device):
        """Get both native UI and HTML elements"""

        # Get native UI elements (existing)
        native_elements = device.get_ui_elements()

        # Get HTML elements from Chrome (new)
        html_elements = []
        try:
            cdp = ChromeDevToolsManager()
            if await cdp.connect():
                parser = HTMLParser(cdp)
                html_elements = await parser.get_clickable_elements()
                await cdp.disconnect()
        except Exception as e:
            logger.warning(f"Failed to get HTML elements: {e}")

        # Combine and return
        return native_elements + html_elements
```

## Next Steps

1. **Test with Example Script:**
   ```bash
   python3 examples/chrome_dom_extraction_example.py
   ```

2. **Try Different Pages:**
   - Google: `https://www.google.com`
   - GitHub: `https://github.com`
   - Wikipedia: `https://wikipedia.org`

3. **Integrate with SmartMonkey:**
   - Add Chrome DOM extraction to exploration strategies
   - Test web app automation

4. **Advanced Features:**
   - Add form filling automation
   - Implement DFS/BFS for web navigation
   - Add performance monitoring

## Reference

- Chrome DevTools Protocol: https://chromedevtools.github.io/devtools-protocol/
- WebSocket Protocol: https://datatracker.ietf.org/doc/html/rfc6455
- SmartMonkey Documentation: `/Users/devload/smartMonkey/docs/`

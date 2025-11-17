# Chrome DOM Extraction - Quick Reference Card

## One-Page Cheat Sheet

### Setup (5 minutes)

```bash
# 1. Install library
pip install websockets>=11.0.0

# 2. Enable port forwarding
adb -s emulator-5556 forward tcp:9222 localabstract:chrome_devtools_remote

# 3. Verify
curl http://localhost:9222/json/version
```

### Basic Usage

#### Async (Recommended)
```python
import asyncio
from smartmonkey.device.chrome_manager import ChromeDevToolsManager
from smartmonkey.exploration.html_parser import HTMLParser

async def main():
    cdp = ChromeDevToolsManager()
    if await cdp.connect():
        parser = HTMLParser(cdp)
        elements = await parser.get_clickable_elements()
        print(f"Found {len(elements)} elements")
        await cdp.disconnect()

asyncio.run(main())
```

#### Sync (Simpler)
```python
from smartmonkey.exploration.html_parser import HTMLParserSync
from smartmonkey.device.chrome_manager import ChromeDevToolsManager
import asyncio

cdp = ChromeDevToolsManager()
asyncio.run(cdp.connect())
parser = HTMLParserSync(cdp)
elements = parser.get_clickable_elements()
asyncio.run(cdp.disconnect())
```

### Common Operations

#### Get All Clickable Elements
```python
elements = await parser.get_clickable_elements()
for elem in elements:
    print(f"{elem.tag_name}: {elem.text_content}")
    print(f"  Position: ({elem.center_x}, {elem.center_y})")
```

#### Find by Selector
```python
# Single element
button = await parser.get_element_by_selector("button.primary")

# Multiple elements
buttons = await parser.get_elements_by_selector("button")
```

#### Click Element
```python
elem = elements[0]
success = await parser.click_element(elem.node_id)
```

#### Get Page Info
```python
dimensions = await cdp.get_page_dimensions()
print(f"Viewport: {dimensions['width']}x{dimensions['height']}")

title = await cdp.evaluate_js("document.title")
```

#### Scroll Page
```python
# Scroll down 500px
await parser.perform_scroll(direction="down", amount=500)

# Scroll up
await parser.perform_scroll(direction="up", amount=300)
```

#### Navigate to URL
```python
await cdp.navigate_to("https://www.google.com")
```

### DOMNode Properties

```python
elem = elements[0]

# Basic properties
elem.node_id          # CDP node ID
elem.tag_name         # HTML tag (button, a, input, etc.)
elem.text_content     # Element text (max 200 chars)
elem.attributes       # Dict of all attributes

# Coordinates
elem.coordinates      # {'x': 100, 'y': 200, 'width': 50, 'height': 30}
elem.center_x         # Center X coordinate
elem.center_y         # Center Y coordinate

# Status
elem.is_visible       # Is element visible to user
elem.is_clickable     # Can element be clicked
elem.is_input         # Is element an input field

# Selector
elem.css_selector     # Generated CSS selector
```

### Selectors

```python
# Pre-defined selector sets
parser.CLICKABLE_SELECTORS  # Buttons, links, inputs
parser.INPUT_SELECTORS      # Text inputs, textareas, etc.

# Custom selectors
buttons = await parser.get_elements_by_selector("button")
links = await parser.get_elements_by_selector("a[href]")
inputs = await parser.get_elements_by_selector("input[type='text']")

# Complex CSS
search_box = await parser.get_element_by_selector(
    "div.search input[name='q']"
)
```

### Error Handling

```python
try:
    elements = await parser.get_clickable_elements()
except RuntimeError as e:
    print(f"CDP Error: {e}")
except asyncio.TimeoutError:
    print("Timeout waiting for response")
```

### Retry Pattern

```python
async def get_elements_safe(parser, retries=3):
    for attempt in range(retries):
        try:
            return await parser.get_clickable_elements()
        except Exception as e:
            if attempt < retries - 1:
                await asyncio.sleep(1)
            else:
                raise
```

### Caching

```python
# Get hash of current page state
hash1 = await parser.get_page_state_hash()

# ... do something ...

# Check if page changed
hash2 = await parser.get_page_state_hash()

if hash1 == hash2:
    # Page unchanged, use cached elements
    pass
else:
    # Re-extract elements
    parser.clear_cache()
    elements = await parser.get_clickable_elements()
```

### Performance Tips

| Operation | Time |
|-----------|------|
| Connect | 200-500ms |
| Get all clickable | 250-350ms |
| Get elements (cached) | 50-100ms |
| Click element | 100-200ms |
| Scroll | 200-500ms |

**Optimization:**
1. Reuse connection (don't reconnect every time)
2. Cache elements between actions
3. Use selector queries for specific types
4. Filter results after extraction

### Debugging

```python
# Enable logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check if connected
connected = await cdp.is_connected()

# Inspect element details
elem = elements[0]
print(f"ID: {elem.node_id}")
print(f"Tag: {elem.tag_name}")
print(f"Attrs: {elem.attributes}")
print(f"Coords: {elem.coordinates}")
print(f"Visible: {elem.is_visible}")

# Take screenshot
screenshot = await cdp.take_screenshot()
if screenshot:
    with open("page.png", "wb") as f:
        f.write(screenshot)
```

### CLI Commands

```bash
# List devices
smartmonkey list-devices

# Run web exploration
smartmonkey run-web \
  --url "https://www.google.com" \
  --steps 20

# Inspect Chrome interactively
smartmonkey inspect-chrome
```

### Comparison: Native vs Chrome DOM

| Need | Solution | Command |
|------|----------|---------|
| Test native UI | UIAutomator | `device.get_ui_elements()` |
| Test web | Chrome DOM | `await parser.get_clickable_elements()` |
| Both | Hybrid | `await engine.discover_interactive_elements()` |

### Troubleshooting Cheat Sheet

| Problem | Solution |
|---------|----------|
| "Cannot connect" | `adb forward tcp:9222 localabstract:chrome_devtools_remote` |
| "No elements found" | Wait for page load, check Chrome is running |
| "Timeout" | Increase `timeout` parameter, reduce selectors |
| "Coordinates are 0,0" | Element may be hidden, check width/height |
| "Module not found" | `pip install websockets>=11.0.0` |
| "No Chrome running" | `adb shell am start -n com.android.chrome/...` |

### One-Liner Examples

```python
# Extract first 5 buttons
buttons = (await parser.get_elements_by_selector("button"))[:5]

# Find searchable text
search = [e for e in elements if "search" in e.text_content.lower()]

# Get all links
links = await parser.get_elements_by_selector("a[href]")

# Click first button
await parser.click_element(elements[0].node_id)

# Navigate and extract
await cdp.navigate_to("https://example.com")
await asyncio.sleep(2)
parser.clear_cache()
elements = await parser.get_clickable_elements()
```

### Resource Links

| Resource | URL |
|----------|-----|
| CDP Docs | chromedevtools.github.io/devtools-protocol |
| Setup Guide | `/docs/CHROME_DOM_SETUP.md` |
| Full Docs | `/docs/CHROME_DOM_EXTRACTION.md` |
| Integration | `/docs/CHROME_INTEGRATION_GUIDE.md` |
| Examples | `/examples/chrome_dom_extraction_example.py` |

### Version Info

```python
# Check Chrome version via CDP
version = await cdp.evaluate_js("navigator.userAgent")
print(version)

# Get CDP protocol version
version_info = await cdp.send_command("Browser.getVersion")
```

### Full Workflow Example

```python
import asyncio
from smartmonkey.device.chrome_manager import ChromeDevToolsManager
from smartmonkey.exploration.html_parser import HTMLParser

async def full_workflow():
    # Connect
    cdp = ChromeDevToolsManager()
    assert await cdp.connect(), "Connection failed"

    try:
        # Navigate
        await cdp.navigate_to("https://www.google.com")
        await asyncio.sleep(2)

        # Parse
        parser = HTMLParser(cdp)
        elements = await parser.get_clickable_elements()

        # Filter
        buttons = [e for e in elements if e.tag_name == "button"]

        # Action
        if buttons:
            await parser.click_element(buttons[0].node_id)
            await asyncio.sleep(1)

            # Re-extract after action
            parser.clear_cache()
            new_elements = await parser.get_clickable_elements()
            print(f"After click: {len(new_elements)} elements")

        return new_elements

    finally:
        # Cleanup
        await cdp.disconnect()

# Run it
results = asyncio.run(full_workflow())
print(f"Total elements: {len(results)}")
```

---

**For detailed info, see full documentation:**
- Setup: `/docs/CHROME_DOM_SETUP.md`
- Reference: `/docs/CHROME_DOM_EXTRACTION.md`
- Comparison: `/docs/CHROME_VS_NATIVE_COMPARISON.md`
- Integration: `/docs/CHROME_INTEGRATION_GUIDE.md`

#!/usr/bin/env python3
"""
Example: Extract HTML DOM elements from Chrome on Android

This example demonstrates how to:
1. Connect to Chrome DevTools Protocol on Android device
2. Extract clickable HTML elements
3. Get element coordinates for automated clicking
4. Perform actions (click, scroll, etc.)

Setup:
    adb -s emulator-5556 forward tcp:9222 localabstract:chrome_devtools_remote
    python3 examples/chrome_dom_extraction_example.py
"""

import asyncio
import sys
from pathlib import Path

# Add smartmonkey to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from smartmonkey.device.chrome_manager import ChromeDevToolsManager
from smartmonkey.exploration.html_parser import HTMLParser, HTMLParserSync
from smartmonkey.utils.logger import get_logger

logger = get_logger(__name__)


async def example_async():
    """Async example of Chrome DOM extraction"""
    print("\n" + "="*70)
    print("ASYNC Chrome DOM Extraction Example")
    print("="*70)

    # Connect to Chrome DevTools
    cdp = ChromeDevToolsManager(
        ws_url="ws://localhost:9222/devtools/page/1",
        timeout=5.0
    )

    if not await cdp.connect():
        print("ERROR: Failed to connect to Chrome DevTools")
        print("\nSetup required:")
        print("  adb -s emulator-5556 forward tcp:9222 localabstract:chrome_devtools_remote")
        return

    try:
        # Initialize parser
        parser = HTMLParser(cdp)

        print("\n[1] Getting page dimensions...")
        dimensions = await cdp.get_page_dimensions()
        print(f"    Viewport: {dimensions['width']}x{dimensions['height']}")
        print(f"    Scroll: ({dimensions['scrollX']}, {dimensions['scrollY']})")

        print("\n[2] Extracting clickable elements...")
        elements = await parser.get_clickable_elements()

        if not elements:
            print("    No clickable elements found")
        else:
            print(f"    Found {len(elements)} interactive elements:")
            print(f"\n    {'Tag':<10} {'Text':<30} {'Coords':<25} {'Type':<10}")
            print(f"    {'-'*10} {'-'*30} {'-'*25} {'-'*10}")

            for i, elem in enumerate(elements[:10], 1):  # Show first 10
                text = elem.text_content[:25].replace("\n", " ").strip()
                if elem.coordinates:
                    coords = f"({elem.coordinates['x']}, {elem.coordinates['y']})"
                else:
                    coords = "N/A"

                elem_type = "input" if elem.is_input else "button"
                print(f"    {elem.tag_name:<10} {text:<30} {coords:<25} {elem_type:<10}")

                # Print details for first element
                if i == 1:
                    print(f"\n    Details of first element:")
                    print(f"      Tag: {elem.tag_name}")
                    print(f"      Text: {elem.text_content[:100]}")
                    print(f"      Attributes: {elem.attributes}")
                    print(f"      Visible: {elem.is_visible}")
                    print(f"      Coordinates: {elem.coordinates}")
                    print(f"      CSS Selector: {elem.css_selector}")

            if len(elements) > 10:
                print(f"    ... and {len(elements) - 10} more elements")

        print("\n[3] Testing specific queries...")

        # Query for buttons
        buttons = await parser.get_elements_by_selector("button")
        print(f"    Found {len(buttons)} button elements")

        # Query for links
        links = await parser.get_elements_by_selector("a")
        print(f"    Found {len(links)} link elements")

        # Query for input fields
        inputs = await parser.get_elements_by_selector("input")
        print(f"    Found {len(inputs)} input elements")

        print("\n[4] Getting element at specific point (0, 0)...")
        elem = await parser.get_element_at_point(0, 0)
        if elem:
            print(f"    Found: <{elem.tag_name}> {elem.text_content[:50]}")
        else:
            print("    No element at that point")

        print("\n[5] Testing page navigation...")
        print("    Navigating to google.com...")
        if await cdp.navigate_to("https://www.google.com"):
            print("    Navigation successful!")
            await asyncio.sleep(2)  # Wait for page load

            # Clear cache and reparse
            parser.clear_cache()
            google_elements = await parser.get_clickable_elements()
            print(f"    Found {len(google_elements)} elements on google.com")
        else:
            print("    Navigation failed")

    finally:
        await cdp.disconnect()

    print("\n" + "="*70)
    print("Async example completed!")
    print("="*70 + "\n")


def example_sync():
    """Sync example using wrapper"""
    print("\n" + "="*70)
    print("SYNC Chrome DOM Extraction Example (using wrapper)")
    print("="*70)

    # Connect to Chrome DevTools
    cdp = ChromeDevToolsManager(
        ws_url="ws://localhost:9222/devtools/page/1",
        timeout=5.0
    )

    # Note: Connect still needs to be async
    connected = asyncio.run(cdp.connect())

    if not connected:
        print("ERROR: Failed to connect to Chrome DevTools")
        return

    try:
        # Initialize sync parser
        parser = HTMLParserSync(cdp)

        print("\n[1] Extracting clickable elements (sync)...")
        elements = parser.get_clickable_elements()

        if not elements:
            print("    No clickable elements found")
        else:
            print(f"    Found {len(elements)} interactive elements")
            for elem in elements[:5]:
                print(f"    - <{elem.tag_name}> {elem.text_content[:40]}")

        print("\n[2] Querying elements by selector (sync)...")
        buttons = parser.get_elements_by_selector("button")
        print(f"    Found {len(buttons)} buttons")

        print("\n[3] Clicking element (example)...")
        if buttons:
            success = parser.click_element(buttons[0].node_id)
            print(f"    Click result: {success}")

    finally:
        asyncio.run(cdp.disconnect())

    print("\n" + "="*70)
    print("Sync example completed!")
    print("="*70 + "\n")


def example_with_retry():
    """Example with retry logic"""
    print("\n" + "="*70)
    print("Chrome DOM Extraction with Retry Logic")
    print("="*70)

    async def get_elements_with_retry(max_retries: int = 3) -> list:
        """Get clickable elements with retry"""
        for attempt in range(1, max_retries + 1):
            try:
                cdp = ChromeDevToolsManager()
                if not await cdp.connect():
                    print(f"  Attempt {attempt}: Connection failed")
                    await asyncio.sleep(1)
                    continue

                try:
                    parser = HTMLParser(cdp)
                    elements = await parser.get_clickable_elements()
                    print(f"  Attempt {attempt}: Success! Found {len(elements)} elements")
                    return elements
                finally:
                    await cdp.disconnect()

            except Exception as e:
                print(f"  Attempt {attempt}: Error - {e}")
                if attempt < max_retries:
                    await asyncio.sleep(1)

        return []

    elements = asyncio.run(get_elements_with_retry(max_retries=3))
    print(f"\nFinal result: {len(elements)} elements")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    import subprocess

    print("\nSmartMonkey Chrome DOM Extraction Examples")
    print("=" * 70)
    print("\nBefore running examples, ensure port forwarding is set up:")
    print("  adb -s emulator-5556 forward tcp:9222 localabstract:chrome_devtools_remote")

    # Check if device is connected
    try:
        result = subprocess.run(
            ["adb", "devices"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if "emulator-5556" not in result.stdout:
            print("\nWARNING: emulator-5556 not found in connected devices")
            print("Available devices:")
            print(result.stdout)
    except Exception as e:
        print(f"WARNING: Could not check connected devices: {e}")

    print("\n" + "=" * 70)

    # Run examples
    choice = input("\nSelect example to run:\n"
                  "  1. Async example (recommended)\n"
                  "  2. Sync example\n"
                  "  3. Retry logic example\n"
                  "  4. Run all\n"
                  "\nChoice (1-4): ").strip()

    try:
        if choice == "1" or choice == "4":
            asyncio.run(example_async())

        if choice == "2" or choice == "4":
            example_sync()

        if choice == "3" or choice == "4":
            example_with_retry()

        if choice not in ["1", "2", "3", "4"]:
            print("Invalid choice")
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()

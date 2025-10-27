#!/usr/bin/env python3
"""Test screenshot timing to ensure post-navigation capture"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smartmonkey.device.chrome.chrome_device import ChromeDevice


async def main():
    print("=" * 70)
    print("🧪 Screenshot Timing Test")
    print("=" * 70)

    device = ChromeDevice(device_serial="emulator-5556", cdp_port=9222)

    if not await device.connect(initial_url="https://m.naver.com"):
        print("❌ Connection failed")
        return

    print("\n✅ Connected to m.naver.com")

    # Take screenshot of initial page
    print("\n📸 Step 1: Capture BEFORE navigation...")
    await device.capture_screenshot("/tmp/screenshot_before.png")
    print("   Saved: /tmp/screenshot_before.png")

    # Navigate to a different page using JavaScript
    print("\n🔗 Step 2: Navigate to NAVER TV...")
    await device.cdp.evaluate_js("window.location.href = 'https://tv.naver.com'")

    # Short wait
    print("   ⏳ Wait 1 second...")
    await asyncio.sleep(1.0)

    # Take screenshot immediately (might show old page)
    print("\n📸 Step 3: Capture 1 second after navigation...")
    await device.capture_screenshot("/tmp/screenshot_1sec.png")
    print("   Saved: /tmp/screenshot_1sec.png")

    # Longer wait
    print("   ⏳ Wait 2 more seconds...")
    await asyncio.sleep(2.0)

    # Take screenshot after longer wait
    print("\n📸 Step 4: Capture 3 seconds after navigation...")
    await device.capture_screenshot("/tmp/screenshot_3sec.png")
    print("   Saved: /tmp/screenshot_3sec.png")

    # Even longer wait
    print("   ⏳ Wait 2 more seconds...")
    await asyncio.sleep(2.0)

    # Take screenshot after even longer wait
    print("\n📸 Step 5: Capture 5 seconds after navigation...")
    await device.capture_screenshot("/tmp/screenshot_5sec.png")
    print("   Saved: /tmp/screenshot_5sec.png")

    # Check current URL
    current_url = await device.cdp.evaluate_js("document.URL")
    print(f"\n🌐 Current URL: {current_url}")

    await device.disconnect()

    print("\n" + "=" * 70)
    print("✅ Test Complete!")
    print("=" * 70)
    print("\n📋 Compare the screenshots:")
    print("   - screenshot_before.png  → Should show m.naver.com")
    print("   - screenshot_1sec.png    → Might still show m.naver.com (too fast)")
    print("   - screenshot_3sec.png    → Should show tv.naver.com")
    print("   - screenshot_5sec.png    → Should show tv.naver.com")


if __name__ == "__main__":
    asyncio.run(main())

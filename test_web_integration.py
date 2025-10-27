#!/usr/bin/env python3
"""
Chrome Web Testing Integration Test

이 스크립트는 SmartMonkey의 Chrome 웹 테스트 기능을 검증합니다.
"""

import asyncio
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smartmonkey.device.chrome.chrome_device import ChromeDevice
from smartmonkey.exploration.strategies.random_strategy import RandomStrategy
from smartmonkey.exploration.action import Action, ActionType


async def test_web_exploration():
    """Test web exploration with Chrome"""

    print("=" * 70)
    print("🌐 SmartMonkey Chrome Web Testing")
    print("=" * 70)

    # Step 1: Initialize ChromeDevice
    print("\n📱 Step 1: Initializing ChromeDevice...")
    device = ChromeDevice(device_serial="emulator-5556")

    # Step 2: Connect to Chrome and navigate
    print("\n🔌 Step 2: Connecting to Chrome...")
    if not await device.connect(initial_url="https://m.naver.com"):
        print("❌ Failed to connect to Chrome")
        return False

    print(f"✅ Connected to: {device.url}")

    # Step 3: Get initial state
    print("\n📄 Step 3: Extracting page state...")
    state = await device.get_current_state()
    print(f"✅ Page state extracted")
    print(f"   URL: {state.url}")
    print(f"   Elements: {len(state.elements)}")
    print(f"   State hash: {state.state_hash[:8]}")

    # Step 4: Initialize strategy
    print("\n🎲 Step 4: Initializing Random Strategy...")
    strategy = RandomStrategy()

    # Step 5: Run exploration (10 steps)
    print("\n🚀 Step 5: Running exploration (10 steps)...")
    print("-" * 70)

    max_steps = 10
    visited_states = set()

    for step in range(1, max_steps + 1):
        print(f"\n[Step {step}/{max_steps}]")

        # Get current state
        current_state = await device.get_current_state()
        state_hash = current_state.state_hash

        # Check if state is new
        if state_hash in visited_states:
            print(f"   State: {state_hash[:8]} (visited)")
        else:
            print(f"   State: {state_hash[:8]} (NEW)")
            visited_states.add(state_hash)

        print(f"   URL: {current_state.url}")
        print(f"   Elements: {len(current_state.elements)}")

        # Get clickable elements
        clickable = current_state.get_clickable_elements()
        if not clickable:
            print("   ⚠️  No clickable elements found")
            break

        print(f"   Clickable: {len(clickable)}")

        # Choose action using strategy
        action = strategy.next_action(current_state)

        if action.action_type == ActionType.TAP:
            if action.element:
                elem_text = action.element.text[:30] if action.element.text else "(no text)"
                print(f"   Action: TAP on '{elem_text}' at ({action.x}, {action.y})")
            else:
                print(f"   Action: TAP at ({action.x}, {action.y})")
        else:
            print(f"   Action: {action.action_type.value}")

        # Execute action
        await device.execute_action(action)

        # Wait a bit for page to load/transition
        await asyncio.sleep(1.0)

    # Step 6: Summary
    print("\n" + "=" * 70)
    print("📊 Exploration Summary")
    print("=" * 70)
    print(f"Total steps: {max_steps}")
    print(f"Unique states visited: {len(visited_states)}")
    print(f"Final URL: {device.url}")

    # Step 7: Disconnect
    print("\n🔌 Step 7: Disconnecting...")
    await device.disconnect()
    print("✅ Disconnected")

    print("\n" + "=" * 70)
    print("✅ Test completed successfully!")
    print("=" * 70)

    return True


async def main():
    """Main entry point"""
    try:
        success = await test_web_exploration()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Test interrupted by user")
        sys.exit(130)
    except Exception as e:
        print(f"\n\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    print("\n🧪 Starting Chrome Web Testing Integration Test\n")
    asyncio.run(main())

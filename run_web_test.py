#!/usr/bin/env python3
"""웹 테스트 실행 및 리포트 생성"""

import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smartmonkey.device.chrome.chrome_device import ChromeDevice
from smartmonkey.exploration.strategies.random_strategy import RandomStrategy
from smartmonkey.exploration.exploration_engine import ExplorationResult
from smartmonkey.exploration.state import AppState
from smartmonkey.exploration.action import Action
from smartmonkey.reporting.report_generator import ReportGenerator

async def main():
    print("=" * 70)
    print("🌐 SmartMonkey Web Test - Naver Mobile")
    print("=" * 70)

    # 1. ChromeDevice 초기화
    print("\n📱 Step 1: ChromeDevice 초기화...")
    device = ChromeDevice(device_serial="emulator-5556", cdp_port=9222)

    # 2. Chrome 연결
    print("\n🔌 Step 2: Chrome 연결...")
    if not await device.connect(initial_url="https://m.naver.com"):
        print("❌ Chrome 연결 실패!")
        return

    print(f"✅ 연결 성공: {device.url}")

    # 3. 탐색 실행 (5 steps만)
    print("\n🚀 Step 3: 웹 탐색 시작 (5 steps)...")
    strategy = RandomStrategy()

    # ExplorationResult 초기화 (인자 없이)
    result = ExplorationResult()

    try:
        visited_states = set()

        for step in range(5):
            print(f"\n[Step {step+1}/5]")

            # 현재 상태 가져오기
            state = await device.get_current_state()
            print(f"   State: {state.state_hash[:8]}")
            print(f"   URL: {state.url}")
            print(f"   Elements: {len(state.elements)}")

            # 상태 기록
            if state.state_hash not in visited_states:
                visited_states.add(state.state_hash)
                print(f"   → NEW state discovered")
            else:
                print(f"   → Visited state")

            # 스크린샷 캡처
            screenshot_dir = "./reports/web_naver_test/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = f"{screenshot_dir}/screenshot_{step:04d}.png"
            await device.capture_screenshot(screenshot_path)
            print(f"   📸 Screenshot: {screenshot_path}")

            # 상태를 result에 추가 (AppState로 변환)
            # AppState를 직접 추가할 수 없으므로, HTML state를 그대로 추가
            result.states.append(state)

            # 다음 액션 결정
            action = strategy.next_action(state)
            if action is None:
                print("   ⚠️  No more actions available")
                break

            print(f"   Action: {action}")

            # 액션 기록
            result.actions.append(action)

            # 액션 실행
            await device.execute_action(action)
            await asyncio.sleep(1.0)  # 페이지 로딩 대기

    finally:
        # 연결 종료
        await device.disconnect()

    # 탐색 종료
    result.finish()

    # 4. 리포트 생성
    print("\n📊 Step 4: 리포트 생성...")
    generator = ReportGenerator()

    # JSON 리포트 저장 (자동으로 index.json 업데이트됨!)
    json_path = "./reports/web_naver_test/report.json"
    generator.save_json_report(result, json_path)
    print(f"✅ JSON 리포트: {json_path}")

    # 텍스트 리포트 저장
    txt_path = "./reports/web_naver_test/report.txt"
    generator.save_text_report(result, txt_path)
    print(f"✅ 텍스트 리포트: {txt_path}")

    # 5. 결과 요약
    print("\n" + "=" * 70)
    print("✅ 웹 테스트 완료!")
    print("=" * 70)
    print(f"\n📈 결과:")
    print(f"   - 실행 시간: {result.duration:.1f}초")
    print(f"   - 총 이벤트: {result.total_events}개")
    print(f"   - 고유 상태: {result.unique_states}개")
    print(f"   - 총 상태: {len(result.states)}개")
    print(f"\n🎯 index.json이 자동으로 업데이트되었습니다!")
    print(f"   Grafana에서 확인하세요: http://localhost:3000")

if __name__ == "__main__":
    asyncio.run(main())

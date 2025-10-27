#!/usr/bin/env python3
"""웹 네비게이션 테스트 - 실제로 페이지 이동하는 테스트"""

import asyncio
import sys
import os
from datetime import datetime
import random

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smartmonkey.device.chrome.chrome_device import ChromeDevice
from smartmonkey.exploration.strategies.random_strategy import RandomStrategy
from smartmonkey.exploration.exploration_engine import ExplorationResult
from smartmonkey.exploration.action import TapAction, ActionType
from smartmonkey.reporting.report_generator import ReportGenerator

async def main():
    print("=" * 70)
    print("🌐 SmartMonkey 웹 네비게이션 테스트")
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

    # 3. 탐색 실행
    print("\n🚀 Step 3: 웹 네비게이션 시작 (10 steps)...")

    result = ExplorationResult()

    try:
        visited_urls = set()
        previous_url = None

        for step in range(10):
            print(f"\n[Step {step+1}/10]")

            # 현재 상태 가져오기
            state = await device.get_current_state()
            current_url = state.url

            print(f"   URL: {current_url}")
            print(f"   Elements: {len(state.elements)}개")

            # URL 변경 감지
            if previous_url and previous_url != current_url:
                print(f"   ✨ 새로운 페이지로 이동!")
                visited_urls.add(current_url)
            elif current_url not in visited_urls:
                print(f"   → 새로운 URL 발견")
                visited_urls.add(current_url)
            else:
                print(f"   → 같은 페이지 (URL 변경 없음)")

            # 스크린샷 캡처
            screenshot_dir = "./reports/web_navigation_test/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = f"{screenshot_dir}/screenshot_{step:04d}.png"
            await device.capture_screenshot(screenshot_path)
            print(f"   📸 Screenshot: {screenshot_path}")

            # 상태 기록
            result.states.append(state)

            # **개선된 액션 선택**: 네비게이션 링크 우선
            # 1. href가 있는 <a> 태그 중에서 외부 URL로 이동하는 것 선택
            navigation_links = []
            for elem in state.elements:
                # DOMNode는 attributes dict에서 href를 가져옴
                if elem.tag_name == 'a':
                    href = elem.attributes.get('href') if hasattr(elem, 'attributes') else None
                    if href:
                        # 절대 URL이거나 상대 URL인 경우
                        if href.startswith('http') or href.startswith('/'):
                            # 현재 URL과 다른 경로인지 확인
                            if href not in visited_urls and href != current_url:
                                navigation_links.append(elem)

            if navigation_links:
                print(f"   🔗 네비게이션 링크 {len(navigation_links)}개 발견")
                # 무작위로 하나 선택
                selected = random.choice(navigation_links)
                # Use coordinates directly, not element (DOMNode doesn't have center property)
                x = selected.center_x if hasattr(selected, 'center_x') else selected.coordinates['x'] + selected.coordinates['width'] // 2
                y = selected.center_y if hasattr(selected, 'center_y') else selected.coordinates['y'] + selected.coordinates['height'] // 2
                action = TapAction(x=x, y=y)
                link_text = selected.text_content.strip()[:40] if selected.text_content else "텍스트 없음"
                href = selected.attributes.get('href', '')
                print(f"   → 선택한 링크: {link_text}")
                print(f"   → 목적지: {href[:60]}")
            else:
                # 네비게이션 링크가 없으면 일반 요소 중에서 선택
                print(f"   ⚠️  네비게이션 링크 없음, 일반 요소 선택")
                if state.elements:
                    selected = random.choice(state.elements)
                    # Use coordinates directly, not element
                    x = selected.center_x if hasattr(selected, 'center_x') else selected.coordinates['x'] + selected.coordinates['width'] // 2
                    y = selected.center_y if hasattr(selected, 'center_y') else selected.coordinates['y'] + selected.coordinates['height'] // 2
                    action = TapAction(x=x, y=y)
                else:
                    print("   ❌ 클릭 가능한 요소 없음")
                    break

            # 액션 기록
            result.actions.append(action)

            # 액션 실행
            print(f"   🎯 액션 실행: TAP at ({action.x}, {action.y})")
            await device.execute_action(action)

            # 페이지 로딩 대기 (더 길게)
            print("   ⏳ 페이지 로딩 대기...")
            await asyncio.sleep(2.0)

            # URL 저장
            previous_url = current_url

    finally:
        # 연결 종료
        await device.disconnect()

    # 탐색 종료
    result.finish()

    # 4. 리포트 생성
    print("\n📊 Step 4: 리포트 생성...")
    generator = ReportGenerator()

    json_path = "./reports/web_navigation_test/report.json"
    generator.save_json_report(result, json_path)
    print(f"✅ JSON 리포트: {json_path}")

    txt_path = "./reports/web_navigation_test/report.txt"
    generator.save_text_report(result, txt_path)
    print(f"✅ 텍스트 리포트: {txt_path}")

    # 5. 결과 요약
    print("\n" + "=" * 70)
    print("✅ 웹 네비게이션 테스트 완료!")
    print("=" * 70)
    print(f"\n📈 결과:")
    print(f"   - 실행 시간: {result.duration:.1f}초")
    print(f"   - 총 이벤트: {result.total_events}개")
    print(f"   - 고유 상태: {result.unique_states}개")
    print(f"   - 방문한 URL: {len(visited_urls)}개")
    print(f"\n🌐 방문한 URL 목록:")
    for i, url in enumerate(visited_urls, 1):
        print(f"   {i}. {url}")
    print(f"\n🎯 index.json이 자동으로 업데이트되었습니다!")
    print(f"   Grafana에서 확인하세요: http://localhost:3000")

if __name__ == "__main__":
    asyncio.run(main())

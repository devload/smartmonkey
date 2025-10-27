#!/usr/bin/env python3
"""Test click execution and URL changes"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from smartmonkey.device.chrome.chrome_device import ChromeDevice
from smartmonkey.core.action import Action, ActionType

async def main():
    print("=" * 70)
    print("🧪 클릭 실행 및 URL 변경 테스트")
    print("=" * 70)

    device = ChromeDevice(device_serial="emulator-5556", cdp_port=9222)

    if not await device.connect(initial_url="https://m.naver.com"):
        print("❌ 연결 실패")
        return

    print("\n✅ m.naver.com 연결 완료")

    # 초기 URL 확인
    initial_url = await device.cdp.evaluate_js("document.URL")
    print(f"\n📍 초기 URL: {initial_url}")

    # HTML 요소 가져오기
    print("\n🔍 클릭 가능한 링크 찾기...")
    elements = await device.parser.get_clickable_elements()

    # 뉴스 링크 찾기 (href가 있는 <a> 태그)
    news_links = []
    for elem in elements:
        if elem.tag_name == 'a' and hasattr(elem, 'attributes') and 'href' in elem.attributes:
            href = elem.attributes['href']
            text = elem.text_content.strip()
            if text and len(text) > 5 and ('뉴스' in text or 'news' in href.lower()):
                news_links.append((elem, text, href))

    if not news_links:
        print("❌ 뉴스 링크를 찾을 수 없습니다")
        # 아무 링크나 사용
        for elem in elements:
            if elem.tag_name == 'a' and hasattr(elem, 'attributes') and 'href' in elem.attributes:
                href = elem.attributes['href']
                text = elem.text_content.strip()
                if text and len(text) > 5:
                    news_links.append((elem, text, href))
                    break

    if not news_links:
        print("❌ 클릭 가능한 링크가 없습니다")
        await device.disconnect()
        return

    # 첫 번째 링크 클릭
    elem, text, href = news_links[0]
    print(f"\n🎯 클릭할 링크:")
    print(f"   텍스트: {text}")
    print(f"   URL: {href}")
    print(f"   좌표: ({elem.center_x}, {elem.center_y})")

    # 스크린샷 (클릭 전)
    print("\n📸 스크린샷 캡처 (클릭 전)...")
    await device.capture_screenshot("/tmp/before_click.png")

    # 클릭 실행
    print(f"\n👆 클릭 실행: ({elem.center_x}, {elem.center_y})")
    action = Action(ActionType.TAP, x=elem.center_x, y=elem.center_y)
    await device.execute_action(action)

    # 짧은 대기
    print("   ⏳ 1초 대기...")
    await asyncio.sleep(1.0)

    # URL 확인 (1초 후)
    url_1sec = await device.cdp.evaluate_js("document.URL")
    print(f"\n📍 URL (1초 후): {url_1sec}")
    print(f"   변경됨: {'예' if url_1sec != initial_url else '아니오'}")

    # 스크린샷 (1초 후)
    print("\n📸 스크린샷 캡처 (1초 후)...")
    await device.capture_screenshot("/tmp/after_click_1sec.png")

    # 긴 대기
    print("   ⏳ 3초 더 대기...")
    await asyncio.sleep(3.0)

    # URL 확인 (4초 후)
    url_4sec = await device.cdp.evaluate_js("document.URL")
    print(f"\n📍 URL (4초 후): {url_4sec}")
    print(f"   변경됨: {'예' if url_4sec != initial_url else '아니오'}")

    # 스크린샷 (4초 후)
    print("\n📸 스크린샷 캡처 (4초 후)...")
    await device.capture_screenshot("/tmp/after_click_4sec.png")

    # 페이지 제목 확인
    title = await device.cdp.evaluate_js("document.title")
    print(f"\n📄 페이지 제목: {title}")

    await device.disconnect()

    print("\n" + "=" * 70)
    print("📊 테스트 결과 요약")
    print("=" * 70)
    print(f"초기 URL:  {initial_url}")
    print(f"1초 후 URL: {url_1sec}")
    print(f"4초 후 URL: {url_4sec}")
    print(f"")
    print(f"URL 변경: {'✅ 성공' if url_4sec != initial_url else '❌ 실패'}")
    print(f"")
    print("스크린샷 파일:")
    print("  /tmp/before_click.png")
    print("  /tmp/after_click_1sec.png")
    print("  /tmp/after_click_4sec.png")
    print("=" * 70)

if __name__ == "__main__":
    asyncio.run(main())

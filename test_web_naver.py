"""웹 테스트 - 네이버 모바일"""

import asyncio
from smartmonkey.device.chrome.chrome_device import ChromeDevice
from smartmonkey.exploration.engine import ExplorationEngine
from smartmonkey.exploration.strategies.random_strategy import RandomStrategy
from smartmonkey.reporting.report_generator import ReportGenerator

async def main():
    print("=" * 70)
    print("🌐 SmartMonkey Web Test - Naver Mobile")
    print("=" * 70)

    # 1. ChromeDevice 초기화
    print("\n📱 Step 1: ChromeDevice 초기화...")
    device = ChromeDevice(
        device_serial="emulator-5556",
        cdp_port=9222
    )

    # 2. Chrome 연결 및 네이버 모바일 접속
    print("\n🔌 Step 2: Chrome 연결 및 네이버 접속...")
    if not await device.connect(initial_url="https://m.naver.com"):
        print("❌ Chrome 연결 실패!")
        return

    print(f"✅ 연결 성공: {device.url}")

    # 3. Random Strategy로 탐색 엔진 초기화
    print("\n🎲 Step 3: Random Strategy 초기화...")
    strategy = RandomStrategy()
    engine = ExplorationEngine(device, strategy)

    # 4. 웹 탐색 실행 (10 steps)
    print("\n🚀 Step 4: 웹 탐색 시작 (10 steps)...")
    result = await engine.explore(
        max_steps=10,
        timeout_seconds=300
    )

    # 5. 결과 리포트 생성
    print("\n📊 Step 5: 리포트 생성...")
    generator = ReportGenerator()

    # JSON 리포트 저장
    json_path = "./reports/web_naver_test/report.json"
    generator.save_json_report(result, json_path)
    print(f"✅ JSON 리포트: {json_path}")

    # 텍스트 리포트 저장
    txt_path = "./reports/web_naver_test/report.txt"
    generator.save_text_report(result, txt_path)
    print(f"✅ 텍스트 리포트: {txt_path}")

    # 6. 연결 종료
    await device.disconnect()

    print("\n" + "=" * 70)
    print("✅ 웹 테스트 완료!")
    print("=" * 70)
    print(f"\n📈 결과:")
    print(f"   - 실행 시간: {result.duration:.1f}초")
    print(f"   - 총 이벤트: {result.total_events}개")
    print(f"   - 고유 상태: {result.unique_states}개")
    print(f"   - 크래시 감지: {'예' if result.crash_detected else '아니오'}")

if __name__ == "__main__":
    asyncio.run(main())

"""AI-driven testing command using Claude Code CLI"""

import asyncio
import os
from datetime import datetime
import click

from smartmonkey.device.chrome.chrome_device import ChromeDevice
from smartmonkey.device.device import Device
from smartmonkey.device.adb_manager import ADBManager
from smartmonkey.device.app_manager import AppManager
from smartmonkey.exploration.exploration_engine import ExplorationResult
from smartmonkey.exploration.strategies.ai_strategy import AIStrategy
from smartmonkey.exploration.state import AppState
from smartmonkey.reporting.report_generator import ReportGenerator


async def run_ai_test(device_serial, url, mission, steps, port, output):
    """AI 기반 웹 네비게이션 테스트 실행"""

    # output이 상대 경로면 SmartMonkey 프로젝트 기준으로 변환
    if not os.path.isabs(output):
        # SmartMonkey 프로젝트 루트 찾기
        # __file__: /Users/devload/smartMonkey/smartmonkey/cli/commands/ai_command.py
        # 4번 상위로: smartmonkey/cli/commands/ai_command.py -> smartmonkey/cli/commands -> smartmonkey/cli -> smartmonkey -> SmartMonkey
        smartmonkey_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        output = os.path.join(smartmonkey_root, output.lstrip('./'))

    # 고유한 테스트 ID 생성
    test_id = f"ai_navigation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print("=" * 70)
    print("🤖 SmartMonkey AI 모드 (Claude Code 연동)")
    print("=" * 70)
    print(f"📋 테스트 ID: {test_id}")
    print(f"📱 Device: {device_serial}")
    print(f"🌐 Start URL: {url}")
    print(f"🎯 Mission: {mission}")
    print(f"🔢 Max Steps: {steps}")
    print(f"📂 Output: {output}")
    print()
    
    # 1. ChromeDevice 초기화
    print("\n📱 Step 1: ChromeDevice 초기화...")
    device = ChromeDevice(device_serial=device_serial, cdp_port=port)
    
    # 2. 홈 화면으로 이동
    print("\n🏠 Step 2: 홈 버튼 누르기 (초기화)...")
    device.device.adb.shell("input keyevent 3")
    await asyncio.sleep(1.0)
    
    # 3. Chrome 완전 종료
    print("\n🔌 Step 3: Chrome 완전 종료...")
    device.device.adb.shell("am force-stop com.android.chrome")
    await asyncio.sleep(0.5)
    device.device.adb.shell("killall chrome 2>/dev/null || true")
    await asyncio.sleep(1.0)
    
    chrome_count = device.device.adb.shell("ps -A | grep chrome | wc -l").strip()
    print(f"   Chrome 프로세스 수: {chrome_count}")
    
    # 4. Chrome 시작
    print("\n🔌 Step 4: Chrome 시작...")
    device.device.adb.shell(f'am start -a android.intent.action.VIEW -d "{url}"')
    await asyncio.sleep(6.0)  # Chrome 시작 대기 증가

    # 포트 포워딩
    device.device.adb.execute(f"forward tcp:{port} localabstract:chrome_devtools_remote")
    await asyncio.sleep(3.0)  # 포트 포워딩 안정화 대기 증가
    
    # 5. Chrome DevTools 연결
    print("\n🔌 Step 5: Chrome DevTools 연결...")
    if not await device.connect(initial_url=url):
        print("❌ Chrome 연결 실패!")
        return
    
    print(f"✅ 연결 성공: {device.url}")
    
    # 6. 시작 페이지 캡처
    print("\n📸 시작 페이지 캡처...")
    screenshot_dir = os.path.join(output, test_id, "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    initial_screenshot = f"{screenshot_dir}/screenshot_initial.png"
    await device.capture_screenshot(initial_screenshot)
    print(f"   ✅ {initial_screenshot}")
    
    # 7. AI 탐색 시작
    print(f"\n🚀 Step 6: AI 탐색 시작 ({steps} steps)...")
    print(f"   Mission: {mission}")
    print()
    
    # AI Strategy 생성
    strategy = AIStrategy(mission=mission, workspace_dir=os.getcwd())
    
    result = ExplorationResult()
    visited_urls = set([url])
    current_step = 0
    
    try:
        while current_step < steps:
            print(f"\n{'='*70}")
            print(f"[Step {current_step + 1}/{steps}]")
            print(f"{'='*70}")
            
            # 현재 상태 가져오기
            state = await device.get_current_state()
            current_url = state.url
            
            print(f"   URL: {current_url}")
            print(f"   Elements: {len(state.elements)}개")
            
            # 요소가 없으면 종료
            if not state.elements:
                print(f"   ❌ No elements found, stopping")
                break
            
            # 상태 기록
            result.states.append(state)
            visited_urls.add(current_url)
            
            # AI에게 액션 추천 받기
            action = await strategy.select_action(state, device)
            result.actions.append(action)
            
            # 액션 실행
            print(f"\n   🎯 Executing: {action.action_type} at ({action.x if hasattr(action, 'x') else 'N/A'}, {action.y if hasattr(action, 'y') else 'N/A'})")
            await device.execute_action(action)
            
            # 페이지 로딩 대기
            print(f"   ⏳ Waiting for page load...")
            await asyncio.sleep(4.0)
            
            # 스크린샷 캡처
            screenshot_path = f"{screenshot_dir}/screenshot_{current_step:04d}.png"
            if hasattr(action, 'x') and hasattr(action, 'y'):
                await device.capture_screenshot(screenshot_path, click_x=action.x, click_y=action.y)
            else:
                await device.capture_screenshot(screenshot_path)
            print(f"   📸 Screenshot: {screenshot_path}")
            
            current_step += 1
    
    except KeyboardInterrupt:
        print("\n\n⚠️  User interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 연결 종료
        await device.disconnect()
    
    # 탐색 종료
    result.finish()
    
    # 8. 리포트 생성
    print("\n📊 Step 7: 리포트 생성...")
    generator = ReportGenerator()

    json_path = os.path.join(output, test_id, "report.json")
    generator.save_json_report(result, json_path)
    print(f"✅ JSON 리포트: {json_path}")

    txt_path = os.path.join(output, test_id, "report.txt")
    generator.save_text_report(result, txt_path)
    print(f"✅ 텍스트 리포트: {txt_path}")
    
    # 9. 결과 요약
    print("\n" + "=" * 70)
    print("✅ AI 테스트 완료!")
    print("=" * 70)
    print(f"\n📈 결과:")
    print(f"   - 실행 시간: {result.duration:.1f}초")
    print(f"   - 총 이벤트: {result.total_events}개")
    print(f"   - 고유 상태: {result.unique_states}개")
    print(f"   - 방문한 URL: {len(visited_urls)}개")
    print(f"\n🌐 방문한 URL 목록:")
    for i, url_item in enumerate(visited_urls, 1):
        print(f"   {i}. {url_item}")


async def run_ai_app_test(device_serial, package, mission, steps, output):
    """AI 기반 앱 테스트 실행 (이미지 전용 분석)"""

    # output이 상대 경로면 SmartMonkey 프로젝트 기준으로 변환
    if not os.path.isabs(output):
        smartmonkey_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        output = os.path.join(smartmonkey_root, output.lstrip('./'))

    # 고유한 테스트 ID 생성
    test_id = f"ai_app_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print("=" * 70)
    print("🤖 SmartMonkey AI 앱 모드 (Claude Code 연동)")
    print("=" * 70)
    print(f"📋 테스트 ID: {test_id}")
    print(f"📱 Device: {device_serial}")
    print(f"📦 Package: {package}")
    print(f"🎯 Mission: {mission}")
    print(f"🔢 Max Steps: {steps}")
    print(f"📂 Output: {output}")
    print()

    # 1. Device 연결
    print("\n📱 Step 1: Android 디바이스 연결...")
    adb = ADBManager()
    devices = adb.get_devices()

    if not devices:
        print("❌ 연결된 디바이스가 없습니다!")
        return

    if device_serial not in devices:
        print(f"❌ 디바이스 {device_serial}을 찾을 수 없습니다!")
        print(f"사용 가능한 디바이스: {', '.join(devices)}")
        return

    device = Device(device_serial)
    if not device.connect():
        print(f"❌ 디바이스 {device_serial} 연결 실패!")
        return

    print(f"✅ 연결 성공: {device.model}")

    # 2. 앱 시작
    print(f"\n📱 Step 2: 앱 시작 ({package})...")
    app_mgr = AppManager(device)

    # 앱이 이미 실행 중이면 종료
    app_mgr.stop_app(package)
    await asyncio.sleep(1.0)

    # 앱 시작
    if not app_mgr.launch_app(package):
        print(f"❌ 앱 시작 실패: {package}")
        return

    await asyncio.sleep(5.0)  # 앱 로딩 및 권한 다이얼로그 대기

    # 앱이 실제로 포그라운드에 있는지 확인
    current_activity = app_mgr.get_current_activity()
    if current_activity and package in current_activity:
        print(f"✅ 앱 시작 완료: {current_activity}")
    else:
        print(f"⚠️  앱이 백그라운드로 이동했습니다. 다시 포그라운드로 가져옵니다...")
        # monkey 명령어로 앱을 다시 포그라운드로
        device.adb.shell(f"monkey -p {package} -c android.intent.category.LAUNCHER 1")
        await asyncio.sleep(2.0)
        current_activity = app_mgr.get_current_activity()
        if current_activity and package in current_activity:
            print(f"✅ 앱 재시작 완료: {current_activity}")
        else:
            print(f"⚠️  앱이 여전히 포그라운드에 없습니다: {current_activity}")

    # 3. 테스트 디렉토리 준비
    test_dir = os.path.join(output, test_id)
    screenshot_dir = os.path.join(test_dir, "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)

    # claude.md 템플릿을 테스트 디렉토리에 복사
    import shutil
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        'ai', 'templates', 'app_claude.md'
    )
    claude_md_path = os.path.join(test_dir, 'claude.md')
    if os.path.exists(template_path):
        shutil.copy(template_path, claude_md_path)
        print(f"✅ Claude.md 템플릿 복사 완료: {claude_md_path}")
    else:
        print(f"⚠️  템플릿 파일을 찾을 수 없습니다: {template_path}")

    # 4. AI Strategy 생성 (workspace는 test_dir 루트)
    print(f"\n🚀 Step 3: AI 탐색 시작 ({steps} steps)...")
    print(f"   Mission: {mission}")
    print(f"   Workspace: {test_dir}")
    print()

    strategy = AIStrategy(mission=mission, workspace_dir=test_dir)

    result = ExplorationResult()
    current_step = 0

    try:
        while current_step < steps:
            print(f"\n{'='*70}")
            print(f"[Step {current_step + 1}/{steps}]")
            print(f"{'='*70}")

            # 현재 상태 생성 (앱 모드 - 요소 없음)
            # AppState는 activity와 elements를 필요로 하지만, AI 모드에서는 빈 리스트 전달
            current_activity = device.adb.shell("dumpsys activity activities | grep mResumedActivity | cut -d' ' -f8").strip()
            state = AppState(
                activity=current_activity or package,
                elements=[],  # AI 앱 모드 - 이미지만 분석
                screenshot_path=None
            )

            # URL 대신 activity 정보 저장
            state.url = current_activity or package

            print(f"   Activity: {state.url}")
            print(f"   Mode: AI App (Image-only analysis)")

            # 상태 기록
            result.states.append(state)

            # AI에게 액션 추천 받기
            action = await strategy.select_action(state, device)
            result.actions.append(action)

            # 액션 실행
            print(f"\n   🎯 Executing: {action.action_type} at ({action.x if hasattr(action, 'x') else 'N/A'}, {action.y if hasattr(action, 'y') else 'N/A'})")

            # 액션이 BackAction인 경우
            if action.action_type == "back":
                device.adb.shell("input keyevent 4")  # BACK key
            elif hasattr(action, 'x') and hasattr(action, 'y'):
                # Tap 액션
                device.adb.shell(f"input tap {action.x} {action.y}")

            # 화면 변화 대기
            print(f"   ⏳ Waiting for UI response...")
            await asyncio.sleep(2.0)

            # 스크린샷 캡처 (action 실행 후)
            screenshot_path = f"{screenshot_dir}/screenshot_{current_step:04d}.png"
            from smartmonkey.device.screen_capture import ScreenCapture
            screen_capture = ScreenCapture(device)
            screen_capture.take_screenshot(screenshot_path)
            print(f"   📸 Screenshot: {screenshot_path}")

            current_step += 1

    except KeyboardInterrupt:
        print("\n\n⚠️  User interrupted")
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

    # 탐색 종료
    result.finish()

    # 5. 리포트 생성
    print("\n📊 Step 4: 리포트 생성...")
    generator = ReportGenerator()

    json_path = os.path.join(output, test_id, "report.json")
    generator.save_json_report(result, json_path)
    print(f"✅ JSON 리포트: {json_path}")

    txt_path = os.path.join(output, test_id, "report.txt")
    generator.save_text_report(result, txt_path)
    print(f"✅ 텍스트 리포트: {txt_path}")

    # 6. 결과 요약
    print("\n" + "=" * 70)
    print("✅ AI 앱 테스트 완료!")
    print("=" * 70)
    print(f"\n📈 결과:")
    print(f"   - 실행 시간: {result.duration:.1f}초")
    print(f"   - 총 이벤트: {result.total_events}개")
    print(f"   - 고유 상태: {result.unique_states}개")


@click.command('ai')
@click.option('-d', '--device', default='emulator-5554',
              help='Android device serial (default: emulator-5554)')
@click.option('-u', '--url', default=None,
              help='Starting URL (for web testing)')
@click.option('-pkg', '--package', default=None,
              help='App package name (for app testing)')
@click.option('-m', '--mission', required=True,
              help='Mission to accomplish (e.g., "상품 검색하고 장바구니 담기")')
@click.option('-s', '--steps', type=int, default=5,
              help='Maximum number of steps (default: 5)')
@click.option('-p', '--port', type=int, default=9222,
              help='Chrome DevTools port (default: 9222, web mode only)')
@click.option('-o', '--output', default='./reports',
              help='Output directory (default: ./reports)')
def ai_command(device, url, package, mission, steps, port, output):
    """Run AI-driven testing using Claude Code CLI

    Supports both web and app testing modes:
    - Web mode: Use --url to test mobile web apps
    - App mode: Use --package to test native Android apps
    """
    # Validate: Either URL or package must be provided (but not both)
    if not url and not package:
        click.echo("❌ Error: Either --url (web mode) or --package (app mode) must be provided")
        click.echo("\nExamples:")
        click.echo("  # Web testing")
        click.echo("  smartmonkey ai --url https://m.coupang.com --mission '상품 검색하기' --steps 10")
        click.echo("\n  # App testing")
        click.echo("  smartmonkey ai --package com.coupang.mobile --mission '상품 검색하기' --steps 10")
        return

    if url and package:
        click.echo("❌ Error: Cannot use both --url and --package at the same time")
        click.echo("Please choose one mode: web (--url) or app (--package)")
        return

    # Route to appropriate test function
    if url:
        # Web mode
        asyncio.run(run_ai_test(device, url, mission, steps, port, output))
    else:
        # App mode
        asyncio.run(run_ai_app_test(device, package, mission, steps, output))

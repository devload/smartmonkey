"""Web navigation testing command"""

import asyncio
import os
from datetime import datetime
import random
import click

from smartmonkey.device.chrome.chrome_device import ChromeDevice
from smartmonkey.exploration.exploration_engine import ExplorationResult
from smartmonkey.exploration.action import TapAction, BackAction, SwipeAction
from smartmonkey.reporting.report_generator import ReportGenerator


async def is_chrome_internal_page(url: str) -> bool:
    """Chrome 내부 페이지인지 확인"""
    return url.startswith('chrome://') or url.startswith('about:')


async def is_valid_web_url(url: str) -> bool:
    """유효한 웹 URL인지 확인"""
    return url.startswith('http://') or url.startswith('https://')


async def detect_and_close_overlay(device) -> bool:
    """
    오버레이(메뉴, 모달, 사이드바)를 감지하고 닫기 시도

    Returns:
        True if overlay was detected and closed, False otherwise
    """
    try:
        # CDP를 통해 현재 DOM 가져오기
        dom_result = await device.cdp.send_command("DOM.getDocument")
        root_node_id = dom_result.get("root", {}).get("nodeId")

        if not root_node_id:
            return False

        # 일반적인 오버레이 선택자들 (보수적으로)
        overlay_selectors = [
            # 사이드 메뉴 (명확한 케이스만)
            '[class*="sidebar"][class*="open"]',
            '[class*="drawer"][class*="open"]',
            '[class*="side-menu"][class*="active"]',
            # 모달 (명확한 케이스만)
            '[class*="modal"][class*="show"]',
            '[class*="popup"][class*="active"]',
            '[class*="dialog"][class*="open"]',
            # 오버레이 배경 (명확한 케이스만)
            '[class*="modal-backdrop"]',
            '[class*="overlay"][class*="show"]',
            '[class*="mask"][class*="show"]'
        ]

        for selector in overlay_selectors:
            try:
                query_result = await device.cdp.send_command(
                    "DOM.querySelector",
                    {"nodeId": root_node_id, "selector": selector}
                )

                if query_result.get("nodeId", 0) > 0:
                    print(f"   🚨 오버레이 감지: {selector}")

                    # 닫기 버튼 찾기
                    close_selectors = [
                        'button[class*="close"]',
                        'button[class*="dismiss"]',
                        '[class*="close-btn"]',
                        '[aria-label*="close" i]',
                        '[aria-label*="닫기"]',
                        '.close', '#close',
                        'button[type="button"][class*="icon"]'
                    ]

                    for close_selector in close_selectors:
                        try:
                            close_result = await device.cdp.send_command(
                                "DOM.querySelector",
                                {"nodeId": root_node_id, "selector": close_selector}
                            )

                            close_node_id = close_result.get("nodeId", 0)
                            if close_node_id > 0:
                                # 닫기 버튼 클릭
                                await device.cdp.send_command(
                                    "DOM.focus",
                                    {"nodeId": close_node_id}
                                )
                                await device.cdp.send_command(
                                    "DOM.click",
                                    {"nodeId": close_node_id}
                                )
                                print(f"   ✅ 오버레이 닫기 버튼 클릭: {close_selector}")
                                await asyncio.sleep(1.0)
                                return True
                        except:
                            continue

                    # 닫기 버튼이 없으면 Back 버튼 사용
                    print(f"   ⬅️  닫기 버튼 없음, Back 버튼 사용")
                    device.event_injector.press_back()
                    await asyncio.sleep(1.0)
                    return True

            except:
                continue

        return False

    except Exception as e:
        print(f"   ⚠️  오버레이 감지 실패: {e}")
        return False


def filter_safe_elements(elements, min_y=150):
    """안전한 요소만 필터링 (브라우저 UI 및 앱 링크 제외)"""
    safe_elements = []
    for elem in elements:
        # URL 바 영역 제외 (상단 min_y px)
        if elem.center_y < min_y:
            continue

        # 브라우저 내부 링크만 허용
        if hasattr(elem, 'attributes'):
            href = elem.attributes.get('href', '')

            # chrome://, about:, chrome-native:// 링크 제외
            if href.startswith('chrome://') or href.startswith('about:') or href.startswith('chrome-native://'):
                continue

            # 앱 딥링크 제외 (/naverapp/, intent://, etc.)
            if href.startswith('/naverapp/') or href.startswith('intent://'):
                continue

            # 상대 경로 링크 중 앱 관련 제외
            if href.startswith('/') and 'app' in href.lower():
                continue

        # 텍스트가 브라우저 UI 관련인지 체크
        if hasattr(elem, 'text_content') and elem.text_content:
            text_lower = elem.text_content.lower().strip()
            # 브라우저 UI 텍스트 제외
            browser_ui_keywords = ['새 탭', 'new tab', '홈', 'home', '뒤로', 'back', '앞으로', 'forward']
            if any(keyword in text_lower for keyword in browser_ui_keywords):
                continue

        safe_elements.append(elem)

    return safe_elements


async def run_web_test(device_serial, url, steps, port, url_bar_height, output, stuck_threshold):
    """웹 네비게이션 테스트 실행"""

    # output이 상대 경로면 SmartMonkey 프로젝트 기준으로 변환
    if not os.path.isabs(output):
        # SmartMonkey 프로젝트 루트 찾기
        smartmonkey_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
        output = os.path.join(smartmonkey_root, output.lstrip('./'))

    # 고유한 테스트 ID 생성 (타임스탬프 기반)
    test_id = f"web_navigation_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print("=" * 70)
    print("🌐 SmartMonkey 웹 네비게이션 테스트")
    print("=" * 70)
    print(f"📋 테스트 ID: {test_id}")
    print(f"📱 Device: {device_serial}")
    print(f"🌐 Start URL: {url}")
    print(f"🔢 Steps: {steps}")
    print(f"📂 Output: {output}")

    # 1. ChromeDevice 초기화
    print("\n📱 Step 1: ChromeDevice 초기화...")
    device = ChromeDevice(device_serial=device_serial, cdp_port=port)

    # 2. 홈 화면으로 이동 (초기화)
    print("\n🏠 Step 2: 홈 버튼 누르기 (초기화)...")
    device.device.adb.shell("input keyevent 3")  # KEYCODE_HOME
    await asyncio.sleep(1.0)

    # Chrome 완전 종료 (모든 프로세스 강제 종료)
    print("\n🔌 Step 3: Chrome 완전 종료...")
    device.device.adb.shell("am force-stop com.android.chrome")
    await asyncio.sleep(0.5)
    # killall로 남아있는 프로세스 정리
    device.device.adb.shell("killall chrome 2>/dev/null || true")
    await asyncio.sleep(1.0)

    # Chrome 프로세스 확인
    chrome_count = device.device.adb.shell("ps -A | grep chrome | wc -l").strip()
    print(f"   Chrome 프로세스 수: {chrome_count}")

    print("\n🔌 Step 4: Chrome 시작...")

    # Chrome을 지정된 URL로 실행
    device.device.adb.shell(f'am start -n com.android.chrome/com.google.android.apps.chrome.Main -d "{url}"')
    await asyncio.sleep(4.0)  # Chrome 시작 대기 시간 증가

    # 포트 포워딩 재설정
    device.device.adb.execute(f"forward tcp:{port} localabstract:chrome_devtools_remote")
    await asyncio.sleep(2.0)  # 포트 포워딩 안정화 대기 시간 증가

    print("\n🔌 Step 5: Chrome DevTools 연결...")
    initial_url = url
    if not await device.connect(initial_url=initial_url):
        print("❌ Chrome 연결 실패!")
        return

    print(f"✅ 연결 성공: {device.url}")

    # 시작 페이지 캡처
    print("\n📸 시작 페이지 캡처...")
    screenshot_dir = os.path.join(output, test_id, "screenshots")
    os.makedirs(screenshot_dir, exist_ok=True)
    initial_screenshot_path = f"{screenshot_dir}/screenshot_initial.png"
    await device.capture_screenshot(initial_screenshot_path)
    print(f"   ✅ 시작 페이지 스크린샷: {initial_screenshot_path}")

    # 6. 탐색 실행
    print(f"\n🚀 Step 6: 웹 네비게이션 시작 ({steps} actions)...")

    result = ExplorationResult()
    visited_urls = set()
    visited_urls.add(initial_url)
    previous_url = initial_url
    stuck_count = 0  # 같은 페이지에서 반복 카운트
    current_step = 0  # 실제 실행된 스텝 수 (스와이프 포함)
    action_count = 0  # 탭/백 액션 수 (스와이프 제외)

    try:
        while action_count < steps:
            print(f"\n[Step {current_step+1}] (Action {action_count+1}/{steps})")

            # 현재 상태 가져오기
            state = await device.get_current_state()
            current_url = state.url

            print(f"   URL: {current_url}")
            print(f"   Elements: {len(state.elements)}개")

            # Chrome 내부 페이지 감지
            if await is_chrome_internal_page(current_url):
                print(f"   ⚠️  Chrome 내부 페이지 감지! Back 버튼으로 복귀...")
                device.event_injector.press_back()
                await asyncio.sleep(1.5)
                continue

            # URL 변경 감지
            if previous_url and previous_url != current_url:
                print(f"   ✨ 새로운 페이지로 이동!")
                visited_urls.add(current_url)
                stuck_count = 0  # 리셋
            elif current_url not in visited_urls:
                print(f"   → 새로운 URL 발견")
                visited_urls.add(current_url)
                stuck_count = 0  # 리셋
            else:
                stuck_count += 1
                print(f"   → 같은 페이지 (반복 {stuck_count}회)")

                # N번 연속 같은 페이지면 Back 버튼
                if stuck_count >= stuck_threshold:
                    print(f"   ⚠️  {stuck_threshold}회 반복, Back 버튼으로 이동 시도...")
                    # Back 액션 생성 및 기록
                    action = BackAction()
                    result.actions.append(action)

                    # Back 버튼 실행
                    device.event_injector.press_back()
                    await asyncio.sleep(1.5)

                    # Back 후 스크린샷 캡처
                    screenshot_dir = os.path.join(output, test_id, "screenshots")
                    os.makedirs(screenshot_dir, exist_ok=True)
                    screenshot_path = f"{screenshot_dir}/screenshot_{current_step:04d}.png"

                    # 스크린샷 캡처 (클릭 마커 없음 - Back 액션이므로)
                    screenshot_success = False
                    for retry in range(3):
                        if await device.capture_screenshot(screenshot_path):
                            screenshot_success = True
                            print(f"   📸 Screenshot after BACK: {screenshot_path}")
                            break
                        else:
                            print(f"   ⚠️ Screenshot capture failed (attempt {retry + 1}/3)")
                            await asyncio.sleep(1.0)

                    if not screenshot_success:
                        print(f"   ❌ Failed to capture screenshot after 3 attempts: {screenshot_path}")

                    current_step += 1  # Back도 스텝으로 카운트
                    action_count += 1  # Back도 액션으로 카운트
                    stuck_count = 0
                    continue

            # 상태 기록
            result.states.append(state)

            # **안전한 요소 필터링** - URL 바 제외
            safe_elements = filter_safe_elements(state.elements, min_y=url_bar_height)
            print(f"   🛡️  안전한 요소: {len(safe_elements)}개 (URL 바 제외)")

            if not safe_elements:
                print(f"   ❌ 안전한 클릭 가능 요소 없음")
                break

            # **개선된 액션 선택**: 네비게이션 링크 우선
            navigation_links = []
            for elem in safe_elements:
                if elem.tag_name == 'a':
                    href = elem.attributes.get('href') if hasattr(elem, 'attributes') else None
                    if href:
                        # 유효한 웹 URL만 선택 (chrome:// 제외)
                        if href.startswith('http') or href.startswith('/'):
                            # 현재 URL과 다른 경로인지 확인
                            if href not in visited_urls and href != current_url:
                                # chrome:// 링크 제외
                                if not href.startswith('chrome://'):
                                    navigation_links.append(elem)

            if navigation_links:
                print(f"   🔗 네비게이션 링크 {len(navigation_links)}개 발견")
                # 무작위로 하나 선택
                selected = random.choice(navigation_links)
                x = selected.center_x if hasattr(selected, 'center_x') else selected.coordinates['x'] + selected.coordinates['width'] // 2
                y = selected.center_y if hasattr(selected, 'center_y') else selected.coordinates['y'] + selected.coordinates['height'] // 2
                action = TapAction(x=x, y=y)
                link_text = selected.text_content.strip()[:40] if selected.text_content else "텍스트 없음"
                href = selected.attributes.get('href', '')
                print(f"   → 선택한 링크: {link_text}")
                print(f"   → 목적지: {href[:60]}")
            else:
                # 네비게이션 링크가 없으면 안전한 요소 중에서 선택
                print(f"   ⚠️  네비게이션 링크 없음, 안전한 요소 선택")
                selected = random.choice(safe_elements)
                x = selected.center_x if hasattr(selected, 'center_x') else selected.coordinates['x'] + selected.coordinates['width'] // 2
                y = selected.center_y if hasattr(selected, 'center_y') else selected.coordinates['y'] + selected.coordinates['height'] // 2
                action = TapAction(x=x, y=y)

            # 화면 크기 확인 및 스크롤 필요 여부 판단
            screen_size_output = device.device.adb.shell("wm size").strip()
            if ":" in screen_size_output:
                size_str = screen_size_output.split(":")[-1].strip()
                screen_width, screen_height = map(int, size_str.split("x"))
            else:
                screen_width, screen_height = 1080, 2400  # 기본값

            # Y 좌표가 화면을 벗어나면 스크롤 먼저 수행 (독립 스텝으로)
            if action.y > screen_height - 100:  # 하단 100px 버퍼
                # 스크롤 전에 오버레이(메뉴/모달) 감지 및 닫기
                print(f"   🔍 스크롤 전 오버레이 감지...")
                overlay_closed = await detect_and_close_overlay(device)

                if overlay_closed:
                    # 오버레이를 닫았으므로 DOM이 변경됨, 현재 상태 재확인
                    print(f"   🔄 오버레이 닫음, DOM 재확인...")
                    await asyncio.sleep(1.0)
                    state = await device.get_current_state()
                    safe_elements = filter_safe_elements(state.elements, min_y=url_bar_height)

                    # 새로운 요소 선택 (오버레이 제거 후)
                    if safe_elements:
                        selected = random.choice(safe_elements)
                        x = selected.center_x if hasattr(selected, 'center_x') else selected.coordinates['x'] + selected.coordinates['width'] // 2
                        y = selected.center_y if hasattr(selected, 'center_y') else selected.coordinates['y'] + selected.coordinates['height'] // 2
                        action = TapAction(x=x, y=y)
                        print(f"   🎯 오버레이 닫은 후 새 요소 선택: ({x}, {y})")

                # 여전히 화면 밖이면 스크롤
                if action.y > screen_height - 100:
                    # 사람처럼 자연스러운 스크롤: 하단 65% → 상단 35% (약 30% 거리)
                    scroll_start_y = int(screen_height * 0.65)  # 하단에서 적절한 margin
                    scroll_end_y = int(screen_height * 0.35)    # 상단에 충분한 margin
                    scroll_distance = scroll_start_y - scroll_end_y
                    print(f"   📜 요소가 화면 밖 (y={action.y}), 자연스러운 스크롤 수행 ({scroll_distance}px)")

                    # 스크롤 액션 생성 (아래로 스와이프 = 위로 스크롤)
                    swipe_action = SwipeAction(
                        x1=screen_width // 2,
                        y1=scroll_start_y,
                        x2=screen_width // 2,
                        y2=scroll_end_y,
                        duration=500
                    )
                    result.actions.append(swipe_action)
                    await device.execute_action(swipe_action)
                    await asyncio.sleep(2.0)  # 스크롤 후 안정화 대기

                    # 스크롤 후 스크린샷 캡처 (독립 스텝으로, 스와이프 마커 표시)
                    screenshot_dir = os.path.join(output, test_id, "screenshots")
                    os.makedirs(screenshot_dir, exist_ok=True)
                    scroll_screenshot_path = f"{screenshot_dir}/screenshot_{current_step:04d}.png"
                    await device.capture_screenshot(
                        scroll_screenshot_path,
                        swipe_start_x=screen_width // 2,
                        swipe_start_y=scroll_start_y,
                        swipe_end_x=screen_width // 2,
                        swipe_end_y=scroll_end_y
                    )
                    print(f"   📸 스크롤 스크린샷 (Step {current_step}): {scroll_screenshot_path}")

                    current_step += 1  # 스와이프도 독립 스텝으로 카운트

                    # 요소 위치 재계산 (스크롤 후 DOM 변경 가능)
                    # 원래 요소가 화면 밖에 있었으므로, 스크롤 후 하단 1/3 지점에 위치하도록 조정
                    action.y = int(screen_height * 0.7)  # 화면 하단 70% 지점

            # 액션 기록
            result.actions.append(action)

            # 액션 실행
            print(f"   🎯 액션 실행: TAP at ({action.x}, {action.y})")
            await device.execute_action(action)

            # 페이지 로딩 대기 (충분히 길게 - 4초)
            print(f"   ⏳ 페이지 로딩 대기 (4초)...")
            await asyncio.sleep(4.0)

            # **스크린샷 캡처 (클릭 후 페이지 로딩 완료 후, 클릭 위치 표시)**
            screenshot_dir = os.path.join(output, test_id, "screenshots")
            os.makedirs(screenshot_dir, exist_ok=True)
            screenshot_path = f"{screenshot_dir}/screenshot_{current_step:04d}.png"

            # 스크린샷 캡처 시도 (최대 3번 재시도)
            screenshot_success = False
            for retry in range(3):
                if await device.capture_screenshot(screenshot_path, click_x=action.x, click_y=action.y):
                    screenshot_success = True
                    print(f"   📸 TAP 스크린샷 (Step {current_step}): {screenshot_path}")
                    break
                else:
                    print(f"   ⚠️ Screenshot capture failed (attempt {retry + 1}/3)")
                    await asyncio.sleep(1.0)

            if not screenshot_success:
                print(f"   ❌ Failed to capture screenshot after 3 attempts: {screenshot_path}")

            # 스텝 카운터 증가
            current_step += 1
            action_count += 1

            # URL 저장
            previous_url = current_url

    finally:
        # 연결 종료
        await device.disconnect()

    # 탐색 종료
    result.finish()

    # 7. 리포트 생성
    print("\n📊 Step 7: 리포트 생성...")
    generator = ReportGenerator()

    # 메인 reports 디렉토리에 저장 (Grafana 통합을 위해)
    json_path = os.path.join(output, test_id, "report.json")
    generator.save_json_report(result, json_path)
    print(f"✅ JSON 리포트: {json_path}")

    txt_path = os.path.join(output, test_id, "report.txt")
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


@click.command('web')
@click.option('-d', '--device', default='emulator-5554',
              help='Android device serial (default: emulator-5554)')
@click.option('-u', '--url', default='https://m.naver.com',
              help='Starting URL (default: https://m.naver.com)')
@click.option('-s', '--steps', type=int, default=10,
              help='Number of exploration steps (default: 10)')
@click.option('-p', '--port', type=int, default=9222,
              help='Chrome DevTools Protocol port (default: 9222)')
@click.option('--url-bar-height', type=int, default=150,
              help='URL bar height in pixels to exclude from clicks (default: 150)')
@click.option('-o', '--output', default='./reports',
              help='Output directory for reports (default: ./reports)')
@click.option('--stuck-threshold', type=int, default=5,
              help='Number of same-page repetitions before pressing back (default: 5)')
def web_command(device, url, steps, port, url_bar_height, output, stuck_threshold):
    """Run web navigation testing using Chrome DevTools"""
    asyncio.run(run_web_test(device, url, steps, port, url_bar_height, output, stuck_threshold))

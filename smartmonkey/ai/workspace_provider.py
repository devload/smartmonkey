"""Workspace-based AI provider using Claude Code"""

import json
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
from ..utils.logger import get_logger

logger = get_logger(__name__)


class WorkspaceAIProvider:
    """
    Workspace-based AI provider that communicates with Claude Code via files.

    Creates a workspace directory with CLAUDE.md, scenario files, and current state.
    Claude Code analyzes the files and creates response.json with the next action.
    """

    def __init__(
        self,
        workspace_dir: str,
        test_goal: str,
        test_config: Dict,
        package_name: str
    ):
        """
        Initialize workspace AI provider

        Args:
            workspace_dir: Directory for AI workspace
            test_goal: Natural language test goal
            test_config: Test configuration (credentials, scenario type, etc.)
            package_name: Android app package name
        """
        self.workspace = Path(workspace_dir)
        self.test_goal = test_goal
        self.test_config = test_config
        self.package_name = package_name

        # Initialize workspace
        self._init_workspace()

    def _init_workspace(self):
        """Create workspace folder structure"""
        logger.info(f"Initializing AI workspace: {self.workspace}")

        # Create folders if they don't exist (don't delete existing workspace)
        self.workspace.mkdir(parents=True, exist_ok=True)
        (self.workspace / "scenarios").mkdir(exist_ok=True)
        (self.workspace / "current_state").mkdir(exist_ok=True)

        # Clean old response file if exists
        response_file = self.workspace / "response.json"
        if response_file.exists():
            response_file.unlink()

        # Create CLAUDE.md
        self._create_claude_md()

        # Create test_config.json
        with open(self.workspace / "test_config.json", "w") as f:
            json.dump(self.test_config, f, indent=2, ensure_ascii=False)

        # Copy scenario files
        self._copy_scenarios()

        logger.info("✅ Workspace initialized")

    def _create_claude_md(self):
        """Create CLAUDE.md with instructions for Claude Code"""

        # Format test credentials
        credentials = self.test_config.get("credentials", {})
        credentials_json = json.dumps(credentials, indent=2, ensure_ascii=False)

        claude_md_content = f"""# SmartMonkey AI Testing Session

## 🎯 Your Role
You are an AI testing assistant for SmartMonkey, an Android app automated testing tool.
Your job is to analyze screenshots and UI elements, then decide the next action to achieve the test goal.

## 📋 Test Configuration
- **Package**: {self.package_name}
- **Test Goal**: {self.test_goal}
- **Test Type**: {self.test_config.get('scenario_type', 'custom')}

## 🔑 Test Credentials
```json
{credentials_json}
```

## 📚 Known Scenarios
Check the `scenarios/` folder for learned test patterns:
- `login.md` - Login flow patterns
- `checkout.md` - Shopping cart and checkout patterns
- `settings.md` - Settings navigation patterns

## 📂 Current Test State
- **Screenshot**: `current_state/screenshot.png` - ALWAYS check this first!
- **UI Elements**: `current_state/ui_elements.json` - Available clickable elements
- **History**: `current_state/history.json` - Previous actions taken

## ⚙️ How to Proceed

### Step 1: Analyze Current State
Read these files:
1. `current_state/screenshot.png` - What do you see on screen?
2. `current_state/ui_elements.json` - What elements are clickable?
3. `current_state/history.json` - What actions were already taken?

### Step 2: Decide Next Action
Based on the test goal and current screen, determine:
- What should be the next action?
- Which UI element should be interacted with?
- Is the goal achieved?

### Step 3: Write Response
Create `response.json` with this exact format:

```json
{{
  "reasoning": "Explain what you see and why you chose this action",
  "action_type": "tap | input | swipe_up | swipe_down | back | done",
  "target_element_index": 0,
  "input_text": "text to input (only for input action)",
  "confidence": 0.95,
  "goal_achieved": false,
  "next_expected_screen": "Description of what should appear next"
}}
```

## 📖 Action Types
- **tap**: Click on a UI element (button, link, etc.)
- **input**: Enter text into a text field
- **swipe_up**: Scroll down (content moves up)
- **swipe_down**: Scroll up (content moves down)
- **back**: Press back button
- **done**: Test goal is achieved, stop testing

## 🎯 Test Goal
{self.test_goal}

## ⚠️ Important Rules
1. ALWAYS look at the screenshot first before deciding
2. ALWAYS check ui_elements.json to find the exact element index
3. NEVER guess element indices - they must exist in ui_elements.json
4. If you're unsure, choose "back" or "done"
5. Explain your reasoning clearly for debugging
6. Consider the action history to avoid loops
7. If you see the same screen 3+ times, try a different action or "back"

## 🔄 Workflow
1. SmartMonkey captures screenshot and UI elements
2. SmartMonkey updates files in `current_state/`
3. **YOU analyze and create `response.json`**
4. SmartMonkey reads your response and executes the action
5. Repeat until goal is achieved or max steps reached

---

🚀 Please analyze the current state and create `response.json` now!
"""

        with open(self.workspace / "CLAUDE.md", "w") as f:
            f.write(claude_md_content)

        logger.info("✅ CLAUDE.md created")

    def _copy_scenarios(self):
        """Create learned scenario files"""

        scenarios = {
            "login.md": """# Login Scenario - Learned Patterns

## Common Login Flows

### Pattern 1: Email + Password
1. Find email/ID input field (usually contains "email", "id", "username", "계정")
2. Enter test email from credentials
3. Find password input field (usually contains "password", "pw", "비밀번호")
4. Enter test password from credentials
5. Find login button (usually contains "login", "로그인", "sign in", "submit")
6. Click login button

### Pattern 2: Phone Number Login
1. Find phone input field (contains "phone", "전화", "번호")
2. Enter phone number from credentials
3. Request verification code (contains "인증", "code", "verify")
4. Enter verification code

### Pattern 3: Social Login
1. Look for social login buttons (Kakao, Naver, Google, Facebook)
2. Usually yellow button for Kakao, green for Naver
3. Click preferred social button
4. Handle webview authentication

## Success Indicators
- Main screen appears
- User profile/name visible
- "로그인 성공" or "Login successful" message
- Navigation changes from login to main
- Bottom navigation bar appears

## Common Element Identifiers
- Email field: resource_id contains "email", "id", "username"
- Password field: resource_id contains "password", "pw", "passwd"
- Login button: text contains "login", "로그인", "sign in", class is Button

## Common Issues
- Already logged in: Skip login flow, goal achieved
- Wrong credentials: Look for error message, retry not recommended
- Network error: Wait and retry or report
""",

            "checkout.md": """# Checkout/Purchase Scenario Patterns

## Common E-commerce Flow

### Pattern 1: Product to Cart
1. Find product (search or browse)
2. Click product item
3. Look for "장바구니", "cart", "add to cart" button
4. Click add to cart
5. Go to cart (usually cart icon in top-right)

### Pattern 2: Checkout Process
1. In cart screen, find "구매", "checkout", "buy now" button
2. Click checkout
3. Enter shipping address (if required)
4. Select payment method
5. Review order
6. Confirm purchase

## Success Indicators
- "주문 완료", "Order complete" message
- Order confirmation screen
- Order number displayed

## Common Buttons
- Add to cart: "담기", "장바구니", "cart"
- Buy now: "바로구매", "buy now", "purchase"
- Checkout: "결제", "checkout", "pay"
""",

            "settings.md": """# Settings Navigation Patterns

## How to Find Settings
1. Look for "Settings", "설정", gear icon (⚙️)
2. Usually located in:
   - Bottom navigation bar (rightmost)
   - Top-right menu (hamburger ≡ or three dots ⋮)
   - Side drawer menu
   - Profile/My page section

## Common Settings Paths
- Profile → Settings
- Menu → Settings
- More → Settings
- My Page → Settings

## Settings Screen Indicators
- List of options (notification, account, privacy, etc.)
- Toggle switches
- Nested menu items
- "설정", "Settings" in title

## Common Settings Items
- Notification settings: "알림", "notification"
- Account settings: "계정", "account"
- Privacy: "프라이버시", "privacy"
- Language: "언어", "language"
- Logout: "로그아웃", "logout", "sign out"
""",
        }

        for filename, content in scenarios.items():
            with open(self.workspace / "scenarios" / filename, "w") as f:
                f.write(content)

        logger.info(f"✅ {len(scenarios)} scenario files created")

    def analyze_and_wait(
        self,
        state,
        step: int,
        max_steps: int,
        history: List[Dict]
    ) -> Dict:
        """
        Save current state to workspace and wait for Claude Code's response

        Args:
            state: Current app state
            step: Current step number
            max_steps: Maximum steps
            history: Action history

        Returns:
            Claude Code's response (JSON dict)
        """

        # 1. Copy screenshot
        if state.screenshot_path:
            screenshot_dest = self.workspace / "current_state" / "screenshot.png"
            shutil.copy(state.screenshot_path, screenshot_dest)
            logger.info(f"📸 Screenshot copied: {screenshot_dest}")

        # 2. Save UI elements
        ui_elements = [
            {
                "index": i,
                "class_name": elem.class_name,
                "text": elem.text,
                "content_desc": elem.content_desc,
                "resource_id": elem.resource_id,
                "clickable": elem.clickable,
                "scrollable": elem.scrollable,
                "bounds": {
                    "left": elem.bounds.left,
                    "top": elem.bounds.top,
                    "right": elem.bounds.right,
                    "bottom": elem.bounds.bottom,
                    "center_x": elem.bounds.center[0],
                    "center_y": elem.bounds.center[1]
                },
                "visit_count": elem.visit_count
            }
            for i, elem in enumerate(state.get_clickable_elements())
        ]

        with open(self.workspace / "current_state" / "ui_elements.json", "w") as f:
            json.dump(ui_elements, f, indent=2, ensure_ascii=False)

        logger.info(f"📋 UI elements saved: {len(ui_elements)} clickable elements")

        # 3. Save history
        with open(self.workspace / "current_state" / "history.json", "w") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

        logger.info(f"📜 History saved: {len(history)} previous actions")

        # 4. Update CLAUDE.md status
        self._update_claude_md_status(step, max_steps, len(history))

        # 5. Delete previous response
        response_file = self.workspace / "response.json"
        if response_file.exists():
            response_file.unlink()

        # 6. Print instructions for user
        self._print_instructions(step, max_steps)

        # 7. Wait for response.json
        logger.info(f"\n⏳ Waiting for auto_responder to create: {response_file}")
        logger.info(f"⏱️  Timeout: 30 seconds\n")

        timeout = 30  # 30 seconds (auto_responder should respond within 1-2s)
        start_time = time.time()

        while not response_file.exists():
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise TimeoutError(
                    f"Auto_responder timeout after {timeout}s. "
                    f"Expected file: {response_file}\n"
                    f"Check if auto_responder is running: ps aux | grep auto_responder"
                )

            # Print status every 5 seconds
            if int(elapsed) % 5 == 0 and int(elapsed) > 0:
                logger.info(f"⏳ Still waiting... ({int(elapsed)}s elapsed)")

            time.sleep(0.5)  # Check every 0.5 seconds for faster response

        # 8. Read response
        logger.info(f"✅ Response received!")
        with open(response_file) as f:
            response = json.load(f)

        logger.info(f"🤖 AI Decision: {response.get('action_type')}")
        logger.info(f"💭 Reasoning: {response.get('reasoning')}")

        return response

    def _update_claude_md_status(self, step: int, max_steps: int, actions_taken: int):
        """Update CLAUDE.md with current status"""
        claude_md = self.workspace / "CLAUDE.md"

        with open(claude_md, "r") as f:
            content = f.read()

        # Update status section
        status = f"""
---

**Current Step**: {step + 1}/{max_steps}
**Actions Taken**: {actions_taken}
**Status**: 🟢 Waiting for your analysis

🚀 Please analyze the current state and create `response.json` now!
"""

        # Remove old status section and add new one
        if "---\n\n**Current Step**:" in content:
            content = content.split("---\n\n**Current Step**:")[0]

        content += status

        with open(claude_md, "w") as f:
            f.write(content)

    def _print_instructions(self, step: int, max_steps: int):
        """Print instructions for Claude Code user"""
        print("\n" + "="*70)
        print("🤖 AI DECISION REQUIRED")
        print("="*70)
        print(f"\n📍 Step: {step + 1}/{max_steps}")
        print(f"📂 Workspace: {self.workspace.absolute()}")
        print(f"🎯 Goal: {self.test_goal}")
        print("\n📋 Files to analyze:")
        print(f"  1. CLAUDE.md - Instructions")
        print(f"  2. current_state/screenshot.png - Screenshot")
        print(f"  3. current_state/ui_elements.json - Clickable elements")
        print(f"  4. current_state/history.json - Previous actions")
        print("\n🎬 Action needed:")
        print(f"  → Open workspace in Claude Code")
        print(f"  → Analyze the files")
        print(f"  → Create response.json")
        print("\n💡 Quick command:")
        print(f"  cd {self.workspace.absolute()}")
        print("\n" + "="*70 + "\n")

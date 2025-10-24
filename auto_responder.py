#!/usr/bin/env python3
"""
Auto responder for AI testing - automatically creates response.json based on test goal
"""

import json
import time
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class AIResponder(FileSystemEventHandler):
    def __init__(self, workspace_dir):
        self.workspace = Path(workspace_dir)
        self.current_state = self.workspace / "current_state"
        self.response_file = self.workspace / "response.json"
        self.click_counts = {}  # Track clicks per button per screen

    def on_modified(self, event):
        """Watch for ui_elements.json updates"""
        if event.src_path.endswith("ui_elements.json"):
            print(f"\n📝 UI elements modified, analyzing...")
            time.sleep(0.5)  # Wait for file write to complete
            self.create_response()

    def on_created(self, event):
        """Watch for ui_elements.json creation"""
        if event.src_path.endswith("ui_elements.json"):
            print(f"\n📝 UI elements created, analyzing...")
            time.sleep(0.5)  # Wait for file write to complete
            self.create_response()

    def create_response(self):
        """Create intelligent response based on test goal"""
        try:
            # Load current state
            ui_elements = self.load_json(self.current_state / "ui_elements.json")
            history = self.load_json(self.current_state / "history.json")

            if not ui_elements:
                print("❌ No UI elements found")
                return

            # Analyze history to track button clicks
            functional_buttons = []
            nav_button = None

            for i, elem in enumerate(ui_elements):
                text = elem.get("text", "")
                if "GO TO SCREEN" in text or "다음 화면" in text or "NEXT" in text.upper():
                    nav_button = (i, text)
                else:
                    functional_buttons.append((i, text))

            # Count clicks from history for functional buttons
            screen_button_clicks = {}
            for action in history:
                idx = action.get("target_element_index")
                if idx is not None and idx < len(ui_elements):
                    button_text = ui_elements[idx].get("text", f"button_{idx}")
                    screen_button_clicks[button_text] = screen_button_clicks.get(button_text, 0) + 1

            print(f"\n📊 Analysis:")
            print(f"  Functional buttons: {len(functional_buttons)}")
            print(f"  Navigation button: {nav_button}")
            print(f"  Click history: {screen_button_clicks}")

            # Decide action: Test functional buttons 3x each, then navigate
            least_clicked_button = None
            min_clicks = 999

            for idx, text in functional_buttons:
                clicks = screen_button_clicks.get(text, 0)
                if clicks < min_clicks:
                    min_clicks = clicks
                    least_clicked_button = (idx, text, clicks)

            # Decision logic
            if least_clicked_button and least_clicked_button[2] < 3:
                # Still need to test functional buttons
                idx, text, clicks = least_clicked_button
                response = {
                    "reasoning": f"Testing functional button '{text}' ({clicks + 1}/3 clicks). Need to click each button 3 times before navigating.",
                    "action_type": "tap",
                    "target_element_index": idx,
                    "input_text": None,
                    "confidence": 1.0,
                    "goal_achieved": False,
                    "next_expected_screen": f"Same screen, testing '{text}' button functionality"
                }
            elif nav_button:
                # All functional buttons tested, navigate to next screen
                idx, text = nav_button
                response = {
                    "reasoning": f"All functional buttons tested 3+ times. Now clicking navigation button '{text}' to move to next screen.",
                    "action_type": "tap",
                    "target_element_index": idx,
                    "input_text": None,
                    "confidence": 1.0,
                    "goal_achieved": False,
                    "next_expected_screen": "Next screen should appear"
                }
            else:
                # No navigation button, try back
                response = {
                    "reasoning": "All buttons tested but no navigation button found. Trying back action.",
                    "action_type": "back",
                    "confidence": 0.8,
                    "goal_achieved": False,
                    "next_expected_screen": "Previous screen or app exit"
                }

            # Write response
            with open(self.response_file, "w") as f:
                json.dump(response, f, indent=2, ensure_ascii=False)

            print(f"✅ Response created: {response['action_type']}")
            print(f"💭 Reasoning: {response['reasoning']}")

        except Exception as e:
            print(f"❌ Error creating response: {e}")
            import traceback
            traceback.print_exc()

    def load_json(self, filepath):
        """Load JSON file"""
        try:
            if filepath.exists():
                with open(filepath) as f:
                    return json.load(f)
        except:
            pass
        return []

if __name__ == "__main__":
    workspace = "./ai_workspace"

    print("🤖 Auto Responder Started")
    print(f"📂 Watching: {workspace}")
    print("⏸️  Press Ctrl+C to stop\n")

    responder = AIResponder(workspace)

    # Start watching
    observer = Observer()
    observer.schedule(responder, str(Path(workspace) / "current_state"), recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n\n🛑 Auto Responder stopped")

    observer.join()

"""Simple report generator"""

import os
import json
from datetime import datetime
from typing import List
from ..exploration.exploration_engine import ExplorationResult
from ..utils.logger import get_logger
from ..utils.helpers import ensure_dir

logger = get_logger(__name__)


class ReportGenerator:
    """Generate exploration reports"""

    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url

    def _get_screenshot_url(self, output_path: str, screenshot_path: str, step: int) -> str:
        """
        Generate HTTP URL for screenshot

        Args:
            output_path: Path to report.json
            screenshot_path: Relative screenshot path
            step: Step number

        Returns:
            HTTP URL for screenshot
        """
        # Extract report folder name from output_path
        # e.g., ./reports/grafana_test/report.json -> grafana_test
        import re
        match = re.search(r'reports/([^/]+)/', output_path)
        if match:
            report_name = match.group(1)
            return f"{self.base_url}/{report_name}/screenshots/screenshot_{step:04d}.png"

        # Fallback
        return f"{self.base_url}/screenshots/screenshot_{step:04d}.png"

    def generate_text_report(self, result: ExplorationResult) -> str:
        """
        Generate text summary report

        Args:
            result: Exploration result

        Returns:
            Text report
        """
        lines = []
        lines.append("=" * 60)
        lines.append("SmartMonkey Exploration Report")
        lines.append("=" * 60)
        lines.append("")
        lines.append(f"Start Time: {result.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        if result.end_time:
            lines.append(f"End Time: {result.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"Duration: {result.duration:.1f} seconds")
        lines.append("")
        lines.append(f"Total Events: {result.total_events}")
        lines.append(f"Unique States: {result.unique_states}")
        lines.append(f"Total States Visited: {len(result.states)}")
        lines.append("")

        # Crash detection
        if result.crash_detected:
            lines.append("🔴 CRASH DETECTED!")
            lines.append("-" * 60)
            lines.append(f"Crash Info: {result.crash_info}")
            lines.append("")

        # State summary
        lines.append("States Explored:")
        lines.append("-" * 60)
        visited_hashes = set()
        for i, state in enumerate(result.states):
            if state.state_hash not in visited_hashes:
                visited_hashes.add(state.state_hash)
                lines.append(f"  {i+1}. {state.activity} ({len(state.elements)} elements)")

        lines.append("")

        # Actions summary
        lines.append("Actions Performed:")
        lines.append("-" * 60)
        action_counts = {}
        for action in result.actions:
            action_type = action.action_type.value
            action_counts[action_type] = action_counts.get(action_type, 0) + 1

        for action_type, count in sorted(action_counts.items()):
            lines.append(f"  {action_type}: {count}")

        lines.append("")
        lines.append("=" * 60)

        return "\n".join(lines)

    def save_text_report(self, result: ExplorationResult, output_path: str) -> bool:
        """
        Save text report to file

        Args:
            result: Exploration result
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            ensure_dir(os.path.dirname(output_path))
            report = self.generate_text_report(result)

            with open(output_path, 'w') as f:
                f.write(report)

            logger.info(f"Report saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save report: {e}")
            return False

    def save_json_report(self, result: ExplorationResult, output_path: str) -> bool:
        """
        Save JSON report to file

        Args:
            result: Exploration result
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            import os
            ensure_dir(os.path.dirname(output_path))

            # Calculate timestamps for each state based on start_time
            state_duration_per_step = result.duration / max(len(result.states), 1)

            report_data = {
                "start_time": result.start_time.isoformat(),
                "end_time": result.end_time.isoformat() if result.end_time else None,
                "duration_seconds": result.duration,
                "total_events": result.total_events,
                "unique_states": result.unique_states,
                "total_states": len(result.states),
                "crash_detected": result.crash_detected,
                "crash_info": result.crash_info,
                "states": [
                    {
                        "step": i,
                        "timestamp": (result.start_time.timestamp() + i * state_duration_per_step),
                        "datetime": datetime.fromtimestamp(result.start_time.timestamp() + i * state_duration_per_step).isoformat(),
                        "activity": state.activity,
                        "element_count": len(state.elements),
                        "state_hash": state.state_hash,
                        "screenshot": state.screenshot_path,
                        "screenshot_url": self._get_screenshot_url(output_path, state.screenshot_path, i)
                    }
                    for i, state in enumerate(result.states)
                ],
                "actions": [
                    {
                        "step": i,
                        "timestamp": (result.start_time.timestamp() + i * state_duration_per_step),
                        "datetime": datetime.fromtimestamp(result.start_time.timestamp() + i * state_duration_per_step).isoformat(),
                        **action.to_dict(),  # Spread operator to merge detailed action data
                        "repr": repr(action)  # Keep repr for backward compatibility
                    }
                    for i, action in enumerate(result.actions)
                ]
            }

            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2)

            # Verify file was actually written
            if not os.path.exists(output_path):
                logger.error(f"CRITICAL: File write appeared successful but file does not exist: {output_path}")
                return False

            file_size = os.path.getsize(output_path)
            if file_size == 0:
                logger.error(f"CRITICAL: File was written but is empty: {output_path}")
                return False

            logger.info(f"✅ JSON report saved to {output_path} ({file_size} bytes)")

            # Auto-update index.json for Grafana
            try:
                self.update_index_json(output_path, result)
            except Exception as idx_error:
                logger.error(f"Failed to update index.json (report still saved): {idx_error}")
                import traceback
                traceback.print_exc()

            return True

        except Exception as e:
            logger.error(f"Failed to save JSON report: {e}")
            import traceback
            traceback.print_exc()
            return False

    def update_index_json(self, report_path: str, result: ExplorationResult) -> bool:
        """
        Update index.json with new test run entry for Grafana dashboard

        Args:
            report_path: Path to the report.json file
            result: Exploration result

        Returns:
            True if successful
        """
        try:
            import re

            # Extract report folder name from path
            # e.g., ./reports/ai_multi_test_run001/report.json -> ai_multi_test_run001
            match = re.search(r'reports/([^/]+)/', report_path)
            if not match:
                logger.warning(f"Could not extract report name from path: {report_path}")
                return False

            report_name = match.group(1)

            # Determine index.json path (reports/index.json)
            reports_dir = os.path.dirname(os.path.dirname(report_path))
            index_path = os.path.join(reports_dir, "index.json")

            # Load existing index or create new one
            if os.path.exists(index_path):
                with open(index_path, 'r') as f:
                    index_data = json.load(f)
            else:
                index_data = {
                    "total_tests": 0,
                    "last_updated": None,
                    "test_runs": []
                }

            # Check if this test run already exists
            existing_index = None
            for i, test_run in enumerate(index_data["test_runs"]):
                if test_run.get("id") == report_name:
                    existing_index = i
                    break

            # Get device info (package name from result if available)
            package_name = getattr(result, 'package', 'unknown')
            device_name = getattr(result, 'device_name', 'Unknown Device')

            # Create new entry
            new_entry = {
                "id": report_name,
                "name": f"SmartMonkey Test - {report_name}",
                "package": package_name,
                "device": device_name,
                "start_time": result.start_time.isoformat(),
                "duration_seconds": result.duration,
                "total_steps": result.total_events,
                "unique_states": result.unique_states,
                "crash_detected": result.crash_detected,
                "status": "failed" if result.crash_detected else "passed",
                "report_url": f"{self.base_url}/{report_name}/report.json",
                "thumbnail": f"{self.base_url}/{report_name}/screenshots/screenshot_0000.png" if result.states else None
            }

            # Update or append
            if existing_index is not None:
                index_data["test_runs"][existing_index] = new_entry
                logger.info(f"Updated existing entry in index.json: {report_name}")
            else:
                index_data["test_runs"].append(new_entry)
                index_data["total_tests"] += 1
                logger.info(f"Added new entry to index.json: {report_name}")

            # Update timestamp
            index_data["last_updated"] = datetime.now().isoformat()

            # Save updated index
            ensure_dir(reports_dir)
            with open(index_path, 'w') as f:
                json.dump(index_data, f, indent=2)

            logger.info(f"✅ index.json updated: {index_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to update index.json: {e}")
            import traceback
            traceback.print_exc()
            return False

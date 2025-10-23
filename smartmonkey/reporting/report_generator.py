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

    def __init__(self):
        pass

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
                        "activity": state.activity,
                        "element_count": len(state.elements),
                        "state_hash": state.state_hash,
                        "screenshot": state.screenshot_path
                    }
                    for state in result.states
                ],
                "actions": [
                    {
                        "type": action.action_type.value,
                        "repr": repr(action)
                    }
                    for action in result.actions
                ]
            }

            with open(output_path, 'w') as f:
                json.dump(report_data, f, indent=2)

            logger.info(f"JSON report saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save JSON report: {e}")
            return False

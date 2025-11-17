"""
MCP Tool Handlers for SmartMonkey

Implements the actual logic for each MCP tool.
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import threading

# Add smartmonkey to path if not already
smartmonkey_root = Path(__file__).parent.parent.parent
if str(smartmonkey_root) not in sys.path:
    sys.path.insert(0, str(smartmonkey_root))

from smartmonkey.device.adb_manager import ADBManager
from smartmonkey.device.device import Device


class TestRunner:
    """Handles background test execution"""

    def __init__(self):
        self.running_tests: Dict[str, Dict[str, Any]] = {}

    def start_test(self, test_id: str, test_func, *args, **kwargs):
        """Start a test in background thread"""
        self.running_tests[test_id] = {
            "status": "running",
            "start_time": datetime.now().isoformat(),
            "output_dir": kwargs.get("output_dir")
        }

        thread = threading.Thread(
            target=self._run_test,
            args=(test_id, test_func, args, kwargs)
        )
        thread.daemon = True
        thread.start()

    def _run_test(self, test_id: str, test_func, args, kwargs):
        """Run test and update status"""
        try:
            result = test_func(*args, **kwargs)
            self.running_tests[test_id].update({
                "status": "completed",
                "end_time": datetime.now().isoformat(),
                "result": result
            })
        except Exception as e:
            self.running_tests[test_id].update({
                "status": "failed",
                "end_time": datetime.now().isoformat(),
                "error": str(e)
            })


# Global test runner
test_runner = TestRunner()


async def handle_list_devices(arguments: Dict[str, Any]) -> List[Dict[str, str]]:
    """List all connected Android devices"""
    try:
        adb = ADBManager()
        devices = adb.get_devices()

        if not devices:
            return [{
                "message": "No devices connected",
                "devices": []
            }]

        result = []
        for device_serial in devices:
            device = Device(device_serial)
            device.connect()
            model = device.adb.shell("getprop ro.product.model").strip()
            result.append({
                "serial": device_serial,
                "model": model,
                "status": "connected"
            })

        return result

    except Exception as e:
        return [{
            "error": f"Failed to list devices: {str(e)}"
        }]


async def handle_run_ai_test(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Run AI-driven test"""
    try:
        # Generate test ID
        test_id = f"ai_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"

        # Prepare output directory
        output_dir = Path("./reports") / test_id
        output_dir.mkdir(parents=True, exist_ok=True)

        # Extract parameters
        device_serial = arguments.get("device")
        package = arguments.get("package")
        url = arguments.get("url")
        mission = arguments["mission"]
        steps = arguments.get("steps", 5)

        # Validate: must have package or url
        if not package and not url:
            return {
                "error": "Must provide either 'package' (for app) or 'url' (for web)"
            }

        # Build command
        cmd_parts = [
            sys.executable, "-m", "smartmonkey.cli.main", "ai"
        ]

        if device_serial:
            cmd_parts.extend(["-d", device_serial])

        if package:
            cmd_parts.extend(["-pkg", package])
        elif url:
            cmd_parts.extend(["-u", url])

        cmd_parts.extend([
            "-m", mission,
            "-s", str(steps),
            "-o", str(output_dir)
        ])

        # Start test in background
        def run_test():
            import subprocess
            env = os.environ.copy()
            env["PYTHONPATH"] = str(smartmonkey_root)
            return subprocess.run(
                cmd_parts,
                env=env,
                capture_output=True,
                text=True
            )

        test_runner.start_test(test_id, run_test, output_dir=str(output_dir))

        return {
            "test_id": test_id,
            "status": "started",
            "type": "ai",
            "mode": "app" if package else "web",
            "target": package or url,
            "mission": mission,
            "steps": steps,
            "output_dir": str(output_dir),
            "message": f"AI test started. Test ID: {test_id}. "
                      f"Results will be saved to {output_dir}"
        }

    except Exception as e:
        return {
            "error": f"Failed to start AI test: {str(e)}"
        }


async def handle_run_mobile_test(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Run traditional mobile app test"""
    try:
        test_id = f"mobile_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        output_dir = Path("./reports") / test_id
        output_dir.mkdir(parents=True, exist_ok=True)

        device_serial = arguments.get("device")
        package = arguments["package"]
        steps = arguments.get("steps", 50)

        cmd_parts = [
            sys.executable, "-m", "smartmonkey.cli.main", "mobile"
        ]

        if device_serial:
            cmd_parts.extend(["-d", device_serial])

        cmd_parts.extend([
            "-p", package,
            "-s", str(steps),
            "-o", str(output_dir)
        ])

        def run_test():
            import subprocess
            env = os.environ.copy()
            env["PYTHONPATH"] = str(smartmonkey_root)
            return subprocess.run(
                cmd_parts,
                env=env,
                capture_output=True,
                text=True
            )

        test_runner.start_test(test_id, run_test, output_dir=str(output_dir))

        return {
            "test_id": test_id,
            "status": "started",
            "type": "mobile",
            "package": package,
            "steps": steps,
            "output_dir": str(output_dir),
            "message": f"Mobile test started. Test ID: {test_id}. "
                      f"Results will be saved to {output_dir}"
        }

    except Exception as e:
        return {
            "error": f"Failed to start mobile test: {str(e)}"
        }


async def handle_run_web_test(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Run web app test"""
    try:
        test_id = f"web_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:8]}"
        output_dir = Path("./reports") / test_id
        output_dir.mkdir(parents=True, exist_ok=True)

        device_serial = arguments.get("device")
        url = arguments["url"]
        steps = arguments.get("steps", 10)

        cmd_parts = [
            sys.executable, "-m", "smartmonkey.cli.main", "web"
        ]

        if device_serial:
            cmd_parts.extend(["-d", device_serial])

        cmd_parts.extend([
            "-u", url,
            "-s", str(steps),
            "-o", str(output_dir)
        ])

        def run_test():
            import subprocess
            env = os.environ.copy()
            env["PYTHONPATH"] = str(smartmonkey_root)
            return subprocess.run(
                cmd_parts,
                env=env,
                capture_output=True,
                text=True
            )

        test_runner.start_test(test_id, run_test, output_dir=str(output_dir))

        return {
            "test_id": test_id,
            "status": "started",
            "type": "web",
            "url": url,
            "steps": steps,
            "output_dir": str(output_dir),
            "message": f"Web test started. Test ID: {test_id}. "
                      f"Results will be saved to {output_dir}"
        }

    except Exception as e:
        return {
            "error": f"Failed to start web test: {str(e)}"
        }


# Tool handler registry
HANDLERS = {
    "list_devices": handle_list_devices,
    "run_ai_test": handle_run_ai_test,
    "run_mobile_test": handle_run_mobile_test,
    "run_web_test": handle_run_web_test,
}


async def handle_tool_call(name: str, arguments: Dict[str, Any]) -> Any:
    """Route tool calls to appropriate handlers"""
    handler = HANDLERS.get(name)

    if not handler:
        return {
            "error": f"Unknown tool: {name}"
        }

    try:
        return await handler(arguments)
    except Exception as e:
        return {
            "error": f"Tool execution failed: {str(e)}"
        }


# TODO: Implement these handlers
async def handle_get_results(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """TODO: Get test results and screenshots"""
    return {
        "error": "Not implemented yet. TODO: Implement get_results handler"
    }


async def handle_stop_test(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """TODO: Stop a running test"""
    return {
        "error": "Not implemented yet. TODO: Implement stop_test handler"
    }


async def handle_get_logs(arguments: Dict[str, Any]) -> Dict[str, Any]:
    """TODO: Get real-time logs"""
    return {
        "error": "Not implemented yet. TODO: Implement get_logs handler"
    }

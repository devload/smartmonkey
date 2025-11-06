"""
MCP Tool Definitions for SmartMonkey

Defines the available tools that can be called through the MCP protocol.
"""

TOOLS = [
    {
        "name": "list_devices",
        "description": "List all connected Android devices and emulators",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": []
        }
    },
    {
        "name": "run_ai_test",
        "description": "Run AI-driven testing with mission-oriented approach. "
                       "Supports both native Android apps and mobile web apps. "
                       "Provide either 'package' (for apps) or 'url' (for web).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "device": {
                    "type": "string",
                    "description": "Device serial number (optional, auto-detects if only one device)"
                },
                "package": {
                    "type": "string",
                    "description": "Android app package name (e.g., com.coupang.mobile)"
                },
                "url": {
                    "type": "string",
                    "description": "Mobile web URL (e.g., https://m.naver.com)"
                },
                "mission": {
                    "type": "string",
                    "description": "Testing mission in natural language (e.g., '쿠팡에서 상품 둘러보기')"
                },
                "steps": {
                    "type": "number",
                    "description": "Maximum number of test steps",
                    "default": 5
                }
            },
            "required": ["mission"]
        }
    },
    {
        "name": "run_mobile_test",
        "description": "Run traditional mobile app testing with weighted or random strategy",
        "inputSchema": {
            "type": "object",
            "properties": {
                "device": {
                    "type": "string",
                    "description": "Device serial number (optional)"
                },
                "package": {
                    "type": "string",
                    "description": "Android app package name"
                },
                "steps": {
                    "type": "number",
                    "description": "Maximum number of test steps",
                    "default": 50
                }
            },
            "required": ["package"]
        }
    },
    {
        "name": "run_web_test",
        "description": "Run web app testing using Chrome DevTools Protocol",
        "inputSchema": {
            "type": "object",
            "properties": {
                "device": {
                    "type": "string",
                    "description": "Device serial number (optional)"
                },
                "url": {
                    "type": "string",
                    "description": "Starting URL to test"
                },
                "steps": {
                    "type": "number",
                    "description": "Maximum number of test actions",
                    "default": 10
                }
            },
            "required": ["url"]
        }
    }
]

# TODO: Additional tools to implement
TODO_TOOLS = [
    {
        "name": "get_results",
        "description": "Get test results and screenshots for a completed test",
        "inputSchema": {
            "type": "object",
            "properties": {
                "test_id": {
                    "type": "string",
                    "description": "Test ID returned from run_* commands"
                }
            },
            "required": ["test_id"]
        }
    },
    {
        "name": "stop_test",
        "description": "Stop a running test",
        "inputSchema": {
            "type": "object",
            "properties": {
                "test_id": {
                    "type": "string",
                    "description": "Test ID to stop"
                }
            },
            "required": ["test_id"]
        }
    },
    {
        "name": "get_logs",
        "description": "Get real-time logs for a running or completed test",
        "inputSchema": {
            "type": "object",
            "properties": {
                "test_id": {
                    "type": "string",
                    "description": "Test ID"
                }
            },
            "required": ["test_id"]
        }
    }
]

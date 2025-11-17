# SmartMonkey MCP Server Setup Guide

## 🎯 Overview

SmartMonkey now supports **Model Context Protocol (MCP)**, allowing Claude Desktop and other MCP clients to directly control Android app testing!

### What You Can Do

- **"List my connected devices"** → Claude shows all Android devices
- **"Test Coupang app with mission: browse products"** → Claude runs AI test
- **"Run traditional test on com.example.app"** → Claude runs mobile test
- **"Test https://m.naver.com"** → Claude tests mobile web

---

## 🚀 Quick Setup

### 1. Install Dependencies

```bash
# Install MCP SDK
pip install 'mcp>=0.9.0'

# Or reinstall smartmonkey with latest dependencies
cd /path/to/smartmonkey
pip install -e .
```

### 2. Configure Claude Desktop

**macOS:**
```bash
# Edit Claude Desktop config
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json
```

**Add SmartMonkey server:**
```json
{
  "mcpServers": {
    "smartmonkey": {
      "command": "python3",
      "args": [
        "-m",
        "smartmonkey.mcp.server"
      ],
      "env": {
        "PYTHONPATH": "/Users/devload/smartMonkey"
      }
    }
  }
}
```

**⚠️ Important:** Change `/Users/devload/smartMonkey` to your actual smartmonkey path!

### 3. Restart Claude Desktop

```bash
# Quit Claude Desktop completely
# Then restart it
```

### 4. Verify Installation

Open Claude Desktop and ask:
```
"What SmartMonkey tools do you have access to?"
```

Claude should respond with the available tools:
- `list_devices`
- `run_ai_test`
- `run_mobile_test`
- `run_web_test`

---

## 🛠️ Available Tools

### 1. list_devices

**Description:** List all connected Android devices

**Example:**
```
User: "Show me connected Android devices"
Claude: [Calls list_devices]
        "You have 3 devices connected:
         1. Samsung SM-A356N (RFCX919P8ZF)
         2. VIVO V2041 (3062821163005VC)
         3. Android Emulator (emulator-5554)"
```

---

### 2. run_ai_test

**Description:** Run AI-driven testing with mission

**Parameters:**
- `mission` (required): Testing goal in natural language
- `package` (optional): Android app package name
- `url` (optional): Mobile web URL
- `device` (optional): Device serial
- `steps` (optional): Max steps (default: 5)

**Examples:**

**Test Android App:**
```
User: "Test Coupang app, mission: browse products and add to cart"
Claude: [Calls run_ai_test with package="com.coupang.mobile",
         mission="browse products and add to cart"]
```

**Test Mobile Web:**
```
User: "Test Naver mobile site, mission: read news articles"
Claude: [Calls run_ai_test with url="https://m.naver.com",
         mission="read news articles"]
```

---

### 3. run_mobile_test

**Description:** Run traditional mobile app testing

**Parameters:**
- `package` (required): Android app package name
- `device` (optional): Device serial
- `steps` (optional): Max steps (default: 50)

**Example:**
```
User: "Run traditional test on com.android.settings for 20 steps"
Claude: [Calls run_mobile_test]
```

---

### 4. run_web_test

**Description:** Run web app testing using Chrome DevTools

**Parameters:**
- `url` (required): Starting URL
- `device` (optional): Device serial
- `steps` (optional): Max steps (default: 10)

**Example:**
```
User: "Test https://m.shopping.naver.com for 15 steps"
Claude: [Calls run_web_test]
```

---

## 📊 Test Results

All tests return a `test_id` and `output_dir`:

```json
{
  "test_id": "ai_test_20251103_123456_abc123",
  "status": "started",
  "output_dir": "./reports/ai_test_20251103_123456_abc123"
}
```

**Find your results:**
```bash
cd ./reports/ai_test_20251103_123456_abc123/
ls
# Output:
# - screenshots/
# - report.json
# - report.txt
# - claude.md
```

---

## 🔮 Coming Soon (TODO)

### Additional Tools (Not Yet Implemented)

**get_results**
- Get test results and screenshots
- View test summary

**stop_test**
- Stop a running test
- Gracefully terminate

**get_logs**
- Real-time log streaming
- Progress monitoring

**Progress Reporting**
- WebSocket-based progress updates
- Real-time status in Claude

---

## 🧪 Testing Your Setup

### Test 1: List Devices
```
User: "SmartMonkey, list my devices"
Expected: List of connected Android devices
```

### Test 2: AI Test
```
User: "Run AI test on Coupang app, mission: 쿠팡에서 상품 둘러보기, 10 steps"
Expected: Test starts and returns test_id
```

### Test 3: Check Results
```bash
# After test completes, check output directory
cd ./reports/<test_id>/
cat report.txt
open screenshots/
```

---

## 🐛 Troubleshooting

### Issue: "SmartMonkey tools not available"

**Solution:**
1. Check Claude Desktop config path:
   ```bash
   cat ~/Library/Application\ Support/Claude/claude_desktop_config.json
   ```

2. Verify PYTHONPATH is correct:
   ```bash
   echo $PYTHONPATH
   # Should include /path/to/smartmonkey
   ```

3. Test server manually:
   ```bash
   python3 -m smartmonkey.mcp.server
   # Should start without errors
   ```

4. Restart Claude Desktop completely

---

### Issue: "Device not found"

**Solution:**
1. Check ADB connection:
   ```bash
   adb devices
   ```

2. If device not listed, reconnect:
   ```bash
   adb kill-server
   adb start-server
   adb devices
   ```

---

### Issue: "Permission denied"

**Solution:**
1. Check Android device authorization:
   - USB debugging enabled?
   - "Allow" prompt accepted?

2. Verify ADB permissions:
   ```bash
   adb shell whoami
   # Should return "shell"
   ```

---

## 📚 Example Conversations

### Example 1: Quick Device Check
```
User: "What Android devices do I have?"
Claude: [Calls list_devices] "You have 2 devices:
        - Samsung SM-A356N
        - VIVO V2041"

User: "Use Samsung to test Coupang"
Claude: [Calls run_ai_test with device="RFCX919P8ZF"]
        "Starting AI test on Samsung..."
```

### Example 2: Web Testing
```
User: "Test Naver mobile site for 5 steps"
Claude: [Calls run_web_test]
        "Web test started: test_web_20251103_..."

User: "Where are the results?"
Claude: "Results saved to: ./reports/test_web_20251103_.../
        - 5 screenshots captured
        - Test report available"
```

### Example 3: AI-Driven Testing
```
User: "I want to test if users can find and buy products on Coupang"
Claude: "I'll run an AI test with that mission."
        [Calls run_ai_test with mission="find and buy products"]
        "Test started! Mission: Find and buy products
         Device: Samsung SM-A356N
         Steps: 10"
```

---

## 🎯 Best Practices

1. **Always check device connection first:**
   ```
   "List devices before starting test"
   ```

2. **Be specific with missions:**
   ```
   ✅ "Browse products, add to cart, and checkout"
   ❌ "Test the app"
   ```

3. **Use appropriate step counts:**
   - Quick smoke test: 5-10 steps
   - Thorough exploration: 20-50 steps
   - Full regression: 100+ steps

4. **Check results after completion:**
   ```bash
   cd ./reports/<test_id>/
   cat report.txt
   ```

---

## 📖 Additional Resources

- [SmartMonkey README](../README.md)
- [MCP Protocol Docs](https://modelcontextprotocol.io)
- [Claude Desktop](https://claude.ai/download)

---

## 🤝 Contributing

Want to add more MCP tools? Check the TODO items in:
- `smartmonkey/mcp/tools.py` - Add tool definitions
- `smartmonkey/mcp/handlers.py` - Implement handlers

Pull requests welcome! 🚀

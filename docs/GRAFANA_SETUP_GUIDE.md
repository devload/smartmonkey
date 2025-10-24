# 📊 SmartMonkey Grafana Dashboard Setup Guide

Complete guide to setting up Grafana dashboards for visualizing SmartMonkey test results.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Grafana Installation](#grafana-installation)
3. [Required Plugins](#required-plugins)
4. [Data Source Configuration](#data-source-configuration)
5. [Dashboard Import](#dashboard-import)
6. [Usage](#usage)
7. [Screenshots](#screenshots)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

- SmartMonkey installed and working
- Test results generated in `./reports/` directory
- Terminal access
- Web browser

---

## Grafana Installation

### macOS (Homebrew)

```bash
# Install Grafana
brew install grafana

# Start Grafana service
brew services start grafana

# Verify installation
brew services list | grep grafana
# Should show: grafana started
```

**Access Grafana**: Open http://localhost:3000 in your browser

**Default credentials**:
- Username: `admin`
- Password: `admin`
- You'll be prompted to change the password on first login (you can skip this)

### Linux (Ubuntu/Debian)

```bash
# Add Grafana repository
sudo apt-get install -y adduser libfontconfig1
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
echo "deb https://packages.grafana.com/oss/deb stable main" | sudo tee /etc/apt/sources.list.d/grafana.list

# Install Grafana
sudo apt-get update
sudo apt-get install grafana

# Start Grafana service
sudo systemctl start grafana-server
sudo systemctl enable grafana-server

# Check status
sudo systemctl status grafana-server
```

**Access Grafana**: Open http://localhost:3000 in your browser

### Linux (CentOS/RHEL)

```bash
# Add Grafana repository
cat <<EOF | sudo tee /etc/yum.repos.d/grafana.repo
[grafana]
name=grafana
baseurl=https://packages.grafana.com/oss/rpm
repo_gpgcheck=1
enabled=1
gpgcheck=1
gpgkey=https://packages.grafana.com/gpg.key
sslverify=1
sslcacert=/etc/pki/tls/certs/ca-bundle.crt
EOF

# Install Grafana
sudo yum install grafana

# Start Grafana service
sudo systemctl start grafana-server
sudo systemctl enable grafana-server
```

---

## Required Plugins

SmartMonkey dashboards require two plugins:

### 1. Infinity Data Source (v2.9.0+)

This plugin allows Grafana to load data from JSON files via HTTP.

**Installation via Grafana UI**:

1. Go to **Configuration** (⚙️ icon) → **Plugins**
2. Search for `Infinity`
3. Click **Infinity** data source plugin
4. Click **Install**

**Installation via CLI**:

```bash
# Install plugin
grafana-cli plugins install yesoreyeram-infinity-datasource

# Restart Grafana
# macOS:
brew services restart grafana

# Linux:
sudo systemctl restart grafana-server
```

**Verify installation**:
1. Go to **Configuration** → **Plugins**
2. Click **Installed** tab
3. You should see **Infinity** in the list

### 2. HTML Graphics Panel (v2.2.1+)

This plugin renders the screenshot gallery with custom HTML/JavaScript.

**Installation via Grafana UI**:

1. Go to **Configuration** (⚙️ icon) → **Plugins**
2. Search for `HTML Graphics`
3. Click **HTML Graphics** (by gapit)
4. Click **Install**

**Installation via CLI**:

```bash
# Install plugin
grafana-cli plugins install gapit-htmlgraphics-panel

# Restart Grafana
# macOS:
brew services restart grafana

# Linux:
sudo systemctl restart grafana-server
```

**Verify installation**:
1. Go to **Configuration** → **Plugins**
2. Click **Installed** tab
3. You should see **HTML Graphics** in the list

---

## Data Source Configuration

### Step 1: Start HTTP Server

Grafana needs to access your test reports via HTTP. Start a simple HTTP server:

```bash
# Navigate to reports directory
cd /Users/devload/smartMonkey/reports

# Start Python HTTP server on port 8000
python3 -m http.server 8000
```

**Leave this terminal running!** Grafana will fetch data from http://localhost:8000

**Verify it's working**:
- Open http://localhost:8000 in your browser
- You should see your reports directory listing
- Click on `index.json` to verify the file loads

### Step 2: Create Infinity Data Source

1. In Grafana, go to **Connections** → **Data sources**
2. Click **Add data source**
3. Search for and select **Infinity**
4. Configure:
   - **Name**: `SmartMonkey Reports` (or any name you prefer)
   - Leave other settings as default
5. Click **Save & Test**
   - You should see "Data source is working" message

**Note**: The Infinity data source doesn't need a base URL - we'll specify full URLs in each dashboard panel.

---

## Dashboard Import

SmartMonkey provides two pre-configured dashboards:

### Dashboard 1: Test Runs Overview (Main)

This dashboard shows a list of all test runs with drill-down capability.

**Import steps**:

1. In Grafana, click **Dashboards** (📊 icon) → **Import**
2. Click **Upload JSON file**
3. Select `/Users/devload/smartMonkey/grafana/dashboard-main.json`
4. On the import screen:
   - **Name**: Keep as "SmartMonkey - Test Runs" or customize
   - **Folder**: Select a folder or use "General"
   - **Unique identifier (UID)**: Keep as `smartmonkey-main`
   - **Infinity Data Source**: Select the data source you created
5. Click **Import**

**What you'll see**:
- Total test count statistic
- Table listing all test runs with:
  - Test ID (clickable link to detail view)
  - Test name
  - Package name
  - Device
  - Start time
  - Duration
  - Number of steps
  - Crash status (Yes/No with color coding)
  - Overall status (Passed/Failed with color coding)

### Dashboard 2: Test Detail View

This dashboard shows detailed results for a single test run, including screenshot gallery.

**Import steps**:

1. In Grafana, click **Dashboards** → **Import**
2. Click **Upload JSON file**
3. Select `/Users/devload/smartMonkey/grafana/dashboard-detail.json`
4. On the import screen:
   - **Name**: Keep as "SmartMonkey Test Detail" or customize
   - **Folder**: Select the same folder as the main dashboard
   - **Unique identifier (UID)**: Keep as `smartmonkey-detail`
   - **Infinity Data Source**: Select the data source you created
5. Click **Import**

**What you'll see**:
- Test summary (duration, states, crash status)
- Screenshot gallery (scrollable horizontal gallery)
- Test details table (activity, element count, step, timestamp)
- "Back to Test List" link in the top-left

---

## Usage

### Running Tests

First, generate some test results:

```bash
cd /Users/devload/smartMonkey

export PYTHONPATH=$(pwd):$PYTHONPATH

# Run a single test
python3 -m smartmonkey.cli.main run \
  --device emulator-5556 \
  --package io.whatap.session.sample \
  --steps 20 \
  --output ./reports/test_run_001

# Run multiple tests (recommended for dashboard demo)
for i in {1..5}; do
  python3 -m smartmonkey.cli.main run \
    --device emulator-5556 \
    --package io.whatap.session.sample \
    --steps 20 \
    --strategy weighted \
    --output ./reports/test_run_$(printf "%03d" $i)
  sleep 2
done
```

### Viewing Results

1. **Ensure HTTP server is running**:
   ```bash
   cd /Users/devload/smartMonkey/reports
   python3 -m http.server 8000
   ```

2. **Open main dashboard**:
   - Go to **Dashboards** → **SmartMonkey - Test Runs**
   - You'll see a list of all test runs
   - The dashboard auto-refreshes every 30 seconds

3. **View test details**:
   - Click on any **Test ID** in the table
   - You'll be taken to the detail dashboard
   - See the screenshot gallery and detailed metrics
   - Click **⬅️ Back to Test List** to return

### Dashboard Features

**Main Dashboard**:
- ✅ Auto-refresh every 30 seconds
- ✅ Sortable columns (click column headers)
- ✅ Color-coded status (green = passed, red = failed)
- ✅ Clickable Test IDs for drill-down
- ✅ Crash detection indicator

**Detail Dashboard**:
- ✅ Test summary statistics
- ✅ Horizontal scrolling screenshot gallery
- ✅ Activity names and step numbers
- ✅ Detailed test timeline table
- ✅ Auto-retry for loading screenshots (5 attempts)

---

## Screenshots

### Main Dashboard - Test Runs Overview

![Main Dashboard](images/grafana-main-dashboard.png)

**Features shown**:
- Total test count at the top
- List of all test runs
- Status indicators (Passed/Failed)
- Crash detection column
- Clickable Test ID links

### Detail Dashboard - Test Results with Screenshot Gallery

![Detail Dashboard](images/grafana-detail-dashboard.png)

**Features shown**:
- Test summary statistics (duration, states, crash status)
- Horizontal screenshot gallery with thumbnails
- Activity names below each screenshot
- Detailed test timeline table
- Back button to return to main dashboard

---

## Troubleshooting

### Issue: "No data" in dashboards

**Possible causes**:
1. HTTP server not running
2. No test results generated yet
3. Incorrect data source URL

**Solutions**:

```bash
# 1. Check HTTP server is running
curl http://localhost:8000/index.json
# Should return JSON content

# 2. Verify test results exist
ls -la /Users/devload/smartMonkey/reports/
# Should show test_run_* directories

# 3. Check index.json was generated
cat /Users/devload/smartMonkey/reports/index.json
# Should show test runs array
```

### Issue: "Data source is not working"

**Solution**: Verify Infinity plugin is installed:

```bash
# Check installed plugins
ls /opt/homebrew/var/lib/grafana/plugins/  # macOS
ls /var/lib/grafana/plugins/              # Linux

# Should see yesoreyeram-infinity-datasource directory

# If not installed, install it:
grafana-cli plugins install yesoreyeram-infinity-datasource
brew services restart grafana  # macOS
```

### Issue: Screenshots not loading

**Possible causes**:
1. HTTP server not serving images
2. Browser cache
3. Data not ready when page loads

**Solutions**:

```bash
# 1. Verify screenshots are accessible
curl -I http://localhost:8000/test_run_001/screenshots/screenshot_0000.png
# Should return HTTP 200 OK

# 2. Clear browser cache
# Chrome: Cmd+Shift+R (macOS) or Ctrl+Shift+R (Windows/Linux)
# Firefox: Cmd+Shift+R (macOS) or Ctrl+Shift+R (Windows/Linux)

# 3. Refresh the dashboard
# Click the refresh button in Grafana (top-right)
```

The detail dashboard includes retry logic that attempts to load screenshots 5 times with 500ms delays, so it should eventually load even if data is slow to arrive.

### Issue: "Index 0 out of bounds" error in dashboard

**Cause**: Data source not configured properly in dashboard variables

**Solution**:
1. Go to dashboard settings (⚙️ icon in top-right)
2. Click **Variables** tab
3. Ensure `test_id` variable exists
4. Save the dashboard

### Issue: Links not working between dashboards

**Cause**: Dashboard UIDs don't match

**Solution**: Verify the dashboards have the correct UIDs:
- Main dashboard: `smartmonkey-main`
- Detail dashboard: `smartmonkey-detail`

Check in dashboard settings → **General** → **UID**

### Issue: CORS errors in browser console

**This shouldn't happen** because Infinity data source fetches data server-side, not from the browser.

If you see CORS errors:
1. Check that you're using the **Infinity** data source, not a JSON API or other plugin
2. Verify the HTTP server is running on localhost (not a remote host)

---

## Advanced Configuration

### Custom Auto-Refresh Interval

1. Open the dashboard
2. Click the time range selector (top-right)
3. In the **Refreshing every** dropdown, select your preferred interval:
   - 5s (very frequent)
   - 10s
   - 30s (default)
   - 1m
   - 5m

### Filtering Test Runs

You can add filter variables to the main dashboard:

1. Dashboard settings → **Variables** → **Add variable**
2. Configure:
   - **Name**: `device_filter`
   - **Type**: Query
   - **Data source**: SmartMonkey Reports
   - **Query**: Use Infinity query to get unique devices
3. Add filter to table panel query

### Exporting Dashboards

To share your configured dashboards:

1. Open the dashboard
2. Click the share icon (top-right)
3. Go to **Export** tab
4. Click **Save to file**
5. Share the JSON file with others

---

## Performance Tips

### For Large Numbers of Tests

If you have hundreds of test runs:

1. **Limit index.json size**: Modify `report_generator.py` to keep only the most recent N tests
2. **Use pagination**: Add pagination controls to the main dashboard table
3. **Archive old tests**: Move old test directories out of the reports folder

### For Large Screenshots

If screenshots are very large:

1. **Reduce screenshot quality**: Modify the screenshot capture quality in `device.py`
2. **Use thumbnails**: Generate smaller thumbnail versions for the gallery
3. **Lazy loading**: The current implementation already loads images on-demand

---

## Next Steps

Now that you have Grafana set up:

1. ✅ Run multiple tests to populate the dashboards
2. ✅ Customize dashboard layouts to your preference
3. ✅ Set up alerts for crash detection (Grafana feature)
4. ✅ Create custom panels for specific metrics
5. ✅ Share dashboards with your team

---

## Additional Resources

- **Grafana Documentation**: https://grafana.com/docs/grafana/latest/
- **Infinity Plugin Docs**: https://grafana.com/grafana/plugins/yesoreyeram-infinity-datasource/
- **HTML Graphics Plugin**: https://grafana.com/grafana/plugins/gapit-htmlgraphics-panel/
- **SmartMonkey Main README**: [../README.md](../README.md)

---

## Support

If you encounter issues not covered in this guide:

1. Check the SmartMonkey logs for errors
2. Check Grafana server logs:
   ```bash
   # macOS
   tail -f /opt/homebrew/var/log/grafana/grafana.log

   # Linux
   sudo journalctl -u grafana-server -f
   ```
3. Open an issue on the SmartMonkey GitHub repository

---

**Happy Testing! 🐵📊**

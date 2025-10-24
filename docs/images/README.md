# SmartMonkey Documentation Images

This directory contains screenshots and images used in the documentation.

## Required Screenshots

### Grafana Dashboards

1. **grafana-main-dashboard.png**
   - Screenshot of the main dashboard showing the test runs list
   - Should show multiple test runs with status indicators
   - Location referenced in: `../GRAFANA_SETUP_GUIDE.md`

2. **grafana-detail-dashboard.png**
   - Screenshot of the detail dashboard showing:
     - Test summary statistics
     - Screenshot gallery (scrollable horizontal view)
     - Test timeline table
   - Location referenced in: `../GRAFANA_SETUP_GUIDE.md` and `../README.md`

## How to Capture Screenshots

### Main Dashboard
1. Open http://localhost:3000
2. Navigate to "SmartMonkey - Test Runs" dashboard
3. Ensure you have at least 3-5 test runs visible
4. Take a screenshot showing:
   - The full dashboard
   - Test runs table with clickable Test IDs
   - Status column with Passed/Failed indicators
   - Crash detection column
5. Save as `grafana-main-dashboard.png`

### Detail Dashboard
1. Click on any Test ID from the main dashboard
2. Wait for screenshots to load in the gallery
3. Take a screenshot showing:
   - Test summary at the top
   - Screenshot gallery (showing at least 3-4 screenshots)
   - Test details table at the bottom
4. Save as `grafana-detail-dashboard.png`

## Image Specifications

- **Format**: PNG (preferred) or JPG
- **Recommended width**: 1200-1600px
- **Quality**: High (for clear readability of UI elements)
- **Compression**: Optimize for web (use tools like ImageOptim or TinyPNG)

## Current Status

- [ ] grafana-main-dashboard.png
- [ ] grafana-detail-dashboard.png

Once screenshots are added, they will automatically appear in:
- `README.md` (lines 60, 64)
- `GRAFANA_SETUP_GUIDE.md` (lines 320, 328)

"""HTML report generator with screenshot timeline"""

import os
from datetime import datetime
from ..exploration.exploration_engine import ExplorationResult
from ..utils.logger import get_logger
from ..utils.helpers import ensure_dir

logger = get_logger(__name__)


class HTMLReporter:
    """Generate beautiful HTML reports with screenshot timeline"""

    def generate_html_report(self, result: ExplorationResult, output_path: str) -> bool:
        """
        Generate HTML report with screenshot timeline

        Args:
            result: Exploration result
            output_path: Output HTML file path

        Returns:
            True if successful
        """
        try:
            ensure_dir(os.path.dirname(output_path))

            # HTML template
            html = f"""<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartMonkey Test Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 15px;
        }}
        
        .logo {{
            font-size: 1.2em;
        }}
        
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            padding: 30px 40px;
            background: #f8f9fa;
        }}
        
        .stat {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
        }}
        
        .stat-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
            margin-bottom: 5px;
        }}
        
        .stat-label {{
            color: #666;
            font-size: 0.9em;
        }}
        
        .crash-alert {{
            background: #fff5f5;
            border-left: 4px solid #e53e3e;
            padding: 20px;
            margin: 20px 40px;
            border-radius: 5px;
        }}
        
        .crash-alert h3 {{
            color: #e53e3e;
            margin-bottom: 10px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .timeline {{
            padding: 40px;
        }}
        
        .timeline-title {{
            font-size: 1.8em;
            margin-bottom: 30px;
            color: #333;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        
        .timeline-container {{
            position: relative;
        }}
        
        .timeline-line {{
            position: absolute;
            left: 30px;
            top: 0;
            bottom: 0;
            width: 4px;
            background: linear-gradient(to bottom, #667eea, #764ba2);
        }}
        
        .step {{
            position: relative;
            margin-bottom: 40px;
            margin-left: 70px;
            background: white;
            border-radius: 15px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
            overflow: hidden;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .step:hover {{
            transform: translateY(-5px);
            box-shadow: 0 8px 30px rgba(0,0,0,0.15);
        }}
        
        .step-number {{
            position: absolute;
            left: -70px;
            top: 20px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2em;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            z-index: 1;
        }}
        
        .step-content {{
            padding: 20px;
        }}
        
        .step-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
            padding-bottom: 15px;
            border-bottom: 2px solid #f0f0f0;
        }}
        
        .step-activity {{
            font-size: 1.3em;
            font-weight: bold;
            color: #333;
        }}
        
        .step-meta {{
            display: flex;
            gap: 15px;
            font-size: 0.9em;
            color: #666;
        }}
        
        .screenshot-container {{
            margin-top: 15px;
            position: relative;
        }}
        
        .screenshot {{
            width: 100%;
            max-width: 400px;
            border-radius: 10px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            cursor: pointer;
            transition: transform 0.3s ease;
        }}
        
        .screenshot:hover {{
            transform: scale(1.05);
        }}
        
        .lightbox {{
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0,0,0,0.9);
            z-index: 1000;
            justify-content: center;
            align-items: center;
        }}
        
        .lightbox.active {{
            display: flex;
        }}
        
        .lightbox img {{
            max-width: 90%;
            max-height: 90vh;
            border-radius: 10px;
        }}
        
        .lightbox-close {{
            position: absolute;
            top: 20px;
            right: 40px;
            color: white;
            font-size: 3em;
            cursor: pointer;
            z-index: 1001;
        }}
        
        .footer {{
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>
                <span class="logo">🐵🧠</span>
                SmartMonkey Test Report
            </h1>
            <p>Intelligent Android App Testing</p>
        </div>

        <!-- Summary -->
        <div class="summary">
            <div class="stat">
                <div class="stat-value">{result.duration:.1f}s</div>
                <div class="stat-label">Duration</div>
            </div>
            <div class="stat">
                <div class="stat-value">{len(result.states)}</div>
                <div class="stat-label">Total Steps</div>
            </div>
            <div class="stat">
                <div class="stat-value">{result.unique_states}</div>
                <div class="stat-label">Unique States</div>
            </div>
            <div class="stat">
                <div class="stat-value">{result.total_events}</div>
                <div class="stat-label">Actions</div>
            </div>
        </div>

        <!-- Crash Alert -->
        {self._generate_crash_alert(result)}

        <!-- Timeline -->
        <div class="timeline">
            <h2 class="timeline-title">📸 Test Flow Timeline</h2>
            <div class="timeline-container">
                <div class="timeline-line"></div>
                {self._generate_timeline(result)}
            </div>
        </div>

        <!-- Footer -->
        <div class="footer">
            <p>Generated by SmartMonkey v1.0.0 • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <p>🤖 Powered by Claude Code</p>
        </div>
    </div>

    <!-- Lightbox -->
    <div class="lightbox" id="lightbox">
        <span class="lightbox-close" onclick="closeLightbox()">&times;</span>
        <img id="lightbox-img" src="" alt="Screenshot">
    </div>

    <script>
        function openLightbox(src) {{
            document.getElementById('lightbox').classList.add('active');
            document.getElementById('lightbox-img').src = src;
        }}

        function closeLightbox() {{
            document.getElementById('lightbox').classList.remove('active');
        }}

        // Close on click outside
        document.getElementById('lightbox').addEventListener('click', function(e) {{
            if (e.target === this) {{
                closeLightbox();
            }}
        }});

        // Close on ESC key
        document.addEventListener('keydown', function(e) {{
            if (e.key === 'Escape') {{
                closeLightbox();
            }}
        }});
    </script>
</body>
</html>
"""

            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)

            logger.info(f"HTML report saved to {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to save HTML report: {e}")
            return False

    def _generate_crash_alert(self, result: ExplorationResult) -> str:
        """Generate crash alert HTML"""
        if not result.crash_detected:
            return ""

        return f"""
        <div class="crash-alert">
            <h3>🔴 Crash Detected!</h3>
            <p><strong>Info:</strong> {result.crash_info}</p>
        </div>
        """

    def _generate_timeline(self, result: ExplorationResult) -> str:
        """Generate timeline HTML"""
        timeline_html = ""

        for i, state in enumerate(result.states):
            # Screenshot path - relative to HTML file
            screenshot_rel = f"screenshots/screenshot_{i:04d}.png"

            timeline_html += f"""
            <div class="step">
                <div class="step-number">{i}</div>
                <div class="step-content">
                    <div class="step-header">
                        <div class="step-activity">{state.activity}</div>
                        <div class="step-meta">
                            <span>📱 {len(state.elements)} elements</span>
                        </div>
                    </div>
                    <div class="screenshot-container">
                        <img src="{screenshot_rel}" 
                             alt="Screenshot {i}" 
                             class="screenshot"
                             onclick="openLightbox('{screenshot_rel}')">
                    </div>
                </div>
            </div>
            """

        return timeline_html

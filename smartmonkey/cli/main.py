"""SmartMonkey CLI"""

import click
import sys
import json
from pathlib import Path
from ..device.device import Device
from ..device.adb_manager import ADBManager
from ..exploration.exploration_engine import ExplorationEngine
from ..exploration.strategies.random_strategy import RandomStrategy
from ..exploration.strategies.weighted_strategy import WeightedStrategy
from ..exploration.strategies.ai_strategy import AIStrategy
from ..reporting.report_generator import ReportGenerator
from ..utils.logger import setup_logger, get_logger
from ..utils.helpers import get_timestamp, ensure_dir

setup_logger()
logger = get_logger(__name__)


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """SmartMonkey - Intelligent Android App Testing Tool"""
    pass


@cli.command()
def list_devices():
    """List connected Android devices"""
    click.echo("Checking connected devices...")

    adb = ADBManager()
    devices = adb.get_devices()

    if not devices:
        click.echo("No devices found!")
        click.echo("\nMake sure:")
        click.echo("  1. Device is connected via USB")
        click.echo("  2. USB debugging is enabled")
        click.echo("  3. ADB is installed and in PATH")
        return

    click.echo(f"\nFound {len(devices)} device(s):\n")

    for i, serial in enumerate(devices, 1):
        device = Device(serial)
        if device.connect():
            click.echo(f"{i}. {serial}")
            click.echo(f"   Model: {device.model}")
            click.echo(f"   Android: {device.android_version}")
            click.echo(f"   Manufacturer: {device.manufacturer}")
            click.echo()


@cli.command()
@click.option('--device', '-d', help='Device serial number (optional if only one device)')
@click.option('--package', '-p', required=True, help='App package name')
@click.option('--steps', '-n', default=50, help='Maximum number of steps (default: 50)')
@click.option('--strategy', '-s', type=click.Choice(['random', 'weighted', 'ai']), default='weighted',
              help='Exploration strategy (default: weighted)')
@click.option('--output', '-o', help='Output directory (default: ./reports/<timestamp>)')
@click.option('--screenshots/--no-screenshots', default=True, help='Save screenshots (default: yes)')
@click.option('--runs', '-r', default=1, help='Number of test runs (default: 1)')
@click.option('--ai-goal', help='AI test goal (required for ai strategy)')
@click.option('--ai-workspace', default='./ai_workspace', help='AI workspace directory (default: ./ai_workspace)')
@click.option('--ai-credentials', help='Test credentials as JSON (e.g., {"email":"test@example.com"})')
@click.option('--ai-scenario', help='Predefined scenario type (login, checkout, settings)')
def run(device, package, steps, strategy, output, screenshots, runs, ai_goal, ai_workspace, ai_credentials, ai_scenario):
    """Run SmartMonkey exploration on an app"""

    click.echo("=" * 60)
    click.echo("SmartMonkey - Starting Exploration")
    click.echo("=" * 60)

    # Get device
    adb = ADBManager()
    devices = adb.get_devices()

    if not devices:
        click.echo("ERROR: No devices found!")
        sys.exit(1)

    if device:
        if device not in devices:
            click.echo(f"ERROR: Device {device} not found!")
            sys.exit(1)
        device_serial = device
    elif len(devices) == 1:
        device_serial = devices[0]
    else:
        click.echo("ERROR: Multiple devices found. Please specify device with --device")
        click.echo("\nAvailable devices:")
        for d in devices:
            click.echo(f"  - {d}")
        sys.exit(1)

    # Connect to device
    target_device = Device(device_serial)
    if not target_device.connect():
        click.echo(f"ERROR: Failed to connect to device {device_serial}")
        sys.exit(1)

    click.echo(f"\nDevice: {target_device.model} ({device_serial})")
    click.echo(f"Package: {package}")
    click.echo(f"Strategy: {strategy}")
    click.echo(f"Max Steps: {steps}")
    if runs > 1:
        click.echo(f"Test Runs: {runs}")
    click.echo()

    # Base output directory
    base_output = output if output else f"./reports/{get_timestamp()}"

    # Validate AI parameters if AI strategy
    if strategy == 'ai' and not ai_goal:
        click.echo("ERROR: --ai-goal is required when using ai strategy")
        click.echo("\nExample:")
        click.echo("  --strategy ai --ai-goal '로그인 테스트'")
        sys.exit(1)

    # Parse credentials for AI
    credentials = {}
    if ai_credentials:
        try:
            credentials = json.loads(ai_credentials)
        except json.JSONDecodeError:
            click.echo("ERROR: Invalid JSON for --ai-credentials")
            sys.exit(1)

    # Show AI mode info
    if strategy == 'ai':
        click.echo(f"🤖 AI Mode Activated")
        click.echo(f"   Goal: {ai_goal}")
        click.echo(f"   Workspace: {ai_workspace}")
        if ai_scenario:
            click.echo(f"   Scenario: {ai_scenario}")
        if credentials:
            click.echo(f"   Credentials: {list(credentials.keys())}")
        click.echo()

    # Run tests (loop for multiple runs)
    all_results = []

    for run_num in range(1, runs + 1):
        # Determine output directory for this run
        if runs > 1:
            run_output = f"{base_output}_run{run_num:03d}"
        else:
            run_output = base_output

        ensure_dir(run_output)
        screenshot_dir = f"{run_output}/screenshots" if screenshots else None

        # Print run header
        if runs > 1:
            click.echo()
            click.echo("=" * 60)
            click.echo(f"🔄 Test Run {run_num}/{runs}")
            click.echo("=" * 60)

        # Restart app for fresh test (especially important for multiple runs)
        if run_num > 1 or runs > 1:
            from ..device.app_manager import AppManager
            app_mgr = AppManager(target_device)

            click.echo(f"🔄 Restarting app for fresh test state...")
            app_mgr.stop_app(package)
            import time
            time.sleep(1)
            app_mgr.launch_app(package)
            time.sleep(2)
            click.echo(f"✅ App restarted")
            click.echo()

        click.echo(f"Output directory: {run_output}")
        if screenshots:
            click.echo(f"Screenshots: {screenshot_dir}")
        click.echo()

        # Select strategy for this run
        if strategy == 'random':
            exploration_strategy = RandomStrategy()
        elif strategy == 'ai':
            # Create test config
            test_config = {
                "scenario_type": ai_scenario or "custom",
                "credentials": credentials
            }

            # Create AI strategy
            exploration_strategy = AIStrategy(
                workspace_dir=ai_workspace,
                test_goal=ai_goal,
                test_config=test_config,
                package_name=package
            )
            exploration_strategy.set_max_steps(steps)
        else:
            exploration_strategy = WeightedStrategy()

        # Create exploration engine
        engine = ExplorationEngine(
            device=target_device,
            strategy=exploration_strategy,
            package=package,
            screenshot_dir=screenshot_dir if screenshots else "./screenshots"
        )

        # Run exploration
        click.echo("Starting exploration...")
        click.echo("-" * 60)

        try:
            result = engine.explore(max_steps=steps, save_screenshots=screenshots)
            all_results.append(result)

            # Generate reports
            click.echo("\nGenerating reports...")

            reporter = ReportGenerator()

            # Text report
            text_report_path = f"{run_output}/report.txt"
            reporter.save_text_report(result, text_report_path)

            # JSON report
            json_report_path = f"{run_output}/report.json"
            reporter.save_json_report(result, json_report_path)

            # Print summary for this run
            click.echo()
            click.echo("=" * 60)
            if result.crash_detected:
                click.echo("🔴 CRASH DETECTED!")
            else:
                click.echo(f"Exploration Complete! (Run {run_num}/{runs})")
            click.echo("=" * 60)
            click.echo(f"Duration: {result.duration:.1f}s")
            click.echo(f"Total Events: {result.total_events}")
            click.echo(f"Unique States: {result.unique_states}")

            if result.crash_detected:
                click.echo(f"\n🔴 Crash Info: {result.crash_info}")

            click.echo(f"\nReports saved to: {run_output}")
            click.echo(f"  - {text_report_path}")
            click.echo(f"  - {json_report_path}")

            if screenshots:
                click.echo(f"  - Screenshots: {screenshot_dir}/")

        except KeyboardInterrupt:
            click.echo("\n\nExploration interrupted by user")
            break
        except Exception as e:
            click.echo(f"\nERROR in run {run_num}: {e}")
            logger.exception(f"Exploration failed in run {run_num}")
            continue

        # Wait between runs (except after last run)
        if run_num < runs:
            click.echo("\n⏸️  Waiting 5 seconds before next run...")
            import time
            time.sleep(5)

    # Print overall summary if multiple runs
    if runs > 1 and all_results:
        click.echo()
        click.echo("=" * 60)
        click.echo(f"🎉 All {runs} Test Runs Complete!")
        click.echo("=" * 60)

        total_duration = sum(r.duration for r in all_results)
        avg_events = sum(r.total_events for r in all_results) / len(all_results)
        avg_states = sum(r.unique_states for r in all_results) / len(all_results)
        crash_count = sum(1 for r in all_results if r.crash_detected)

        click.echo(f"\n📊 Summary:")
        click.echo(f"  Total Duration: {total_duration:.1f}s")
        click.echo(f"  Avg Events/Run: {avg_events:.1f}")
        click.echo(f"  Avg States/Run: {avg_states:.1f}")
        click.echo(f"  Crashes Detected: {crash_count}/{runs}")

        click.echo(f"\n📁 Reports:")
        for i in range(1, runs + 1):
            if runs > 1:
                click.echo(f"  Run {i}: {base_output}_run{i:03d}/")
            else:
                click.echo(f"  {base_output}/")


if __name__ == '__main__':
    cli()

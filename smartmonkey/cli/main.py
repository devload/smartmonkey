"""SmartMonkey CLI"""

import click
import sys
from pathlib import Path
from ..device.device import Device
from ..device.adb_manager import ADBManager
from ..exploration.exploration_engine import ExplorationEngine
from ..exploration.strategies.random_strategy import RandomStrategy
from ..exploration.strategies.weighted_strategy import WeightedStrategy
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
@click.option('--strategy', '-s', type=click.Choice(['random', 'weighted']), default='weighted',
              help='Exploration strategy (default: weighted)')
@click.option('--output', '-o', help='Output directory (default: ./reports/<timestamp>)')
@click.option('--screenshots/--no-screenshots', default=True, help='Save screenshots (default: yes)')
def run(device, package, steps, strategy, output, screenshots):
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
    click.echo()

    # Create output directory
    if not output:
        output = f"./reports/{get_timestamp()}"

    ensure_dir(output)
    screenshot_dir = f"{output}/screenshots" if screenshots else None

    click.echo(f"Output directory: {output}")
    if screenshots:
        click.echo(f"Screenshots: {screenshot_dir}")
    click.echo()

    # Select strategy
    if strategy == 'random':
        exploration_strategy = RandomStrategy()
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

        # Generate reports
        click.echo("\nGenerating reports...")

        reporter = ReportGenerator()

        # Text report
        text_report_path = f"{output}/report.txt"
        reporter.save_text_report(result, text_report_path)

        # JSON report
        json_report_path = f"{output}/report.json"
        reporter.save_json_report(result, json_report_path)

        # Print summary
        click.echo()
        click.echo("=" * 60)
        if result.crash_detected:
            click.echo("🔴 CRASH DETECTED!")
        else:
            click.echo("Exploration Complete!")
        click.echo("=" * 60)
        click.echo(f"Duration: {result.duration:.1f}s")
        click.echo(f"Total Events: {result.total_events}")
        click.echo(f"Unique States: {result.unique_states}")

        if result.crash_detected:
            click.echo(f"\n🔴 Crash Info: {result.crash_info}")

        click.echo(f"\nReports saved to: {output}")
        click.echo(f"  - {text_report_path}")
        click.echo(f"  - {json_report_path}")

        if screenshots:
            click.echo(f"  - Screenshots: {screenshot_dir}/")

    except KeyboardInterrupt:
        click.echo("\n\nExploration interrupted by user")
    except Exception as e:
        click.echo(f"\nERROR: {e}")
        logger.exception("Exploration failed")
        sys.exit(1)


if __name__ == '__main__':
    cli()

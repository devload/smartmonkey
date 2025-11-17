"""Devices command - List connected Android devices"""

import click
from ...device.device import Device
from ...device.adb_manager import ADBManager


@click.command('devices')
def devices_command():
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

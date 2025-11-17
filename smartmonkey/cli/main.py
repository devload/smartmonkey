"""SmartMonkey CLI - Unified command-line interface"""

import click
from .commands.web import web_command
from .commands.mobile import mobile_command
from .commands.devices import devices_command
from .commands.ai_command import ai_command
from ..utils.logger import setup_logger

setup_logger()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """SmartMonkey - Intelligent Android App Testing Tool

    \b
    Examples:
      # List connected devices
      smartmonkey devices

      # Test a mobile app
      smartmonkey mobile -p com.example.app -s 50

      # Test a web app
      smartmonkey web -u https://m.naver.com -s 10

      # AI-driven testing
      smartmonkey ai -u https://www.coupang.com -m "상품 검색하기" -s 5
    """
    pass


# Register subcommands
cli.add_command(web_command)
cli.add_command(mobile_command)
cli.add_command(devices_command)
cli.add_command(ai_command)


if __name__ == '__main__':
    cli()

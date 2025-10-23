"""Custom exceptions for SmartMonkey"""


class SmartMonkeyException(Exception):
    """Base exception for SmartMonkey"""
    pass


class DeviceConnectionError(SmartMonkeyException):
    """Raised when device connection fails"""
    pass


class ADBCommandError(SmartMonkeyException):
    """Raised when ADB command execution fails"""
    pass


class UIParseError(SmartMonkeyException):
    """Raised when UI hierarchy parsing fails"""
    pass


class ConfigurationError(SmartMonkeyException):
    """Raised when configuration is invalid"""
    pass


class AppNotFoundError(SmartMonkeyException):
    """Raised when target app is not found"""
    pass


class ExplorationError(SmartMonkeyException):
    """Raised when exploration encounters an error"""
    pass

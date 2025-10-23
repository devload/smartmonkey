"""Pytest fixtures"""

import pytest


@pytest.fixture
def mock_device():
    """Mock device for testing"""
    class MockDevice:
        def __init__(self):
            self.serial = "test_device"
            self.model = "Test Model"

    return MockDevice()

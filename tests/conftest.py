"""Shared fixtures for MantisClaw tests."""
import pytest
from pathlib import Path


@pytest.fixture
def workspace_root():
    return Path(__file__).parent.parent


@pytest.fixture
def config(workspace_root):
    """Load default config."""
    import yaml
    config_path = workspace_root / "config" / "default.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

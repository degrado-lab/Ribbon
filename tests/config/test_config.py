import pytest
import ribbon.config.config as config
import ribbon.config.download as download
import ribbon.config.parse_config as parse_config

from unittest.mock import patch
from pathlib import Path
import ribbon.config.parse_config as parse_config

def test_get_default_config(tmp_path):
    """Test that get_default_config returns the expected dictionary structure."""
    with patch('ribbon.config.parse_config.get_latest_tasks_version') as mocked_get_version:
        mocked_get_version.return_value = "v1.0.0"
        
        config = parse_config.get_default_config(tmp_path)
        
        assert config["tasks_version"] == "v1.0.0"
        assert config["tasks_path"] == str(tmp_path / "ribbon_tasks")
        assert config["containers_path"] == str(tmp_path / "ribbon_containers")
        assert config["cache_path"] == str(tmp_path / "ribbon_cache")

def test_get_default_config_fallback(tmp_path):
    """Test get_default_config fallback when network fails."""
    with patch('ribbon.config.parse_config.get_latest_tasks_version') as mocked_get_version:
        mocked_get_version.side_effect = Exception("Network Error")
        
        # This should trigger the fallback to v0.1.3
        config = parse_config.get_default_config(tmp_path)
        
        assert config["tasks_version"] == "v0.1.3"

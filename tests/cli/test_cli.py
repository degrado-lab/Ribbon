import pytest
import ribbon.cli.cli as cli

import subprocess
import pytest

def test_cli_help():
    """Test 'ribbon --help' command."""
    result = subprocess.run(['ribbon', '--help'], capture_output=True, text=True)
    assert result.returncode == 0
    assert "Manage Ribbon task definitions" in result.stdout
    assert "Commands" in result.stdout
    assert "list" in result.stdout
    assert "info" in result.stdout

def test_cli_info():
    """Test 'ribbon info' command."""
    result = subprocess.run(['ribbon', 'info'], capture_output=True, text=True)
    assert result.returncode == 0
    # Check for some expected strings in the output
    assert "Ribbon home directory" in result.stdout
    assert "Active tasks version" in result.stdout
    assert "Tasks directory" in result.stdout

def test_cli_list_versions():
    """Test 'ribbon list' command (lists versions by default)."""
    result = subprocess.run(['ribbon', 'list'], capture_output=True, text=True)
    assert result.returncode == 0
    # It should list at least the default version or local versions
    assert "v0" in result.stdout or "Remote releases" in result.stdout

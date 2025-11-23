"""
Unit tests for app_config module.

Tests configuration loading, validation, and error handling.
"""

import pytest
import os
import json
import tempfile
import shutil
from app_config import load_config, AppConfig


class TestLoadConfig:
    """Test cases for load_config function."""

    @pytest.fixture
    def test_dir(self):
        """Create and cleanup temporary directory for test files."""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_load_valid_config(self, test_dir):
        """Test loading a valid JSON configuration file."""
        config_data = {"key": "value", "number": 42}
        config_file = os.path.join(test_dir, "config.json")

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        result = load_config(config_file)
        assert result == config_data

    def test_load_config_file_not_found(self):
        """Test that FileNotFoundError leads to SystemExit."""
        with pytest.raises(SystemExit):
            load_config("/nonexistent/path/config.json")

    def test_load_invalid_json(self, test_dir):
        """Test that invalid JSON leads to SystemExit."""
        config_file = os.path.join(test_dir, "invalid.json")

        with open(config_file, "w") as f:
            f.write("{invalid json content")

        with pytest.raises(SystemExit):
            load_config(config_file)

    def test_load_config_with_nested_data(self, test_dir):
        """Test loading configuration with nested structures."""
        config_data = {
            "model": {
                "name": "gpt-4o",
                "parameters": {"temperature": 0.7, "top_p": 0.9},
            },
            "response": {"speak": True, "rate": 140},
        }
        config_file = os.path.join(test_dir, "nested.json")

        with open(config_file, "w") as f:
            json.dump(config_data, f)

        result = load_config(config_file)
        assert result == config_data
        assert result["model"]["name"] == "gpt-4o"
        assert result["model"]["parameters"]["temperature"] == 0.7

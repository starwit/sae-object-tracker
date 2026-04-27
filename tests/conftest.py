import pytest

# This is necessary to prevent tests from accidentally loading real config files
@pytest.fixture(autouse=True)
def set_settings_file_location(monkeypatch):
    monkeypatch.setenv('SETTINGS_FILE', '/tmp/should_not_exist.yaml')
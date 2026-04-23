from unittest.mock import patch

import pytest

from objecttracker.config import ObjectTrackerConfig, RedisConfig


@pytest.fixture(autouse=True)
def disable_prometheus():
    with patch('objecttracker.stage.start_http_server'):
        yield

@pytest.fixture(autouse=True)
def set_config():
    with patch('objecttracker.stage.ObjectTrackerConfig') as mock_config:
        mock_config.return_value = ObjectTrackerConfig(
            log_level='DEBUG',
            redis=RedisConfig(
                stream_id='stream1',
            )
        )
        yield

@pytest.fixture
def redis_publisher_mock():
    with patch('objecttracker.stage.RedisPublisher') as mock_publisher:
        yield mock_publisher.return_value.__enter__.return_value

@pytest.fixture
def inject_consumer_messages():
    with patch('objecttracker.stage.RedisConsumer') as mock_consumer:
        def _inject_messages(messages):
            mock_consumer.return_value.__enter__.return_value.return_value.__iter__.return_value = iter(messages)
        yield _inject_messages
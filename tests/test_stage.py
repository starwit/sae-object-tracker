from typing import List, Tuple
from unittest.mock import patch

import pytest
from visionapi.sae_pb2 import Detection, SaeMessage, BoundingBox, VideoFrame, Shape
from visionapi.common_pb2 import MessageType

from objecttracker.config import (ObjectTrackerConfig, RedisConfig)
from objecttracker.stage import run_stage

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


def test_stationary_object(redis_publisher_mock, inject_consumer_messages):
    test_messages = [('objectdetector:stream1', m) for m in _to_msg_bytes_list(source_id='stream1', detections=_make_stationary_trajectory())]

    inject_consumer_messages(test_messages)

    run_stage()

    assert redis_publisher_mock.call_count == len(test_messages)


def _make_stationary_trajectory() -> List[Detection]:
    return [
        _make_detection(0.5, 0.5, 0.1, 0.1)
    ] * 5

def _make_linear_trajectory() -> List[Detection]:
    return [
        _make_detection(
            center_x=0.5 + 0.025 * c, 
            center_y=0.5 + 0.025 * c, 
            width=0.1, 
            height=0.1
        ) for c in range(6)
    ]

def _make_detection(center_x: float, center_y: float, width: float, height: float) -> Detection:
    return Detection(
        bounding_box=BoundingBox(
            max_x=center_x + width / 2,
            min_x=center_x - width / 2,
            max_y=center_y + height / 2,
            min_y=center_y - height / 2
        ),
        confidence=0.9,
        class_id=1
    )

def _to_msg_bytes_list(source_id: str, detections: List[Detection]) -> List[bytes]:
    messages = []
    for idx, det in enumerate(detections):
        sae_msg = SaeMessage(
            frame=VideoFrame(
                source_id=source_id, 
                timestamp_utc_ms=idx * 1000,
            ),
            type=MessageType.SAE, 
            detections=[det]
        )
        messages.append(sae_msg.SerializeToString())
    return messages
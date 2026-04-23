from typing import List

import numpy as np
from visionapi.common_pb2 import MessageType
from visionapi.sae_pb2 import Detection, SaeMessage

from objecttracker.stage import run_stage


def test_stationary_object(redis_publisher_mock, inject_consumer_messages):
    test_messages = [('objectdetector:stream1', m) for m in _to_msg_bytes_list(source_id='stream1', detections=_make_stationary_trajectory())]

    inject_consumer_messages(test_messages)

    run_stage()

    # Assert that one message is published for each input message
    assert redis_publisher_mock.call_count == len(test_messages)

    # Assert that the same track ID is assigned to all detections of the stationary object
    object_ids = set()
    for call in redis_publisher_mock.call_args_list:
        sae_msg = _call_to_sae_msg(call)
        assert len(sae_msg.detections) == 1
        object_ids.add(sae_msg.detections[0].object_id)
    assert len(object_ids) == 1

def test_linearly_moving_object(redis_publisher_mock, inject_consumer_messages):
    test_messages = [('objectdetector:stream1', m) for m in _to_msg_bytes_list(source_id='stream1', detections=_make_linear_trajectory())]

    inject_consumer_messages(test_messages)

    run_stage()

    # Assert that one message is published for each input message
    assert redis_publisher_mock.call_count == len(test_messages)

    # Assert that the same track ID is assigned to all detections of the moving object
    object_ids = set()
    for call in redis_publisher_mock.call_args_list:
        sae_msg = _call_to_sae_msg(call)
        assert len(sae_msg.detections) == 1
        object_ids.add(sae_msg.detections[0].object_id)
    assert len(object_ids) == 1

def test_unrelated_objects(redis_publisher_mock, inject_consumer_messages):
    test_messages = [
        ('objectdetector:stream1', _make_sae_msg(source_id='stream1', timestamp_utc_ms=0, detections=[_make_det(0.1, 0.1, 0.1, 0.1)]).SerializeToString()),
        ('objectdetector:stream1', _make_sae_msg(source_id='stream1', timestamp_utc_ms=1000, detections=[_make_det(0.9, 0.9, 0.1, 0.1)]).SerializeToString())
    ]

    inject_consumer_messages(test_messages)

    run_stage()

    # Assert that one message is published for each input message
    assert redis_publisher_mock.call_count == len(test_messages)

    # Assert that different track IDs are assigned to the two unrelated objects
    object_ids = set()
    for call in redis_publisher_mock.call_args_list:
        sae_msg = _call_to_sae_msg(call)
        assert len(sae_msg.detections) == 1
        object_ids.add(sae_msg.detections[0].object_id)
    assert len(object_ids) == 2

def _make_stationary_trajectory() -> List[Detection]:
    return [
        _make_det(0.5, 0.5, 0.1, 0.1)
    ] * 5

def _make_linear_trajectory() -> List[Detection]:
    return [
        _make_det(
            center_x=0.5 + 0.025 * c, 
            center_y=0.5 + 0.025 * c, 
            width=0.1, 
            height=0.1
        ) for c in range(6)
    ]

def _make_det(center_x: float, center_y: float, width: float, height: float) -> Detection:
    det = Detection()

    det.bounding_box.max_x = center_x + width / 2
    det.bounding_box.min_x = center_x - width / 2
    det.bounding_box.max_y = center_y + height / 2
    det.bounding_box.min_y = center_y - height / 2
    det.confidence = 0.9
    det.class_id = 1
    
    return det

def _make_sae_msg(source_id: str, timestamp_utc_ms: int, detections: List[Detection]) -> SaeMessage:
    sae_msg = SaeMessage()

    sae_msg.frame.source_id = source_id
    sae_msg.frame.shape.height = 10
    sae_msg.frame.shape.width = 10
    sae_msg.frame.shape.channels = 3
    sae_msg.frame.timestamp_utc_ms = timestamp_utc_ms
    sae_msg.frame.frame_data = np.zeros((10, 10, 3), dtype=np.uint8).tobytes()
    sae_msg.type = MessageType.SAE
    sae_msg.detections.extend(detections)

    return sae_msg

def _to_msg_bytes_list(source_id: str, detections: List[Detection]) -> List[bytes]:
    messages = []
    for idx, det in enumerate(detections):
        messages.append(_make_sae_msg(
            source_id=source_id, 
            timestamp_utc_ms=idx * 1000, 
            detections=[det]
        ).SerializeToString())
    return messages

def _call_to_sae_msg(call) -> SaeMessage:
    args, _ = call
    msg_bytes = args[1]
    sae_msg = SaeMessage()
    sae_msg.ParseFromString(msg_bytes)
    return sae_msg
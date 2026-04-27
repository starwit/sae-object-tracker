import pytest
from pydantic import ValidationError

from objecttracker.config import ObjectTrackerConfig

def test_empty_config():
    with pytest.raises(ValidationError):
        config = ObjectTrackerConfig()

def test_minimal_config():
    config = ObjectTrackerConfig.model_validate({
        'redis': {
            'stream_id': 'test_stream'
        }
    })

    assert config.redis.stream_id == 'test_stream'

def test_defaults():
    config = ObjectTrackerConfig.model_validate({
        'redis': {
            'stream_id': 'test_stream'
        }
    })

    assert config.log_level == 'WARNING'
    assert config.redis.host == 'localhost'
    assert config.redis.port == 6379
    assert config.redis.stream_id == 'test_stream'
    assert config.redis.input_stream_prefix == 'objectdetector'
    assert config.redis.output_stream_prefix == 'objecttracker'
    assert config.tracker_algorithm == 'OCSORT'
    assert config.tracker_config.det_thresh == 0.2
    assert config.tracker_config.max_age == 30
    assert config.tracker_config.min_hits == 3
    assert config.tracker_config.asso_threshold == 0.3
    assert config.tracker_config.delta_t == 3
    assert config.tracker_config.asso_func == 'iou'
    assert config.tracker_config.inertia == 0.2
    assert config.tracker_config.use_byte == False
    assert config.tracker_config.Q_xy_scaling == 0.01
    assert config.tracker_config.Q_s_scaling == 0.0001
    assert config.prometheus_port == 8000
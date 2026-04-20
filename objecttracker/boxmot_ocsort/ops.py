# Mikel Broström 🔥 Yolo Tracking 🧾 AGPL-3.0 license

import numpy as np

def xyxy2xysr(x):
    """
    Converts bounding box coordinates from (x1, y1, x2, y2) format to (x, y, s, r) format.

    Args:
        bbox (np.ndarray): The input bounding box coordinates in (x1, y1, x2, y2) format.
    Returns:
        z (np.ndarray): The bounding box coordinates in (x, y, s, r) format, where
                            x, y is the center of the box,
                            s is the scale (area), and
                            r is the aspect ratio.
    """
    x = x[0:4]
    y = np.copy(x)
    w = y[..., 2] - y[..., 0]        # width
    h = y[..., 3] - y[..., 1]        # height
    y[..., 0] = y[..., 0] + w / 2.0  # x center
    y[..., 1] = y[..., 1] + h / 2.0  # y center
    y[..., 2] = w * h                # scale (area)
    y[..., 3] = w / (h + 1e-6)       # aspect ratio
    y = y.reshape((4, 1))
    return y
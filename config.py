# config.py
"""
Configuration settings for gesture control
"""

# Camera settings
CAMERA_INDEX = 0

# MediaPipe settings
MAX_HANDS = 2
MODEL_COMPLEXITY = 1
MIN_DETECTION_CONFIDENCE = 0.8
MIN_TRACKING_CONFIDENCE = 0.8

# Gesture cooldowns (seconds)
HANG_COOLDOWN = 10.0
ROCK_COOLDOWN = 10.0
VOLUME_COOLDOWN = 0.1
PINCH_COOLDOWN = 0.15

# Pinch detection thresholds (pixels)
PINCH_THRESHOLD = 55
RELEASE_THRESHOLD = 80

# Mouse smoothing settings
MOUSE_BUFFER_SIZE = 7
MOUSE_EXPONENTIAL_WEIGHT = 0.25
EDGE_DAMPENING_MARGIN = 0.15

# Display settings
DISPLAY_FPS = True
DISPLAY_GESTURE = True
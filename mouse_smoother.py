# mouse_smoother.py
"""
Mouse smoothing and movement control
"""
from collections import deque
import pyautogui
import numpy as np


class MouseSmoothing:
    """Smooth mouse movement using moving average and exponential smoothing"""
    
    def __init__(self, buffer_size=5, exponential_weight=0.3):
        self.buffer_size = buffer_size
        self.exp_weight = exponential_weight
        self.position_buffer = deque(maxlen=buffer_size)
        self.smooth_x = None
        self.smooth_y = None
        
    def add_position(self, x, y):
        """Add a new position to the smoothing buffer"""
        self.position_buffer.append((x, y))
        
    def get_smoothed_position(self):
        """Calculate and return smoothed position"""
        if not self.position_buffer:
            return None, None
            
        # Moving average
        avg_x = sum(pos[0] for pos in self.position_buffer) / len(self.position_buffer)
        avg_y = sum(pos[1] for pos in self.position_buffer) / len(self.position_buffer)
        
        # Exponential smoothing for extra stability
        if self.smooth_x is None:
            self.smooth_x = avg_x
            self.smooth_y = avg_y
        else:
            self.smooth_x = self.exp_weight * avg_x + (1 - self.exp_weight) * self.smooth_x
            self.smooth_y = self.exp_weight * avg_y + (1 - self.exp_weight) * self.smooth_y
            
        return self.smooth_x, self.smooth_y


class MouseController:
    """Handle mouse movement and clicking"""
    
    def __init__(self, screen_width, screen_height, edge_margin=0.15):
        self.screen_w = screen_width
        self.screen_h = screen_height
        self.edge_margin = edge_margin
        self.smoother = MouseSmoothing(buffer_size=7, exponential_weight=0.25)
        
    def process_movement(self, hand_x, hand_y, frame_width, frame_height):
        """
        Process hand position and move mouse smoothly
        Args:
            hand_x, hand_y: Hand landmark position in frame
            frame_width, frame_height: Camera frame dimensions
        """
        # Normalize to 0-1 range
        norm_x = hand_x / frame_width
        norm_y = hand_y / frame_height
        
        # Apply edge dampening (reduce jitter near screen edges)
        norm_x = self._apply_edge_dampening(norm_x)
        norm_y = self._apply_edge_dampening(norm_y)
        
        # Map to screen coordinates
        target_x = norm_x * self.screen_w
        target_y = norm_y * self.screen_h
        
        # Add to smoothing buffer
        self.smoother.add_position(target_x, target_y)
        smooth_x, smooth_y = self.smoother.get_smoothed_position()
        
        # Move mouse
        if smooth_x is not None and smooth_y is not None:
            try:
                pyautogui.moveTo(smooth_x, smooth_y, duration=0)
            except:
                pass
                
    def _apply_edge_dampening(self, value):
        """Reduce sensitivity near edges"""
        if value < self.edge_margin:
            return value * (1 - self.edge_margin) / self.edge_margin
        elif value > (1 - self.edge_margin):
            return self.edge_margin + (value - (1 - self.edge_margin)) * (1 - self.edge_margin) / self.edge_margin
        return value
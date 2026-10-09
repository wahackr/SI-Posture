"""Camera capture and calibration module."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

import cv2
import numpy as np
from typing import Optional, List, Tuple


class CameraError(Exception):
    """Base camera error."""
    pass


class CameraNotAvailable(CameraError):
    """No cameras available."""
    pass


class CameraUnavailable(CameraError):
    """Specific camera unavailable."""
    pass


class Camera:
    """Webcam capture handler."""
    
    def __init__(self, camera_index: int = 0):
        self.camera_index = camera_index
        self.cap = None
        self._is_opened = False
    
    def open(self) -> bool:
        """Open camera."""
        if self.cap is not None:
            return True
        
        self.cap = cv2.VideoCapture(self.camera_index)
        if not self.cap.isOpened():
            raise CameraUnavailable(f"Failed to open camera index {self.camera_index}")
        
        self._is_opened = True
        return True
    
    def close(self):
        """Close camera."""
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            self._is_opened = False
    
    def is_opened(self) -> bool:
        """Check if camera is opened."""
        return self._is_opened and self.cap is not None and self.cap.isOpened()
    
    def get_frame(self) -> Optional[np.ndarray]:
        """Get current frame."""
        if not self.is_opened():
            return None
        
        ret, frame = self.cap.read()
        if not ret:
            return None
        
        return frame
    
    def get_frame_rgb(self) -> Optional[np.ndarray]:
        """Get frame in RGB format for display."""
        frame = self.get_frame()
        if frame is None:
            return None
        
        # OpenCV reads in BGR, convert to RGB for display
        return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    def get_frame_encoded(self) -> Optional[bytes]:
        """Get frame as JPEG encoded bytes."""
        frame = self.get_frame()
        if frame is None:
            return None
        
        _, encoded = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 85])
        return encoded.tobytes()
    
    def set_properties(self, width: int = 640, height: int = 480):
        """Set camera properties."""
        if not self.is_opened():
            return
        
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    
    def get_property(self, prop: str) -> float:
        """Get camera property."""
        if prop.startswith('CAP_PROP'):
            return self.cap.get(prop)
        return self.cap.get(prop)
    
    @property
    def name(self) -> str:
        """Get human-readable camera name."""
        name = self.cap.get(cv2.CAP_PROP_MODEL_NAME)
        if name:
            return str(name)
        return f"Camera {self.camera_index}"
    
    @property
    def index(self) -> int:
        """Get camera index."""
        return self.camera_index


class CameraEnumerator:
    """Enumerate available cameras."""
    
    @staticmethod
    def enumerate_cameras() -> List[Tuple[int, str]]:
        """List all available cameras."""
        cameras = []
        for i in range(10):  # Check up to 10 cameras
            try:
                cap = cv2.VideoCapture(i)
                if cap.isOpened():
                    cap.release()
                    name = cap.get(cv2.CAP_PROP_MODEL_NAME)
                    cameras.append((i, str(name) if name else f"Camera {i}"))
                else:
                    break
            except Exception:
                break
        
        return cameras

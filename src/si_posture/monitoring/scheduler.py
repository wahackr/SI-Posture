"""Monitoring scheduler and state management."""

import threading
from typing import Callable, Optional
from datetime import datetime
from ..models import PostureStatus
from .evaluator import PostureEvaluator


class MonitoringState:
    """Manages monitoring state and scheduling."""
    
    def __init__(
        self,
        capture_interval_seconds: int = 15,
        evaluator: Optional[PostureEvaluator] = None
    ):
        self.capture_interval_seconds = capture_interval_seconds
        self.evaluator = evaluator or PostureEvaluator()
        
        self._running = False
        self._paused = False
        self._capture_thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()
        self._last_capture_time: Optional[datetime] = None
        self._capture_callback: Optional[Callable] = None
        self._status_callback: Optional[Callable] = None
    
    def start(self):
        """Start monitoring loop."""
        if self._running:
            return
        
        self._running = True
        self._paused = False
        self._stop_event.clear()
        self._last_capture_time = datetime.now()
        
        self._capture_thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._capture_thread.start()
    
    def pause(self):
        """Pause monitoring."""
        self._paused = True
    
    def resume(self):
        """Resume monitoring."""
        self._paused = False
    
    def stop(self):
        """Stop monitoring."""
        self._running = False
        self._stop_event.set()
        
        if self._capture_thread:
            self._capture_thread.join(timeout=2.0)
            self._capture_thread = None
    
    def _capture_loop(self):
        """Main capture loop."""
        while not self._stop_event.is_set():
            try:
                # Wait for next capture interval
                self._stop_event.wait(timeout=self.capture_interval_seconds)
                
                # Check if still running
                if not self._running:
                    break
                
                # Check pause state
                if self._paused:
                    continue
                
                # Capture
                self._perform_capture()
                
            except Exception:
                pass
    
    def _perform_capture(self):
        """Perform single capture and evaluation."""
        if self._capture_callback:
            self._capture_callback()
        
        # Evaluate posture
        if self._status_callback:
            self._status_callback(self.evaluator.get_current_status())
    
    def set_callbacks(self, capture_cb: Callable, status_cb: Callable):
        """Set callbacks for capture and status updates."""
        self._capture_callback = capture_cb
        self._status_callback = status_cb
    
    def is_running(self) -> bool:
        """Check if monitoring is running."""
        return self._running
    
    def is_paused(self) -> bool:
        """Check if monitoring is paused."""
        return self._paused
    
    def get_last_capture_time(self) -> Optional[datetime]:
        """Get last capture time."""
        return self._last_capture_time
    
    def reset_evaluator(self):
        """Reset evaluator state."""
        self.evaluator.reset()

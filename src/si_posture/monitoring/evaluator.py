"""Posture evaluation engine with alert logic."""

from typing import List, Dict, Optional
from enum import Enum
from datetime import datetime, timedelta
from ..models import AIComparisonResponse, Visibility, HeadRelative, TorsoRelative, ChangeMagnitude, PostureStatus


class AlertLevel(str, Enum):
    NONE = "NONE"
    SMALL = "SMALL"
    MODERATE = "MODERATE"
    LARGE = "LARGE"


class PostureEvaluator:
    """Evaluates posture from AI comparisons and manages alerts."""
    
    def __init__(
        self,
        consecutive_window: int = 4,
        alert_threshold: int = 3,
        min_abnormal_duration_seconds: int = 45,
        alert_cooldown_minutes: int = 15
    ):
        self.consecutive_window = consecutive_window
        self.alert_threshold = alert_threshold
        self.min_abnormal_duration_seconds = min_abnormal_duration_seconds
        self.alert_cooldown_minutes = alert_cooldown_minutes
        
        # Rolling window of valid assessments
        self.assessments: List[Dict] = []
        self._last_alert_time: Optional[datetime] = None
        self._abnormal_start_time: Optional[datetime] = None
        self._current_alert_type: Optional[str] = None
    
    def is_cooldown_active(self) -> bool:
        """Check if alert cooldown is active."""
        if self._last_alert_time is None:
            return False
        
        cooldown_end = self._last_alert_time + timedelta(minutes=self.alert_cooldown_minutes)
        return datetime.now() < cooldown_end
    
    def is_minimum_duration_met(self, assessment_time: datetime) -> bool:
        """Check if minimum abnormal duration is met."""
        if self._abnormal_start_time is None:
            return False
        
        elapsed = (assessment_time - self._abnormal_start_time).total_seconds()
        return elapsed >= self.min_abnormal_duration_seconds
    
    def validate_assessment(self, response: AIComparisonResponse) -> bool:
        """Validate if assessment should be stored."""
        # Must have sufficient visibility
        if response.visibility != Visibility.SUFFICIENT:
            return False
        
        # Must have at least MODERATE change
        if response.change_magnitude in (ChangeMagnitude.NONE, ChangeMagnitude.SMALL):
            return False
        
        return True
    
    def should_trigger_alert(self, assessment_time: datetime) -> Optional[str]:
        """Determine if alert should be triggered. Returns alert type or None."""
        # Check cooldown
        if self.is_cooldown_active():
            return None
        
        # Check minimum duration
        if not self.is_minimum_duration_met(assessment_time):
            return None
        
        # Check if we have enough bad assessments
        if len(self.assessments) < self.alert_threshold:
            return None
        
        # Determine alert type based on latest valid assessment
        latest = self.assessments[-1]
        alert_type = None
        
        if latest['head_relative_to_shoulders'] == HeadRelative.FORWARD:
            alert_type = "HEAD_FORWARD"
        elif latest['torso_relative_to_reference'] == TorsoRelative.FORWARD:
            alert_type = "TORSO_FORWARD"
        
        return alert_type
    
    def add_assessment(self, response: AIComparisonResponse, assessment_time: datetime):
        """Add a new assessment to the rolling window."""
        # Validate first
        if not self.validate_assessment(response):
            return
        
        assessment_data = {
            'timestamp': assessment_time,
            'visibility': str(response.visibility),
            'head_relative_to_shoulders': str(response.head_relative_to_shoulders),
            'torso_relative_to_reference': str(response.torso_relative_to_reference),
            'change_magnitude': str(response.change_magnitude),
            'visual_evidence': response.visual_evidence
        }
        
        # Keep only recent assessments (window size)
        if len(self.assessments) >= self.consecutive_window:
            self.assessments.pop(0)
        
        self.assessments.append(assessment_data)
        
        # Track abnormal start time if new bad condition detected
        if not self._abnormal_start_time:
            if (response.head_relative_to_shoulders == HeadRelative.FORWARD or 
                response.torso_relative_to_reference == TorsoRelative.FORWARD):
                self._abnormal_start_time = assessment_time
                self._current_alert_type = self._determine_alert_type(assessment_data)
    
    def _determine_alert_type(self, data: Dict) -> Optional[str]:
        """Determine alert type from assessment data."""
        if data['head_relative_to_shoulders'] == HeadRelative.FORWARD:
            return "HEAD_FORWARD"
        elif data['torso_relative_to_reference'] == TorsoRelative.FORWARD:
            return "TORSO_FORWARD"
        return None
    
    def reset(self):
        """Reset all state."""
        self.assessments.clear()
        self._last_alert_time = None
        self._abnormal_start_time = None
        self._current_alert_type = None
    
    def get_current_status(self) -> PostureStatus:
        """Get current monitoring status."""
        if not self.assessments:
            return PostureStatus.UNKNOWN
        
        latest = self.assessments[-1]
        
        head_status = latest['head_relative_to_shoulders']
        torso_status = latest['torso_relative_to_reference']
        
        if head_status == HeadRelative.FORWARD:
            return PostureStatus.HEAD_FORWARD
        elif torso_status == TorsoRelative.FORWARD:
            return PostureStatus.TORSO_FORWARD
        
        return PostureStatus.UNKNOWN
    
    def get_last_alert_time(self) -> Optional[datetime]:
        """Get time of last alert."""
        return self._last_alert_time
    
    def record_alert(self, alert_type: str):
        """Record that an alert was triggered."""
        self._last_alert_time = datetime.now()
        self._abnormal_start_time = datetime.now()
        self._current_alert_type = alert_type

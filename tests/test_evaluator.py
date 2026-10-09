"""Test suite for SI-Posture."""

import pytest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from si_posture.models import AIComparisonResponse, Visibility, HeadRelative, TorsoRelative, ChangeMagnitude
from si_posture.monitoring.evaluator import PostureEvaluator


class TestAIComparisonResponse:
    """Test AI response validation."""
    
    def test_valid_response(self):
        """Test valid response parsing."""
        response = AIComparisonResponse(
            visibility=Visibility.SUFFICIENT,
            head_relative_to_shoulders=HeadRelative.FORWARD,
            torso_relative_to_reference=TorsoRelative.FORWARD,
            change_magnitude=ChangeMagnitude.MODERATE,
            possible_camera_change=False,
            visual_evidence="Head appears forward",
            observation_notes="Shoulders visible"
        )
        assert response.visibility == Visibility.SUFFICIENT
        assert response.head_relative_to_shoulders == HeadRelative.FORWARD
    
    def test_insufficient_visibility(self):
        """Test insufficient visibility handling."""
        response = AIComparisonResponse(
            visibility=Visibility.INSUFFICIENT,
            head_relative_to_shoulders=HeadRelative.FORWARD,
            torso_relative_to_reference=TorsoRelative.FORWARD,
            change_magnitude=ChangeMagnitude.MODERATE,
            possible_camera_change=False,
            visual_evidence="Cannot see clearly",
            observation_notes="Poor framing"
        )
        assert response.visibility == Visibility.INSUFFICIENT


class TestPostureEvaluator:
    """Test posture evaluation logic."""
    
    def test_no_alert_insufficient_visibility(self):
        """Should not alert with insufficient visibility."""
        evaluator = PostureEvaluator()
        
        from si_posture.models import AIComparisonResponse, Visibility
        
        response = AIComparisonResponse(
            visibility=Visibility.INSUFFICIENT,
            head_relative_to_shoulders=HeadRelative.FORWARD,
            torso_relative_to_reference=TorsoRelative.FORWARD,
            change_magnitude=ChangeMagnitude.MODERATE,
            possible_camera_change=False,
            visual_evidence="Poor visibility",
            observation_notes=""
        )
        
        evaluator.add_assessment(response, evaluator._assessments[0] if evaluator._assessments else None)
        assert len(evaluator.assessments) == 0
    
    def test_no_alert_small_change(self):
        """Should not alert with small change."""
        evaluator = PostureEvaluator()
        
        from si_posture.models import AIComparisonResponse
        
        response = AIComparisonResponse(
            visibility=Visibility.SUFFICIENT,
            head_relative_to_shoulders=HeadRelative.FORWARD,
            torso_relative_to_reference=TorsoRelative.FORWARD,
            change_magnitude=ChangeMagnitude.SMALL,
            possible_camera_change=False,
            visual_evidence="Minor shift",
            observation_notes=""
        )
        
        evaluator.add_assessment(response, None)
        assert len(evaluator.assessments) == 0
    
    def test_valid_assessment_stored(self):
        """Should store valid MODERATE+ assessment."""
        evaluator = PostureEvaluator()
        
        from si_posture.models import AIComparisonResponse
        
        response = AIComparisonResponse(
            visibility=Visibility.SUFFICIENT,
            head_relative_to_shoulders=HeadRelative.FORWARD,
            torso_relative_to_reference=TorsoRelative.FORWARD,
            change_magnitude=ChangeMagnitude.MODERATE,
            possible_camera_change=False,
            visual_evidence="Clear forward head",
            observation_notes=""
        )
        
        evaluator.add_assessment(response, None)
        assert len(evaluator.assessments) == 1
        assert evaluator.assessments[0]['head_relative_to_shoulders'] == 'FORWARD'
    
    def test_window_limit(self):
        """Should limit assessments to window size."""
        evaluator = PostureEvaluator(consecutive_window=3)
        
        for i in range(5):
            from si_posture.models import AIComparisonResponse
            
            response = AIComparisonResponse(
                visibility=Visibility.SUFFICIENT,
                head_relative_to_shoulders=HeadRelative.FORWARD,
                torso_relative_to_reference=TorsoRelative.FORWARD,
                change_magnitude=ChangeMagnitude.MODERATE,
                possible_camera_change=False,
                visual_evidence="",
                observation_notes=""
            )
            
            evaluator.add_assessment(response, None)
        
        assert len(evaluator.assessments) == 3
    
    def test_reset(self):
        """Should reset all state."""
        evaluator = PostureEvaluator()
        evaluator.add_assessment(None, None)
        evaluator.add_assessment(None, None)
        
        evaluator.reset()
        assert len(evaluator.assessments) == 0
        assert evaluator._last_alert_time is None


class TestAlertThreshold:
    """Test alert threshold logic."""
    
    def test_threshold_not_met(self):
        """Should not trigger with threshold not met."""
        evaluator = PostureEvaluator(alert_threshold=3)
        
        from si_posture.models import AIComparisonResponse
        
        for _ in range(2):
            response = AIComparisonResponse(
                visibility=Visibility.SUFFICIENT,
                head_relative_to_shoulders=HeadRelative.FORWARD,
                torso_relative_to_reference=TorsoRelative.FORWARD,
                change_magnitude=ChangeMagnitude.MODERATE,
                possible_camera_change=False,
                visual_evidence="",
                observation_notes=""
            )
            evaluator.add_assessment(response, None)
        
        assert evaluator.should_trigger_alert(None) is None
    
    def test_threshold_met(self):
        """Should trigger with threshold met."""
        evaluator = PostureEvaluator(alert_threshold=3)
        
        from si_posture.models import AIComparisonResponse
        
        for _ in range(3):
            response = AIComparisonResponse(
                visibility=Visibility.SUFFICIENT,
                head_relative_to_shoulders=HeadRelative.FORWARD,
                torso_relative_to_reference=TorsoRelative.FORWARD,
                change_magnitude=ChangeMagnitude.MODERATE,
                possible_camera_change=False,
                visual_evidence="",
                observation_notes=""
            )
            evaluator.add_assessment(response, None)
        
        assert evaluator.should_trigger_alert(None) == "HEAD_FORWARD"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

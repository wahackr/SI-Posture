"""Pydantic models for AI responses and data validation."""

from pydantic import BaseModel, Field
from enum import Enum
from typing import Optional


class Visibility(str, Enum):
    SUFFICIENT = "SUFFICIENT"
    INSUFFICIENT = "INSUFFICIENT"


class HeadRelative(str, Enum):
    FORWARD = "FORWARD"
    UNCHANGED = "UNCHANGED"
    UNKNOWN = "UNKNOWN"


class TorsoRelative(str, Enum):
    FORWARD = "FORWARD"
    UNCHANGED = "UNCHANGED"
    BACKWARD = "BACKWARD"
    UNKNOWN = "UNKNOWN"


class ChangeMagnitude(str, Enum):
    NONE = "NONE"
    SMALL = "SMALL"
    MODERATE = "MODERATE"
    LARGE = "LARGE"
    UNKNOWN = "UNKNOWN"


class AIComparisonResponse(BaseModel):
    """Structured response from AI comparison model."""
    visibility: Visibility = Field(..., description="Visibility of body parts")
    head_relative_to_shoulders: HeadRelative = Field(..., description="Head position relative to shoulders")
    torso_relative_to_reference: TorsoRelative = Field(..., description="Torso position relative to reference")
    change_magnitude: ChangeMagnitude = Field(..., description="Magnitude of detected changes")
    possible_camera_change: bool = Field(..., description="Possible camera angle change")
    visual_evidence: str = Field(..., description="Short text describing visual evidence")
    observation_notes: str = Field(..., description="Additional observation notes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "visibility": "SUFFICIENT",
                "head_relative_to_shoulders": "FORWARD",
                "torso_relative_to_reference": "FORWARD",
                "change_magnitude": "MODERATE",
                "possible_camera_change": False,
                "visual_evidence": "Head appears forward relative to shoulders",
                "observation_notes": "Shoulders visible and provide reference point"
            }
        }


class PostureStatus(str, Enum):
    GOOD = "GOOD"
    HEAD_FORWARD = "HEAD_FORWARD"
    TORSO_FORWARD = "TORSO_FORWARD"
    UNKNOWN = "UNKNOWN"
    PAUSED = "PAUSED"
    SERVER_OFFLINE = "SERVER_OFFLINE"
    CAMERA_ERROR = "CAMERA_ERROR"
    INSUFFICIENT_VISIBILITY = "INSUFFICIENT_VISIBILITY"

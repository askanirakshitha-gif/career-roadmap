"""
schemas.py — Defines the "shape" of data coming IN and going OUT of the API.

Pydantic schemas do two things:
  1. VALIDATE input — if frontend sends wrong data, FastAPI auto-rejects it with clear error
  2. SERIALIZE output — converts SQLAlchemy model objects into JSON for the frontend

Think of schemas as "contracts" between frontend and backend.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


# ─── INPUT SCHEMA (what frontend sends TO backend) ───────────────────────────

class UserInput(BaseModel):
    """Data the Streamlit frontend sends when requesting a roadmap."""
    name: str = Field(..., min_length=1, max_length=100, example="Priya Sharma")
    student_class: str = Field(..., example="B.Tech 2nd Year / 10th Grade")
    target_role: str = Field(..., example="Data Scientist")
    current_skills: List[str] = Field(default=[], example=["Python", "Excel"])
    interests: List[str] = Field(default=[], example=["AI/ML", "Data Analysis"])

    class Config:
        # Example shown in /docs (Swagger UI)
        json_schema_extra = {
            "example": {
                "name": "Arjun Kumar",
                "student_class": "B.Tech 2nd Year CSE",
                "target_role": "Data Scientist",
                "current_skills": ["Python", "Excel", "Basic Statistics"],
                "interests": ["Machine Learning", "Data Visualization"]
            }
        }


# ─── OUTPUT SCHEMA (what backend sends BACK to frontend) ─────────────────────

class RoadmapOut(BaseModel):
    """Full roadmap response — mirrors the Roadmap database model."""
    id: int
    name: str
    student_class: str
    target_role: str
    current_skills: List[str]
    interests: List[str]
    skill_gaps: List[str]
    study_plan: List[Dict[str, Any]]
    mind_map: Dict[str, Any]
    job_prediction: Dict[str, Any]
    resources: List[Dict[str, Any]]
    estimated_months: int
    created_at: datetime

    class Config:
        from_attributes = True   # Allows reading from SQLAlchemy model objects
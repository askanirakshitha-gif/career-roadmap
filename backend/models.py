"""
models.py — Defines the PostgreSQL database tables as Python classes.

Each class = one table in PostgreSQL.
Each class attribute = one column in that table.

SQLAlchemy automatically converts these Python classes into SQL CREATE TABLE statements.
"""

from sqlalchemy import Column, Integer, String, JSON, DateTime, Text
from database import Base
from datetime import datetime


class Roadmap(Base):
    """
    'roadmaps' table — stores every generated career roadmap.
    
    The JSON columns store lists/dicts (PostgreSQL handles JSON natively).
    This avoids needing separate tables for skills, steps, etc.
    """
    __tablename__ = "roadmaps"

    # Primary key — auto-increments (1, 2, 3...)
    id = Column(Integer, primary_key=True, index=True)

    # User info
    name           = Column(String(100), nullable=False)
    student_class  = Column(String(50), nullable=False)   # e.g. "10th Grade", "B.Tech 2nd Year"
    target_role    = Column(String(100), nullable=False)

    # Stored as JSON arrays: ["Python", "Excel", ...]
    current_skills = Column(JSON, default=[])
    interests      = Column(JSON, default=[])

    # AI-generated content (all stored as JSON)
    skill_gaps     = Column(JSON, default=[])   # ["Machine Learning", "SQL", ...]
    study_plan     = Column(JSON, default=[])   # [{month: 1, topic: "...", hours: 10}, ...]
    mind_map       = Column(JSON, default={})   # {center: "...", branches: [...]}
    job_prediction = Column(JSON, default={})   # {top_jobs: [...], salary_range: "...", demand: "..."}
    resources      = Column(JSON, default=[])   # [{name: "...", url: "...", type: "free"}, ...]
    estimated_months = Column(Integer, default=6)

    # Auto-set when record is created
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Roadmap id={self.id} name={self.name} role={self.target_role}>"
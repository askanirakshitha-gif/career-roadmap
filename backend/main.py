import os
from dotenv import load_dotenv

load_dotenv() # This loads the variables from your .env file
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from database import get_db, engine
import models
import schemas
from ai_service import generate_full_roadmap

# Create all DB tables on startup
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Career Roadmap API",
    description="Generates personalized career roadmaps with AI",
    version="1.0.0"
)

# Allow Streamlit frontend to talk to this backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],       # In production: use your actual domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Career Roadmap API is running!", "docs": "/docs"}


@app.get("/debug/info")
def debug_info():
    import os
    try:
        engine_url = str(engine.url)
    except Exception:
        engine_url = None
    return {"env_DATABASE_URL": os.getenv("DATABASE_URL"), "cwd": os.getcwd(), "engine_url": engine_url}


@app.post("/api/roadmap", response_model=schemas.RoadmapOut)
def create_roadmap(user_input: schemas.UserInput, db: Session = Depends(get_db)):
    """
    Main endpoint: takes user profile, generates AI roadmap,
    saves to database, returns full roadmap. In development this
    returns a deterministic sample that matches `schemas.RoadmapOut`.
    """
    from datetime import datetime

    # Deterministic sample matching RoadmapOut fields
    sample = {
        "id": 1,
        "name": user_input.name,
        "student_class": user_input.student_class,
        "target_role": user_input.target_role,
        "current_skills": user_input.current_skills,
        "interests": user_input.interests,
        "skill_gaps": ["Advanced SQL", "Distributed Systems"],
        "study_plan": [
            {"month": 1, "topic": "Core Python", "description": "Practice Python fundamentals", "weekly_hours": 8, "milestones": ["Basic scripts", "OOP basics"], "tools": ["Real Python"]}
        ],
        "mind_map": {"center": user_input.target_role, "branches": [{"name": "Core Skills", "color": "#FF0000", "children": [{"name": "APIs", "priority": "high"}]}]},
        "job_prediction": {"top_jobs": [{"title": user_input.target_role, "demand": "High", "avg_salary_lpa": "6-12", "growth_rate": "8%", "top_companies": ["CompanyA"], "skills_needed": user_input.current_skills}], "market_outlook": "Stable demand", "best_sectors": ["SaaS"], "future_trend": "Cloud-native roles", "demand_score": 8, "salary_growth": "10%"},
        "resources": [{"name": "Coursera Backend", "type": "Course", "url": "https://coursera.org", "cost": "Paid", "duration": "8 weeks", "description": "Good intro"}],
        "estimated_months": 6,
        "created_at": datetime.utcnow()
    }

    return sample


@app.get("/api/roadmaps", response_model=list[schemas.RoadmapOut])
def get_all_roadmaps(db: Session = Depends(get_db)):
    """Get all saved roadmaps from the database."""
    return db.query(models.Roadmap).order_by(models.Roadmap.created_at.desc()).all()


@app.get("/api/roadmap/{roadmap_id}", response_model=schemas.RoadmapOut)
def get_roadmap(roadmap_id: int, db: Session = Depends(get_db)):
    """Get a specific roadmap by ID."""
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    return roadmap


@app.delete("/api/roadmap/{roadmap_id}")
def delete_roadmap(roadmap_id: int, db: Session = Depends(get_db)):
    """Delete a roadmap by ID."""
    roadmap = db.query(models.Roadmap).filter(models.Roadmap.id == roadmap_id).first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found")
    db.delete(roadmap)
    db.commit()
    return {"message": "Deleted successfully"}


@app.get("/debug/anthropic")
def debug_anthropic():
    """Return whether ANTHROPIC_API_KEY is visible to the running process (redacted)."""
    key = os.getenv("ANTHROPIC_API_KEY")
    if not key:
        return {"anthropic_set": False, "anthropic_key_redacted": None}
    # Redact key: show first 4 and last 4 chars if long enough
    if len(key) > 8:
        redacted = f"{key[:4]}...{key[-4:]}"
    else:
        redacted = "****"
    return {"anthropic_set": True, "anthropic_key_redacted": redacted}


@app.get("/debug/anthropic_status")
def debug_anthropic_status():
    """Inspect ai_service module to show whether Anthropic was imported and client created."""
    try:
        import ai_service
    except Exception as e:
        return {"error": f"Failed to import ai_service: {e}"}
    info = {
        "_ANTHROPIC_AVAILABLE": getattr(ai_service, "_ANTHROPIC_AVAILABLE", None),
        "_ANTHROPIC_KEY_set": bool(getattr(ai_service, "_ANTHROPIC_KEY", None)),
        "client_is_none": getattr(ai_service, "client", None) is None,
    }
    init_err = getattr(ai_service, "_ANTHROPIC_INIT_ERROR", None)
    info["_ANTHROPIC_INIT_ERROR"] = init_err[:1000] if isinstance(init_err, str) else None
    return info


@app.get("/debug/anthropic_error_full")
def debug_anthropic_error_full():
    """Return full Anthropic init error (for debugging only)."""
    try:
        import ai_service
    except Exception as e:
        return {"error": f"Failed to import ai_service: {e}"}
    return {"_ANTHROPIC_INIT_ERROR_full": getattr(ai_service, "_ANTHROPIC_INIT_ERROR", None)}
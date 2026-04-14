"""
app.py — Streamlit Frontend for AI Career Roadmap Generator

This file is the entire frontend. Streamlit turns Python code into a web app.
It calls the FastAPI backend using the 'requests' library.

Run with: streamlit run app.py
"""

import os
import streamlit as st
import requests
import json
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from datetime import datetime

# ─── CONFIGURATION ────────────────────────────────────────────────────────────

# URL of your FastAPI backend (change this if backend is on a different port)
# Can be overridden with the environment variable `API_BASE_URL` or the
# sidebar input in the app at runtime.
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")

# Page configuration
st.set_page_config(
    page_title="AI Career Roadmap Generator",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ───────────────────────────────────────────────────────────────

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Sora', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .main-header h1 { font-size: 2.4rem; font-weight: 700; margin: 0; letter-spacing: -1px; }
    .main-header p  { font-size: 1rem; opacity: 0.75; margin: 0.5rem 0 0; }

    .section-card {
        background: white;
        border: 1px solid #e8e8f0;
        border-radius: 14px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 2px 12px rgba(0,0,0,0.04);
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 1rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #f0f0f8;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    
    .skill-gap-tag {
        display: inline-block;
        background: #fff0f3;
        color: #c0392b;
        border: 1px solid #f5c6cb;
        border-radius: 20px;
        padding: 4px 14px;
        margin: 4px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    .skill-have-tag {
        display: inline-block;
        background: #f0fff4;
        color: #196f3d;
        border: 1px solid #a9dfbf;
        border-radius: 20px;
        padding: 4px 14px;
        margin: 4px;
        font-size: 0.82rem;
        font-weight: 600;
    }
    
    .stat-box {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border-radius: 14px;
        padding: 1.2rem;
        text-align: center;
    }
    .stat-box .num { font-size: 2rem; font-weight: 700; }
    .stat-box .lbl { font-size: 0.75rem; opacity: 0.85; text-transform: uppercase; letter-spacing: 1px; }

    .job-card {
        border: 1px solid #e0e0f0;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        background: #fafafe;
        transition: all 0.2s;
    }
    .job-card:hover { box-shadow: 0 4px 16px rgba(102,126,234,0.15); border-color: #667eea; }
    .job-title { font-size: 1rem; font-weight: 700; color: #1a1a2e; }
    .job-salary { font-size: 0.9rem; color: #667eea; font-weight: 600; }
    .demand-high   { color: #27ae60; font-weight: 700; font-size: 0.8rem; }
    .demand-medium { color: #f39c12; font-weight: 700; font-size: 0.8rem; }
    .demand-low    { color: #e74c3c; font-weight: 700; font-size: 0.8rem; }

    .resource-card {
        display: flex;
        align-items: flex-start;
        gap: 12px;
        border: 1px solid #eee;
        border-radius: 10px;
        padding: 0.9rem;
        margin-bottom: 0.6rem;
        background: white;
    }
    .resource-type-badge {
        background: #667eea;
        color: white;
        border-radius: 8px;
        padding: 3px 10px;
        font-size: 0.7rem;
        font-weight: 700;
        white-space: nowrap;
    }
    .free-badge   { background: #27ae60; }
    .paid-badge   { background: #e67e22; }

    .month-step {
        display: flex;
        gap: 16px;
        margin-bottom: 1rem;
        align-items: flex-start;
    }
    .month-circle {
        min-width: 44px; height: 44px;
        border-radius: 50%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .month-content { flex: 1; }
    .month-title { font-weight: 700; color: #1a1a2e; margin-bottom: 2px; }
    .month-desc  { font-size: 0.85rem; color: #666; line-height: 1.5; }

    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        font-family: 'Sora', sans-serif;
        cursor: pointer;
        transition: opacity 0.2s;
    }
    .stButton > button:hover { opacity: 0.88; }

    .history-card {
        border: 1px solid #e8e8f0;
        border-radius: 10px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.6rem;
        background: white;
        cursor: pointer;
    }
    .history-card:hover { border-color: #667eea; }
</style>
""", unsafe_allow_html=True)


# ─── HELPER FUNCTIONS ─────────────────────────────────────────────────────────

def call_api_generate(payload: dict) -> dict | None:
    """Send POST request to FastAPI to generate a roadmap."""
    try:
        base = st.session_state.get("API_BASE_URL", API_BASE_URL)
        response = requests.post(url=f"{base}/api/roadmap", json=payload, timeout=90)
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Backend error {response.status_code}: {response.text}")
            return None
    except requests.exceptions.ConnectionError:
        st.error(
            "Cannot connect to backend!\n\n"
            "Make sure FastAPI is running:\n"
            "`cd backend && uvicorn main:app --reload`"
        )
        return None
    except requests.exceptions.Timeout:
        st.error("AI is taking too long. Please try again.")
        return None


def call_api_history() -> list:
    """GET all saved roadmaps from the database."""
    try:
        base = st.session_state.get("API_BASE_URL", API_BASE_URL)
        response = requests.get(f"{base}/api/roadmaps", timeout=10)
        return response.json() if response.status_code == 200 else []
    except Exception:
        return []


def check_backend_status() -> bool:
    """Check if FastAPI backend is running."""
    try:
        base = st.session_state.get("API_BASE_URL", API_BASE_URL)
        r = requests.get(f"{base}/", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


# ─── VISUALIZATION FUNCTIONS ──────────────────────────────────────────────────

def render_mind_map(mind_map: dict):
    """Create an interactive mind map using Plotly."""
    if not mind_map or "branches" not in mind_map:
        st.info("Mind map data not available.")
        return

    center = mind_map.get("center", "Career Goal")
    branches = mind_map.get("branches", [])

    nodes_x, nodes_y, node_text, node_colors, node_sizes = [], [], [], [], []
    edge_x, edge_y = [], []

    # Center node
    nodes_x.append(0); nodes_y.append(0)
    node_text.append(f"<b>{center}</b>")
    node_colors.append("#667eea"); node_sizes.append(40)

    import math
    for i, branch in enumerate(branches):
        angle = (2 * math.pi * i) / len(branches)
        bx = 2.5 * math.cos(angle); by = 2.5 * math.sin(angle)
        color = branch.get("color", "#764ba2")

        # Branch node
        nodes_x.append(bx); nodes_y.append(by)
        node_text.append(f"<b>{branch['name']}</b>")
        node_colors.append(color); node_sizes.append(28)

        # Edge: center → branch
        edge_x += [0, bx, None]; edge_y += [0, by, None]

        # Children
        children = branch.get("children", [])
        for j, child in enumerate(children):
            spread = 0.8
            child_angle = angle + spread * (j - len(children)/2 + 0.5) / max(len(children), 1)
            cx = bx + 1.8 * math.cos(child_angle)
            cy = by + 1.8 * math.sin(child_angle)

            nodes_x.append(cx); nodes_y.append(cy)
            priority = child.get("priority", "medium")
            p_color = {"high": "#e74c3c", "medium": "#f39c12", "low": "#27ae60"}.get(priority, "#888")
            node_text.append(child["name"])
            node_colors.append(p_color); node_sizes.append(18)

            edge_x += [bx, cx, None]; edge_y += [by, cy, None]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=1.5, color="#ccccee"),
        hoverinfo="none"
    ))
    fig.add_trace(go.Scatter(
        x=nodes_x, y=nodes_y,
        mode="markers+text",
        text=node_text,
        textposition="top center",
        hoverinfo="text",
        marker=dict(size=node_sizes, color=node_colors, line=dict(width=2, color="white")),
        textfont=dict(size=10, family="Sora, sans-serif")
    ))
    fig.update_layout(
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=500,
        margin=dict(l=20, r=20, t=20, b=20),
        font=dict(family="Sora, sans-serif")
    )
    st.plotly_chart(fig, use_container_width=True)


def render_job_demand_chart(job_prediction: dict):
    """Bar chart of job demand scores."""
    jobs = job_prediction.get("top_jobs", [])
    if not jobs:
        return

    demand_map = {"High": 90, "Medium": 60, "Low": 30}
    titles   = [j["title"][:30] for j in jobs]
    scores   = [demand_map.get(j.get("demand", "Medium"), 60) for j in jobs]
    salaries = [j.get("avg_salary_lpa", "N/A") for j in jobs]
    colors   = ["#27ae60" if s >= 80 else "#f39c12" if s >= 50 else "#e74c3c" for s in scores]

    fig = go.Figure(go.Bar(
        x=scores, y=titles,
        orientation="h",
        marker_color=colors,
        text=[f'{s}% | {sal}' for s, sal in zip(scores, salaries)],
        textposition="inside",
        textfont=dict(color="white", size=11, family="Sora, sans-serif"),
    ))
    fig.update_layout(
        xaxis=dict(title="Market Demand Score", range=[0, 100]),
        yaxis=dict(title=""),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=320,
        margin=dict(l=10, r=10, t=10, b=30),
        font=dict(family="Sora, sans-serif")
    )
    st.plotly_chart(fig, use_container_width=True)


def render_study_timeline(study_plan: list):
    """Gantt-style timeline chart for study plan."""
    if not study_plan:
        return

    df_data = []
    for step in study_plan:
        month = step.get("month", 1)
        df_data.append({
            "Topic": step.get("topic", f"Month {month}"),
            "Start": f"2025-{month:02d}-01",
            "End":   f"2025-{min(month+1, 12):02d}-01",
            "Hours": step.get("weekly_hours", 8)
        })

    df = pd.DataFrame(df_data)
    fig = px.timeline(
        df, x_start="Start", x_end="End", y="Topic",
        color="Hours", color_continuous_scale="Viridis",
        labels={"Hours": "hrs/week"}
    )
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=max(250, len(study_plan) * 45),
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Sora, sans-serif")
    )
    fig.update_yaxes(autorange="reversed")
    st.plotly_chart(fig, use_container_width=True)


def render_skill_radar(current_skills: list, skill_gaps: list):
    """Radar chart comparing current skills vs gaps."""
    all_topics = (current_skills[:5] + skill_gaps[:5])[:8]
    if len(all_topics) < 3:
        return

    have_scores = [85 if s in current_skills else 15 for s in all_topics]
    need_scores = [85 if s in skill_gaps else 15 for s in all_topics]

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=have_scores, theta=all_topics, fill="toself",
        name="Current Skills", fillcolor="rgba(39,174,96,0.25)", line=dict(color="#27ae60", width=2)))
    fig.add_trace(go.Scatterpolar(r=need_scores, theta=all_topics, fill="toself",
        name="Skills to Gain", fillcolor="rgba(231,76,60,0.2)", line=dict(color="#e74c3c", width=2, dash="dash")))
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        height=380,
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=40, r=40, t=20, b=20),
        font=dict(family="Sora, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=-0.15)
    )
    st.plotly_chart(fig, use_container_width=True)


# ─── MAIN APP ─────────────────────────────────────────────────────────────────

def main():
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🎯 AI Career Roadmap Generator</h1>
        <p>Personalized roadmaps · Skill gap analysis · Job market prediction · Mind maps</p>
    </div>
    """, unsafe_allow_html=True)

    # Backend status indicator
    backend_ok = check_backend_status()
    if backend_ok:
        st.success("✅ Backend connected — Ready to generate roadmaps!")
    else:
        st.error(
            "⚠️ FastAPI backend not running. Open a terminal and run:\n\n"
            "```\ncd backend\nuvicorn main:app --reload\n```"
        )

    # ── SIDEBAR: Input Form ────────────────────────────────────────────────────
    with st.sidebar:
        st.markdown("### 📝 Your Profile")
        st.markdown("---")

        # Backend URL override (allows using a different backend address)
        if "API_BASE_URL" not in st.session_state:
            st.session_state["API_BASE_URL"] = API_BASE_URL
        st.markdown("### 🔗 Backend")
        st.text_input("Backend URL", key="API_BASE_URL", help="Override the backend base URL (e.g. http://localhost:8000)")
        st.markdown("---")

        name = st.text_input("👤 Your Name", placeholder="e.g. Arjun Kumar")

        student_class = st.selectbox("🎓 Your Class / Year", [
            "10th Grade", "11th Grade", "12th Grade",
            "B.Tech / BE 1st Year", "B.Tech / BE 2nd Year",
            "B.Tech / BE 3rd Year", "B.Tech / BE 4th Year",
            "BCA 1st Year", "BCA 2nd Year", "BCA 3rd Year",
            "B.Sc CS / IT", "MBA / MCA", "Diploma",
            "Working Professional", "Other"
        ])

        target_role = st.selectbox("🎯 Target Career Role", [
            "Data Scientist", "Machine Learning Engineer",
            "Full Stack Developer", "Backend Developer",
            "Frontend Developer", "DevOps Engineer",
            "Cloud Architect", "Cybersecurity Analyst",
            "AI/ML Researcher", "Data Analyst",
            "Product Manager", "UI/UX Designer",
            "Blockchain Developer", "Game Developer",
            "Mobile App Developer (Android/iOS)"
        ])

        st.markdown("**💡 Current Skills** (select all that apply)")
        skill_options = [
            "Python", "Java", "C/C++", "JavaScript", "HTML/CSS",
            "SQL", "Excel", "R", "MATLAB",
            "Machine Learning basics", "Deep Learning",
            "Git/GitHub", "Linux", "Docker",
            "Statistics", "Mathematics", "Data Structures",
            "Communication", "Problem Solving"
        ]
        current_skills = st.multiselect("", skill_options, label_visibility="collapsed")

        st.markdown("**⭐ Interests** (select your areas)")
        interest_options = [
            "Artificial Intelligence", "Data Analysis",
            "Web Development", "Mobile Development",
            "Cloud Computing", "Cybersecurity",
            "Game Development", "Blockchain",
            "Research & Innovation", "Entrepreneurship",
            "Open Source", "Competitive Programming"
        ]
        interests = st.multiselect("Interests", interest_options, label_visibility="collapsed")

        st.markdown("---")
        generate_btn = st.button("🚀 Generate My Roadmap", disabled=not backend_ok)

        st.markdown("---")
        st.markdown("### 📂 Past Roadmaps")
        if st.button("🔄 Load History"):
            st.session_state["history"] = call_api_history()

        if "history" in st.session_state:
            history = st.session_state["history"]
            if history:
                for item in history[:5]:
                    date = item.get("created_at", "")[:10]
                    if st.button(
                        f"📌 {item['name']} → {item['target_role']} ({date})",
                        key=f"hist_{item['id']}"
                    ):
                        st.session_state["roadmap"] = item
                        st.rerun()
            else:
                st.caption("No saved roadmaps yet.")

    # ── GENERATE ROADMAP ──────────────────────────────────────────────────────
    if generate_btn:
        if not name.strip():
            st.warning("Please enter your name.")
            return
        if not current_skills and not interests:
            st.warning("Please select at least some skills or interests.")
            return

        with st.spinner("🤖 Claude AI is building your personalized roadmap... (this takes 20-40 seconds)"):
            payload = {
                "name": name.strip(),
                "student_class": student_class,
                "target_role": target_role,
                "current_skills": current_skills,
                "interests": interests
            }
            result = call_api_generate(payload)
            if result:
                st.session_state["roadmap"] = result
                st.success(f"✅ Roadmap generated for {name}!")

    # ── DISPLAY ROADMAP ───────────────────────────────────────────────────────
    if "roadmap" in st.session_state:
        data = st.session_state["roadmap"]
        render_roadmap(data)
    else:
        # Landing state
        st.markdown("---")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("### 🧠 AI-Powered\nClaude AI analyzes your profile and current job market data to create a custom roadmap.")
        with c2:
            st.markdown("### 🗺️ Mind Map\nVisual mind map showing all skills, tools, projects, and certifications needed.")
        with c3:
            st.markdown("### 📊 Job Prediction\nFuture job demand analysis, salary ranges, and top companies for your target role.")


def render_roadmap(data: dict):
    """Render the complete roadmap after generation."""
    st.markdown("---")
    name        = data.get("name", "Student")
    target      = data.get("target_role", "")
    est_months  = data.get("estimated_months", 6)
    skill_gaps  = data.get("skill_gaps", [])
    curr_skills = data.get("current_skills", [])
    study_plan  = data.get("study_plan", [])
    mind_map    = data.get("mind_map", {})
    job_pred    = data.get("job_prediction", {})
    resources   = data.get("resources", [])

    # ── Summary stats row ─────────────────────────────────────────────────────
    st.markdown(f"## 🎯 {name}'s Career Roadmap → {target}")
    s1, s2, s3, s4 = st.columns(4)
    with s1:
        st.markdown(f"""<div class="stat-box"><div class="num">{est_months}</div>
        <div class="lbl">Months to Goal</div></div>""", unsafe_allow_html=True)
    with s2:
        st.markdown(f"""<div class="stat-box"><div class="num">{len(skill_gaps)}</div>
        <div class="lbl">Skills to Learn</div></div>""", unsafe_allow_html=True)
    with s3:
        top_jobs = job_pred.get("top_jobs", [])
        salary = top_jobs[0].get("avg_salary_lpa", "—") if top_jobs else "—"
        st.markdown(f"""<div class="stat-box"><div class="num" style="font-size:1.3rem">{salary}</div>
        <div class="lbl">Starting Salary</div></div>""", unsafe_allow_html=True)
    with s4:
        demand = job_pred.get("demand_score", "—")
        st.markdown(f"""<div class="stat-box"><div class="num">{demand}/10</div>
        <div class="lbl">Market Demand</div></div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── TAB LAYOUT ────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🗺️ Mind Map", "📊 Skill Analysis", "📅 Study Plan", "💼 Job Market", "📚 Resources"
    ])

    # TAB 1: Mind Map
    with tab1:
        st.markdown("### 🗺️ Career Mind Map")
        st.caption("Visual overview of all skills, tools, certifications and domains for your target role.")
        render_mind_map(mind_map)

        # Branch legend
        branches = mind_map.get("branches", [])
        if branches:
            cols = st.columns(min(len(branches), 3))
            for i, branch in enumerate(branches):
                with cols[i % 3]:
                    children = branch.get("children", [])
                    st.markdown(f"**{branch['name']}**")
                    for child in children:
                        priority = child.get("priority", "medium")
                        dot = "🔴" if priority == "high" else "🟡" if priority == "medium" else "🟢"
                        st.caption(f"{dot} {child['name']}")

    # TAB 2: Skill Analysis
    with tab2:
        st.markdown("### 📊 Skill Gap Analysis")
        col_a, col_b = st.columns([1, 1])

        with col_a:
            st.markdown("**✅ Skills You Have**")
            if curr_skills:
                tags = "".join([f'<span class="skill-have-tag">✓ {s}</span>' for s in curr_skills])
                st.markdown(tags, unsafe_allow_html=True)
            else:
                st.caption("No skills selected.")

            st.markdown("<br>**❌ Skills You Need to Learn**", unsafe_allow_html=True)
            if skill_gaps:
                tags = "".join([f'<span class="skill-gap-tag">+ {s}</span>' for s in skill_gaps])
                st.markdown(tags, unsafe_allow_html=True)

        with col_b:
            st.markdown("**📡 Skill Radar Chart**")
            render_skill_radar(curr_skills, skill_gaps)

    # TAB 3: Study Plan
    with tab3:
        st.markdown("### 📅 Month-by-Month Study Plan")
        if study_plan:
            st.markdown("**📆 Timeline View**")
            render_study_timeline(study_plan)
            st.markdown("---")
            st.markdown("**📋 Detailed Month-by-Month Breakdown**")
            for step in study_plan:
                month = step.get("month", "?")
                topic = step.get("topic", "")
                desc  = step.get("description", "")
                hours = step.get("weekly_hours", 8)
                milestones = step.get("milestones", [])
                tools = step.get("tools", [])

                with st.expander(f"Month {month}: {topic} — {hours} hrs/week"):
                    st.markdown(f"**What to study:** {desc}")
                    if milestones:
                        st.markdown("**Milestones:**")
                        for m in milestones:
                            st.markdown(f"  - ✅ {m}")
                    if tools:
                        st.markdown(f"**Tools/Platforms:** {', '.join(tools)}")
        else:
            st.info("Study plan not available.")

    # TAB 4: Job Market
    with tab4:
        st.markdown("### 💼 Future Job Market Analysis")
        
        # Market outlook
        outlook = job_pred.get("market_outlook", "")
        if outlook:
            st.info(f"📈 **Market Outlook:** {outlook}")

        col_j1, col_j2 = st.columns([1.2, 1])
        with col_j1:
            st.markdown("**🏆 Top Job Opportunities**")
            render_job_demand_chart(job_pred)

        with col_j2:
            st.markdown("**📌 Key Insights**")
            future = job_pred.get("future_trend", "")
            if future:
                st.markdown(f"**5-Year Trend:** {future}")
            sectors = job_pred.get("best_sectors", [])
            if sectors:
                st.markdown(f"**Top Sectors:** {', '.join(sectors)}")
            salary_growth = job_pred.get("salary_growth", "")
            if salary_growth:
                st.markdown(f"**Salary Growth:** {salary_growth}")

        # Job cards
        st.markdown("**💼 Role Details**")
        for job in job_pred.get("top_jobs", []):
            demand = job.get("demand", "Medium")
            demand_cls = f"demand-{demand.lower()}"
            companies = ", ".join(job.get("top_companies", []))
            skills_needed = ", ".join(job.get("skills_needed", []))
            st.markdown(f"""
            <div class="job-card">
                <div class="job-title">{job.get('title','')}</div>
                <div class="job-salary">💰 {job.get('avg_salary_lpa','N/A')} &nbsp;|&nbsp;
                     <span class="{demand_cls}">▲ {demand} Demand</span> &nbsp;|&nbsp;
                     📈 {job.get('growth_rate','N/A')} growth</div>
                {"<div style='font-size:0.8rem;color:#555;margin-top:4px'>🏢 " + companies + "</div>" if companies else ""}
                {"<div style='font-size:0.8rem;color:#888;margin-top:2px'>🔧 " + skills_needed + "</div>" if skills_needed else ""}
            </div>
            """, unsafe_allow_html=True)

    # TAB 5: Resources
    with tab5:
        st.markdown("### 📚 Curated Learning Resources")
        
        free_res = [r for r in resources if r.get("cost", "").lower() == "free"]
        paid_res = [r for r in resources if r.get("cost", "").lower() != "free"]

        if free_res:
            st.markdown("**🆓 Free Resources**")
            for res in free_res:
                url  = res.get("url", "#")
                name = res.get("name", "Resource")
                rtype = res.get("type", "Course")
                dur  = res.get("duration", "")
                desc = res.get("description", "")
                st.markdown(f"""
                <div class="resource-card">
                    <span class="resource-type-badge free-badge">{rtype}</span>
                    <div>
                        <a href="{url}" target="_blank" style="font-weight:700;color:#1a1a2e;text-decoration:none">
                            {name} ↗
                        </a>
                        {"<span style='font-size:0.8rem;color:#888;margin-left:8px'>" + dur + "</span>" if dur else ""}
                        {"<div style='font-size:0.82rem;color:#666;margin-top:3px'>" + desc + "</div>" if desc else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)

        if paid_res:
            st.markdown("**💳 Paid / Premium Resources**")
            for res in paid_res:
                url  = res.get("url", "#")
                name = res.get("name", "Resource")
                rtype = res.get("type", "Course")
                dur  = res.get("duration", "")
                desc = res.get("description", "")
                st.markdown(f"""
                <div class="resource-card">
                    <span class="resource-type-badge paid-badge">{rtype}</span>
                    <div>
                        <a href="{url}" target="_blank" style="font-weight:700;color:#1a1a2e;text-decoration:none">
                            {name} ↗
                        </a>
                        {"<span style='font-size:0.8rem;color:#888;margin-left:8px'>" + dur + "</span>" if dur else ""}
                        {"<div style='font-size:0.82rem;color:#666;margin-top:3px'>" + desc + "</div>" if desc else ""}
                    </div>
                </div>
                """, unsafe_allow_html=True)

    # ── Export ────────────────────────────────────────────────────────────────
    st.markdown("---")
    st.download_button(
        label="📥 Download Roadmap as JSON",
        data=json.dumps(data, indent=2, default=str),
        file_name=f"roadmap_{data.get('name','student')}_{target_role_slug(target)}.json",
        mime="application/json"
    )


def target_role_slug(role: str) -> str:
    return role.lower().replace(" ", "_").replace("/", "_")


# ─── ENTRY POINT ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    main()
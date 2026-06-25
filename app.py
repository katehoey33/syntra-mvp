import streamlit as st
import pandas as pd
from datetime import datetime
import os
import io
import json
import re
import html
from openai import OpenAI

try:
    from pypdf import PdfReader
except Exception:
    PdfReader = None

st.set_page_config(
    page_title="SYNTRA",
    page_icon="🎓",
    layout="wide"
)

st.markdown(
    """
    <style>
    :root {
        --nyu-purple: #57068c;
        --nyu-purple-dark: #330662;
        --nyu-purple-light: #8f4bb8;
        --card-white: #ffffff;
        --card-soft: #f8f6fb;
        --text-dark: #222222;
        --text-muted: #666666;
        --border-soft: #e6e0ec;
        --success-soft: #e9f7ef;
        --success-text: #1f6f43;
        --info-soft: #eef5ff;
        --info-text: #1f4f82;
        --warning-soft: #fff7e6;
        --warning-text: #8a5a00;
    }

    html, body, [class*="css"] {
        font-family: "Inter", "Helvetica Neue", Arial, sans-serif;
    }

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
        max-width: 1200px;
    }

    .topbar {
        background: #ffffff;
        border: 1px solid var(--border-soft);
        border-radius: 18px;
        padding: 0.9rem 1.2rem;
        margin-bottom: 1.2rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 8px 24px rgba(87, 6, 140, 0.08);
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .brand-badge {
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, var(--nyu-purple), var(--nyu-purple-light));
        border-radius: 12px;
        color: white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 1.1rem;
    }

    .brand-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: var(--text-dark);
        margin-bottom: 0.1rem;
    }

    .brand-subtitle {
        font-size: 0.82rem;
        color: var(--text-muted);
    }

    .topbar-status {
        background: var(--card-soft);
        border: 1px solid var(--border-soft);
        padding: 0.55rem 0.85rem;
        border-radius: 999px;
        color: var(--nyu-purple);
        font-weight: 700;
        font-size: 0.85rem;
    }

    .hero {
        background:
            radial-gradient(circle at top right, rgba(255,255,255,0.28), transparent 28%),
            linear-gradient(135deg, var(--nyu-purple-dark) 0%, var(--nyu-purple) 48%, var(--nyu-purple-light) 100%);
        padding: 2.2rem;
        border-radius: 24px;
        color: white;
        margin-bottom: 1.4rem;
        box-shadow: 0 14px 36px rgba(87, 6, 140, 0.28);
    }

    .hero h1 {
        color: white;
        font-size: 2.4rem;
        margin-bottom: 0.35rem;
        letter-spacing: -0.03em;
    }

    .hero p {
        color: rgba(255,255,255,0.92);
        font-size: 1rem;
        margin-bottom: 0;
    }

    .section-card, .data-card, .guardrail-card, .ai-card {
        background: #ffffff;
        border: 1px solid var(--border-soft);
        border-radius: 18px;
        padding: 1.25rem;
        margin-bottom: 1.2rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.05);
        color: var(--text-dark);
    }

    .section-card h3, .data-card h4, .guardrail-card h4, .ai-card h4 {
        color: var(--nyu-purple);
        margin-top: 0;
    }

    .section-card p, .data-card p, .guardrail-card p, .ai-card p {
        color: var(--text-dark);
        line-height: 1.55;
    }

    .ai-card {
        background: linear-gradient(180deg, #ffffff, #f9f5fc);
        border-radius: 20px;
        box-shadow: 0 10px 28px rgba(87, 6, 140, 0.10);
    }

    .gap-card {
        background: #ffffff;
        border-left: 6px solid var(--nyu-purple);
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.8rem;
        box-shadow: 0 8px 20px rgba(0,0,0,0.05);
        color: var(--text-dark);
    }

    .gap-card h4 {
        color: var(--nyu-purple);
        margin-top: 0;
        margin-bottom: 0.35rem;
    }

    .pill {
        display: inline-block;
        background: var(--card-soft);
        border: 1px solid var(--border-soft);
        color: var(--nyu-purple);
        padding: 0.45rem 0.7rem;
        border-radius: 999px;
        font-size: 0.85rem;
        font-weight: 700;
        margin: 0.2rem 0.25rem 0.2rem 0;
    }

    .success-box {
        background: var(--success-soft);
        color: var(--success-text);
        border: 1px solid #b9e6c9;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin: 0.75rem 0;
        font-weight: 650;
    }

    .info-box {
        background: var(--info-soft);
        color: var(--info-text);
        border: 1px solid #c9dcf5;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin: 0.75rem 0;
    }

    .warning-box {
        background: var(--warning-soft);
        color: var(--warning-text);
        border: 1px solid #f1d08b;
        border-radius: 14px;
        padding: 0.9rem 1rem;
        margin: 0.75rem 0;
        font-weight: 650;
    }

    div.stButton > button:first-child {
        background: linear-gradient(135deg, var(--nyu-purple), var(--nyu-purple-light));
        color: white;
        border-radius: 12px;
        border: none;
        padding: 0.7rem 1.05rem;
        font-weight: 750;
        box-shadow: 0 8px 18px rgba(87, 6, 140, 0.22);
    }

    div.stButton > button:first-child:hover {
        background: linear-gradient(135deg, var(--nyu-purple-dark), var(--nyu-purple));
        color: white;
        border: none;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: #ffffff;
        border: 1px solid var(--border-soft);
        padding: 0.45rem;
        border-radius: 16px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.04);
        margin-bottom: 1.2rem;
    }

    .stTabs [data-baseweb="tab"] {
        height: 48px;
        border-radius: 12px;
        padding: 0 1.2rem;
        font-weight: 750;
        color: var(--text-muted);
    }

    .stTabs [aria-selected="true"] {
        background: var(--nyu-purple);
        color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)


@st.cache_data
def load_mock_course_evidence():
    data = [
        ["S001", 1, "The People Factor — You", "Identify personal barriers to change and connect them to leadership behaviors.", "Learning Journal 1", 99, "Clear grasp of the framework and thoughtful reflection.", "I feel confident explaining The People Factor — You and using it in a class discussion.", "Comprehension", 5.0, "Visual", 3.7, "Ask students to connect the concept to a current workplace example.", "2026-09-08 15:30"],
        ["S001", 2, "The People Factor — Everyone Else", "Understand individual and team resistance to change using empathy and vulnerability concepts.", "Learning Journal 2", 94, "Strong understanding of the core concept and clear connection to course materials.", "I understand The People Factor — Everyone Else and can connect it to situations I have seen in work or school.", "Comprehension", 4.9, "Visual", 2.6, "Use these students as peer discussion leaders in breakout groups.", "2026-09-15 21:45"],
        ["S001", 3, "What to Do About People?", "Assess people-related change challenges and compare leadership approaches.", "Learning Journal 3", 83, "Good understanding but application needs improvement.", "I can explain What to Do About People?, but turning it into a recommendation is still difficult.", "Applied Transfer Difficulty", 4.6, "Visual", 3.7, "Model one full example from theory to business recommendation.", "2026-09-22 10:30"],
        ["S002", 1, "The People Factor — You", "Identify personal barriers to change and connect them to leadership behaviors.", "Learning Journal 1", 78, "Reflection shows effort, but needs clearer connection to leadership behaviors.", "I understand parts of the people factor, but I am not sure how to connect it to leadership decisions.", "Applied Transfer Difficulty", 3.2, "Reading/Writing", 3.4, "Provide an example connecting self-awareness to a leadership action.", "2026-09-08 16:10"],
        ["S002", 2, "The People Factor — Everyone Else", "Understand individual and team resistance to change using empathy and vulnerability concepts.", "Learning Journal 2", 74, "Feedback suggests confusion around resistance and vulnerability concepts.", "I am confused about how empathy and vulnerability actually reduce resistance to change.", "Confusion", 2.8, "Discussion", 3.1, "Review resistance concepts using a simple team scenario.", "2026-09-15 13:20"],
        ["S002", 3, "What to Do About People?", "Assess people-related change challenges and compare leadership approaches.", "Learning Journal 3", 81, "Student understands the challenge but needs stronger evidence in recommendations.", "I can identify people challenges, but I need help choosing which leadership approach fits best.", "Applied Transfer Difficulty", 3.6, "Visual", 3.9, "Add a comparison chart of leadership approaches.", "2026-09-22 18:05"],
        ["S003", 4, "Live Client: People & Change", "Apply people and change concepts to a live client context.", "Client Project 1", 72, "Client recommendation lacks specificity and does not fully connect to the course framework.", "The live client project helped, but I was not sure which framework to use in the recommendation.", "Applied Transfer Difficulty", 3.0, "Kinesthetic", 4.2, "Walk through one sample client recommendation in class.", "2026-09-29 20:30"],
        ["S004", 5, "The Anatomy of Change", "Describe major phases of organizational change and identify common failure points.", "Learning Journal 5", 68, "Student appears to confuse change phases and implementation barriers.", "I am still confused about the difference between the phases of change and why change efforts fail.", "Confusion", 2.4, "Reading/Writing", 3.5, "Revisit the change phases with a timeline example.", "2026-10-06 14:45"],
        ["S005", 6, "Applying Change Frameworks", "Apply structured change frameworks to organizational problems.", "Learning Journal 6", 76, "Adequate summary of the framework, but application to the case is limited.", "I understand the framework in theory, but applying it to a messy organization is hard.", "Applied Transfer Difficulty", 3.1, "Discussion", 4.0, "Use a short case exercise to practice framework selection.", "2026-10-13 12:15"],
        ["S006", 7, "Leading Change in Organizations", "Evaluate leadership practices that support successful change implementation.", "Learning Journal 7", 88, "Strong explanation of leadership practices and good applied example.", "I feel comfortable explaining how leaders can support change and reduce uncertainty.", "Comprehension", 4.4, "Visual", 4.3, "Use student examples to reinforce effective leadership practices.", "2026-10-20 09:30"],
        ["S007", 8, "Live Client: Managing Change in Startups", "Analyze change management challenges in startup environments.", "Client Project 2", 71, "Recommendation identifies startup challenges but lacks connection to change management theory.", "The startup example made sense, but I struggled connecting it to formal change management concepts.", "Applied Transfer Difficulty", 3.0, "Kinesthetic", 4.4, "Provide a startup-specific change framework example.", "2026-10-27 17:45"],
        ["S008", 9, "The Anatomy of Innovation", "Describe innovation types and explain how innovation differs from change.", "Learning Journal 9", 70, "Student confuses innovation process with general change process.", "I am confused about the difference between innovation and change because they sound similar.", "Confusion", 2.6, "Reading/Writing", 3.8, "Create a side-by-side comparison of innovation and change.", "2026-11-03 21:10"],
        ["S009", 10, "Innovation Process & Strategy", "Analyze innovation processes and connect them to organizational strategy.", "Learning Journal 10", 82, "Good strategic thinking, but needs clearer link to process stages.", "I understand innovation strategy, but I am not fully sure how the process stages connect.", "Applied Transfer Difficulty", 3.7, "Discussion", 4.1, "Review innovation process stages using a business example.", "2026-11-10 11:00"],
        ["S010", 11, "Building the Innovative Organization", "Identify structures and cultures that support organizational innovation.", "Learning Journal 11", 91, "Strong grasp of organizational culture and innovation support systems.", "I understand how culture, structure, and incentives can make innovation easier.", "Comprehension", 4.7, "Visual", 4.5, "Invite students to compare innovative and non-innovative organizations.", "2026-11-17 15:20"],
        ["S011", 12, "Innovation in Action", "Apply innovation concepts to a real-world organizational example.", "Learning Journal 12", 79, "Application is developing, but example needs more evidence.", "I can identify innovation, but I need more practice supporting my analysis with evidence.", "Support Need", 3.3, "Reading/Writing", 4.0, "Provide a checklist for evidence-based innovation analysis.", "2026-11-24 19:00"],
        ["S012", 13, "Driving Innovation", "Develop recommendations for sustaining innovation over time.", "Client Project 3", 73, "Recommendation is promising but lacks implementation detail.", "I know what innovation recommendation I want to make, but I am unsure how to make it actionable.", "Support Need", 3.2, "Kinesthetic", 4.6, "Provide a template for actionable innovation recommendations.", "2026-12-01 16:30"],
        ["S013", 14, "Synthesis & Reflection", "Synthesize change and innovation concepts into a final course reflection.", "Final Reflection", 93, "Strong synthesis across course themes and thoughtful reflection.", "I can now connect change and innovation concepts and explain why both matter.", "Comprehension", 4.8, "Discussion", 4.7, "Use synthesis examples to model strong final reflections.", "2026-12-08 10:10"],
        ["S014", 6, "Applying Change Frameworks", "Apply structured change frameworks to organizational problems.", "Learning Journal 6", 62, "Student is struggling to distinguish frameworks and apply them appropriately.", "The different change frameworks are hard to keep straight, and I do not know when to use each one.", "Confusion", 2.1, "Visual", 3.2, "Add a framework selection decision tree.", "2026-10-13 13:50"],
        ["S015", 10, "Innovation Process & Strategy", "Analyze innovation processes and connect them to organizational strategy.", "Learning Journal 10", 67, "Reflection suggests pacing concerns and incomplete understanding of process stages.", "This topic moved too fast for me. I need more time with the innovation process steps.", "Pacing Concern", 2.3, "Reading/Writing", 3.6, "Slow down process-stage review and add a short recap.", "2026-11-10 20:25"],
        ["S016", 13, "Driving Innovation", "Develop recommendations for sustaining innovation over time.", "Client Project 3", 85, "Good recommendation with room for stronger implementation planning.", "I understand how to drive innovation, but implementation planning is still a little unclear.", "Applied Transfer Difficulty", 3.9, "Discussion", 4.5, "Review implementation planning for innovation recommendations.", "2026-12-01 12:40"],
    ]

    columns = [
        "student_id", "week", "module_topic", "learning_objective", "assignment_name",
        "assignment_grade", "professor_feedback", "reflection_text", "signal_category",
        "confidence_score", "learning_style", "career_relevance_score",
        "suggested_faculty_action", "timestamp"
    ]

    df = pd.DataFrame(data, columns=columns)
    expanded_df = pd.concat([df] * 22, ignore_index=True).head(420)
    expanded_df["student_id"] = [f"ANON-{(i % 30) + 1:03d}" for i in range(len(expanded_df))]
    return expanded_df


def generate_learning_gap_table(df):
    module_summary = (
        df.groupby(["week", "module_topic", "learning_objective"])
        .agg(
            avg_grade=("assignment_grade", "mean"),
            avg_confidence=("confidence_score", "mean"),
            most_common_signal=("signal_category", lambda x: x.mode().iloc[0]),
            records=("student_id", "count"),
        )
        .reset_index()
    )

    risk_modules = module_summary[
        (module_summary["avg_grade"] < 80)
        | (module_summary["avg_confidence"] < 3.5)
        | (module_summary["most_common_signal"].isin(["Confusion", "Applied Transfer Difficulty", "Support Need", "Pacing Concern"]))
    ].copy()

    risk_modules = risk_modules.sort_values(
        by=["avg_confidence", "avg_grade"],
        ascending=[True, True]
    ).head(6)

    rows = []
    for _, row in risk_modules.iterrows():
        signal = row["most_common_signal"]

        if signal == "Confusion":
            gap = "Students show signs of conceptual confusion and may need clarification before moving forward."
            action = "Revisit the core concept using a short example, comparison chart, or guided class discussion."
        elif signal == "Applied Transfer Difficulty":
            gap = "Students understand the concept in theory but struggle to apply it to realistic organizational situations."
            action = "Add a worked example that connects the framework to a client or workplace scenario."
        elif signal == "Support Need":
            gap = "Students appear to need more structure, examples, or evidence-building support."
            action = "Provide a checklist, template, or model response before the next assignment."
        elif signal == "Pacing Concern":
            gap = "Students indicate that the topic may be moving too quickly for confident understanding."
            action = "Slow down the next class segment and add a brief recap or review activity."
        else:
            gap = "Students are generally demonstrating comprehension, but continued reinforcement may help."
            action = "Use student examples to reinforce understanding and deepen applied learning."

        rows.append({
            "Week": int(row["week"]),
            "Module": row["module_topic"],
            "Learning Outcome": row["learning_objective"],
            "Evidence Pattern": f"Avg grade: {row['avg_grade']:.1f}%, Avg confidence: {row['avg_confidence']:.1f}/5, Signal: {signal}",
            "Learning Gap Detected": gap,
            "Suggested Faculty Action": action
        })

    return pd.DataFrame(rows)


def get_top_faculty_actions(df):
    action_counts = (
        df["suggested_faculty_action"]
        .value_counts()
        .head(5)
        .reset_index()
    )
    action_counts.columns = ["Recommended Action", "Supporting Records"]
    return action_counts


# -----------------------------
# Mock Midterm Survey Dataset
# -----------------------------
def load_mock_midterm_feedback():
    questions = [
        ("Q01", "Which course concept has been clearest so far?", "open_text", "Concept Clarity"),
        ("Q02", "Which course concept still feels most unclear?", "open_text", "Concept Confusion"),
        ("Q03", "How confident are you applying change frameworks to real organizations?", "rating_1_5", "Applied Confidence"),
        ("Q04", "How useful are the live client examples for your learning?", "rating_1_5", "Applied Value"),
        ("Q05", "What type of support would help you most before the next client assignment?", "open_text", "Support Need"),
        ("Q06", "How would you describe the course pace so far?", "choice", "Pacing"),
        ("Q07", "Which learning format helps you most in this course?", "choice", "Learning Style"),
        ("Q08", "How relevant does this course feel to your career or academic goals?", "rating_1_5", "Career Relevance"),
        ("Q09", "What would make the change frameworks easier to apply?", "open_text", "Applied Transfer"),
        ("Q10", "What is one suggestion for improving the second half of the course?", "open_text", "Course Improvement"),
    ]

    modules = [
        (1, "The People Factor — You"),
        (2, "The People Factor — Everyone Else"),
        (3, "What to Do About People?"),
        (4, "Live Client: People & Change"),
        (5, "The Anatomy of Change"),
        (6, "Applying Change Frameworks"),
        (7, "Leading Change in Organizations"),
        (8, "Live Client: Managing Change in Startups"),
        (9, "The Anatomy of Innovation"),
        (10, "Innovation Process & Strategy"),
    ]

    response_bank = {
        "Q01": [
            "The people-side barriers to change are clearest to me.",
            "I understand why empathy matters when people resist change.",
            "The change phases make sense when shown as a timeline.",
            "Leadership behaviors that support change have been clear so far.",
        ],
        "Q02": [
            "I am still unclear on when to use each change framework.",
            "The difference between innovation and change is still confusing.",
            "I need more help connecting theory to client recommendations.",
            "The innovation process stages moved quickly for me.",
        ],
        "Q05": [
            "More worked examples before client assignments would help.",
            "A framework selection checklist would be useful.",
            "I would benefit from a comparison chart of the main frameworks.",
            "More time to practice applying concepts in groups would help.",
        ],
        "Q09": [
            "A decision tree for choosing frameworks would help.",
            "Seeing a full example from problem to recommendation would make it easier.",
            "More practice with messy organizational cases would help.",
            "Rubric examples would help me understand what strong application looks like.",
        ],
        "Q10": [
            "Add more short applied cases before major assignments.",
            "Slow down the innovation process module and add a recap.",
            "Use more side-by-side comparisons of similar concepts.",
            "Keep the live client examples but add more scaffolding before them.",
        ],
    }

    pace_choices = ["Too fast", "About right", "Slightly fast", "Uneven across modules"]
    style_choices = ["Worked examples", "Small-group discussion", "Visual diagrams", "Written templates/checklists", "Live client practice"]

    rows = []
    for student_num in range(1, 31):
        student_id = f"ANON-{student_num:03d}"
        for idx, (question_id, question_text, response_type, feedback_theme) in enumerate(questions):
            week, module_topic = modules[idx]

            if response_type == "rating_1_5":
                if question_id == "Q03":
                    response_value = [2, 3, 3, 4, 4][student_num % 5]
                elif question_id == "Q04":
                    response_value = [4, 4, 5, 5, 3][student_num % 5]
                else:
                    response_value = [3, 4, 4, 5, 5][student_num % 5]
                response_text = str(response_value)
            elif response_type == "choice":
                response_value = ""
                if question_id == "Q06":
                    response_text = pace_choices[student_num % len(pace_choices)]
                else:
                    response_text = style_choices[student_num % len(style_choices)]
            else:
                response_value = ""
                choices = response_bank[question_id]
                response_text = choices[student_num % len(choices)]

            if question_id == "Q02":
                learning_signal = "Confusion" if student_num % 2 == 0 else "Applied Transfer Difficulty"
            elif question_id in ["Q03", "Q09"]:
                learning_signal = "Applied Transfer Difficulty"
            elif question_id == "Q06" and response_text in ["Too fast", "Slightly fast"]:
                learning_signal = "Pacing Concern"
            elif question_id in ["Q05", "Q10"]:
                learning_signal = "Support Need"
            else:
                learning_signal = "Comprehension"

            rows.append({
                "response_id": f"MSF-{student_num:03d}-{question_id}",
                "student_id": student_id,
                "survey_period": "Mid-Semester",
                "question_id": question_id,
                "question_text": question_text,
                "response_type": response_type,
                "response_value": response_value,
                "response_text": response_text,
                "feedback_theme": feedback_theme,
                "linked_module_week": week,
                "linked_module_topic": module_topic,
                "learning_signal": learning_signal,
                "timestamp": "2026-10-20",
            })

    return pd.DataFrame(rows)


def summarize_midterm_feedback(survey_df):
    if survey_df is None or survey_df.empty:
        return {}

    theme_counts = survey_df["feedback_theme"].value_counts().to_dict()

    question_summary = []
    for question_id, group in survey_df.groupby("question_id"):
        rating_values = pd.to_numeric(group["response_text"], errors="coerce").dropna()
        rating_summary = None
        if not rating_values.empty:
            rating_summary = {
                "average_response": round(float(rating_values.mean()), 2),
                "min_response": int(rating_values.min()),
                "max_response": int(rating_values.max()),
            }

        question_summary.append({
            "question_id": question_id,
            "question_text": group["question_text"].iloc[0],
            "response_type": group["response_type"].iloc[0],
            "response_count": int(len(group)),
            "feedback_theme": group["feedback_theme"].iloc[0],
            "rating_summary_if_applicable": rating_summary,
            "sample_responses": group["response_text"].head(6).tolist(),
        })

    return {
        "total_responses": int(len(survey_df)),
        "anonymous_students": int(survey_df["student_id"].nunique()),
        "theme_counts": theme_counts,
        "question_summary": question_summary,
    }


# -----------------------------
# Uploaded Course Context Parsing and Matching
# -----------------------------
def extract_uploaded_course_context(uploaded_files, category):
    items = []
    if not uploaded_files:
        return items

    for uploaded_file in uploaded_files:
        file_name = uploaded_file.name
        extension = file_name.split(".")[-1].lower() if "." in file_name else ""
        text = ""
        status = "Filename captured"

        try:
            uploaded_file.seek(0)
            raw_bytes = uploaded_file.read()
            uploaded_file.seek(0)

            if extension in ["txt", "csv"]:
                text = raw_bytes.decode("utf-8", errors="ignore")
                status = "Text extracted"
            elif extension == "pdf":
                if PdfReader is None:
                    status = "PDF uploaded; install pypdf for full text extraction"
                    text = file_name
                else:
                    reader = PdfReader(io.BytesIO(raw_bytes))
                    page_text = []
                    for page in reader.pages[:8]:
                        page_text.append(page.extract_text() or "")
                    text = "\n".join(page_text)
                    status = "PDF text extracted"
            else:
                text = file_name
                status = "File uploaded; filename used for context matching"

        except Exception as e:
            text = file_name
            status = f"Could not extract text; using filename only ({e})"

        items.append({
            "file_name": file_name,
            "category": category,
            "status": status,
            "character_count": len(text),
            "text_excerpt": text[:3000],
        })

    return items


def update_uploaded_course_context(syllabus_file, materials_files, assignments_files):
    context_items = []
    if syllabus_file is not None:
        context_items.extend(extract_uploaded_course_context([syllabus_file], "Syllabus"))
    if materials_files:
        context_items.extend(extract_uploaded_course_context(materials_files, "Learning Material / Module"))
    if assignments_files:
        context_items.extend(extract_uploaded_course_context(assignments_files, "Assignment / Rubric"))

    st.session_state.uploaded_course_context = context_items
    return context_items


def keyword_tokens(text):
    words = re.findall(r"[A-Za-z]{4,}", str(text).lower())
    stopwords = {"this", "that", "with", "from", "into", "using", "course", "student", "students", "learning", "assignment", "module"}
    return set(w for w in words if w not in stopwords)


def generate_context_match_summary(df, context_items):
    if not context_items:
        return []

    full_context_text = " ".join(
        f"{item.get('file_name', '')} {item.get('text_excerpt', '')}" for item in context_items
    ).lower()

    rows = []
    unique_modules = df[["week", "module_topic", "learning_objective", "assignment_name"]].drop_duplicates().head(14)

    for _, row in unique_modules.iterrows():
        module_topic = row["module_topic"]
        learning_objective = row["learning_objective"]
        assignment_name = row["assignment_name"]

        module_tokens = keyword_tokens(module_topic)
        objective_tokens = keyword_tokens(learning_objective)
        assignment_tokens = keyword_tokens(assignment_name)
        all_tokens = module_tokens | objective_tokens | assignment_tokens
        matched_tokens = sorted([token for token in all_tokens if token in full_context_text])

        exact_module_match = str(module_topic).lower() in full_context_text
        exact_assignment_match = str(assignment_name).lower() in full_context_text

        if exact_module_match or exact_assignment_match or len(matched_tokens) >= 4:
            match_strength = "Strong"
        elif len(matched_tokens) >= 2:
            match_strength = "Moderate"
        else:
            match_strength = "Weak"

        rows.append({
            "week": int(row["week"]),
            "module_topic": module_topic,
            "learning_objective": learning_objective,
            "assignment_name": assignment_name,
            "match_strength": match_strength,
            "matched_terms": ", ".join(matched_tokens[:10]) if matched_tokens else "No direct keyword match found",
        })

    return rows


# -----------------------------
# Live AI Intelligence Layer
# -----------------------------
LIVE_AI_AGENT_PROMPT = """
You are the Learning Intelligence Agent for an NYU faculty-facing instructional dashboard.

Your role is to analyze anonymous, class-level course evidence and produce faculty-facing learning intelligence.
You are not a tutor, chatbot, grading assistant, disciplinary tool, student evaluator, or replacement for faculty judgment.

You will receive raw evidence, including:
- Brightspace-style assignment evidence: module, objective, assignment, outcome, professor feedback
- anonymous student reflection excerpts
- anonymous mid-semester survey responses
- uploaded course context excerpts from syllabus, module files, assignments, and rubrics when available
- a deterministic course-context keyword summary

Important interpretation rule:
Do not treat any pre-labeled mock signal, confidence score, or career relevance score as the analysis.
Your job is to infer the learning story from the raw reflections, grades, professor feedback, survey responses, and course context.
If numeric survey responses appear, treat them only as student survey responses, not as final analytics.

Core analysis tasks:
1. Summarize the overall class-level learning story in plain faculty-facing language.
2. Produce module deep dives that explain what is working and where students are struggling in each module.
3. Identify learning gaps as mismatches between professor/course expectations and student evidence.
4. Rank gaps by how often they appear across the evidence, not just by severity.
5. Recommend practical faculty actions that remain under human faculty control.

Responsible AI rules:
1. Do not grade students.
2. Do not rank students.
3. Do not identify individual students.
4. Do not recommend disciplinary action.
5. Do not make high-stakes decisions.
6. Do not infer sensitive personal traits.
7. Keep all findings at the class, module, or learning-outcome level.
8. Treat assignment outcomes as supporting evidence only, not as a basis for judging students.
9. Always include a reminder that the professor remains the final decision-maker.

Return valid JSON only. Do not include markdown.

Use this exact JSON structure:
{
  "executive_summary": "2-3 sentence faculty-facing summary of the main learning story",
  "overall_learning_health": "short phrase, no more than 9 words",
  "headline_findings": [
    {
      "finding": "short finding label",
      "what_it_means": "one sentence explaining what is difficult or working",
      "where_it_shows_up": "modules, assignments, or survey patterns where this appears"
    }
  ],
  "module_deep_dives": [
    {
      "module_or_topic": "string",
      "module_status": "Working, Struggling, Mixed, or Needs Support",
      "what_is_working": "string",
      "where_students_are_struggling": "string",
      "evidence": "string",
      "faculty_adjustment": "string"
    }
  ],
  "learning_gaps": [
    {
      "gap_title": "short gap name",
      "where_it_shows_up": "modules, assignments, or survey responses",
      "professor_expectation": "what students were expected to demonstrate",
      "student_evidence": "what reflections or survey responses suggest",
      "grade_feedback_evidence": "what assignment outcomes or professor comments suggest",
      "frequency_label": "High, Medium, or Low",
      "frequency_count": 0,
      "priority": "High, Medium, or Low",
      "suggested_faculty_action": "string"
    }
  ],
  "recommended_actions": [
    {
      "action_title": "string",
      "action_description": "string",
      "why_it_matters": "string"
    }
  ],
  "chart_explanations": {
    "learning_story": "string",
    "assignment_outcome_by_week": "string",
    "midterm_feedback": "string",
    "gap_frequency": "string"
  },
  "responsible_use_note": "string",
  "limitations": "string"
}
"""


def build_live_ai_payload(df, max_rows=25):
    # Send raw instructional evidence. Avoid precomputed mock analytics fields so the AI has to infer the learning story.
    sample_cols = [
        "week",
        "module_topic",
        "learning_objective",
        "assignment_name",
        "assignment_grade",
        "professor_feedback",
        "reflection_text",
        "suggested_faculty_action",
    ]

    safe_df = df[sample_cols].copy()
    sample_df = safe_df.head(max_rows)

    context_items = st.session_state.get("uploaded_course_context", [])
    survey_df = st.session_state.get("midterm_feedback_df", pd.DataFrame())

    payload = {
        "course_name": "Managing Change and Innovation",
        "semester": "Fall 2026",
        "professor": "Professor Smith",
        "analysis_level": "class-level only",
        "important_note": "The model should infer learning patterns from raw evidence. Do not rely on pre-labeled confidence, relevance, or signal fields.",
        "assignment_and_reflection_records": sample_df.to_dict(orient="records"),
        "uploaded_course_context": context_items,
        "context_keyword_summary": generate_context_match_summary(df, context_items),
        "midterm_survey_summary": summarize_midterm_feedback(survey_df),
    }

    return payload


def run_live_learning_intelligence_agent(df):
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        return {"error": "OPENAI_API_KEY was not found. Check your Replit Secrets."}

    payload = build_live_ai_payload(df)

    try:
        client = OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": LIVE_AI_AGENT_PROMPT},
                {
                    "role": "user",
                    "content": (
                        "Analyze the following anonymous course evidence and return the required JSON structure.\n\n"
                        + json.dumps(payload, indent=2)
                    ),
                },
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )

        raw_output = response.choices[0].message.content.strip()
        return json.loads(raw_output)

    except Exception as e:
        return {"error": f"OpenAI connection failed: {e}"}


# -----------------------------
# Live AI Display Helpers
# -----------------------------
def h(value):
    return html.escape(str(value or ""))


def shorten_text(value, max_chars=420):
    text = str(value or "")
    if len(text) <= max_chars:
        return text
    return text[:max_chars].rsplit(" ", 1)[0] + "..."


def first_nonempty(*values, default="—"):
    for value in values:
        if value not in [None, "", []]:
            return value
    return default


def gap_frequency_chart_from_gaps(gaps):
    if not gaps:
        return pd.DataFrame({"Learning Gap": [], "Frequency": []}).set_index("Learning Gap")

    rows = []
    for index, gap in enumerate(gaps, start=1):
        title = first_nonempty(gap.get("gap_title"), gap.get("module_or_topic"), f"Gap {index}")
        count = gap.get("frequency_count", None)
        if count in [None, ""]:
            label = str(gap.get("frequency_label", "Medium")).lower()
            count = 12 if label == "high" else 7 if label == "medium" else 3
        try:
            count = int(count)
        except Exception:
            count = index
        rows.append({"Learning Gap": shorten_text(title, 42), "Frequency": count})

    chart_df = pd.DataFrame(rows).sort_values("Frequency", ascending=False)
    return chart_df.set_index("Learning Gap")


def survey_readiness_by_week_chart(survey_df):
    if survey_df is None or survey_df.empty:
        return pd.DataFrame()

    working_df = survey_df.copy()
    working_df["numeric_response"] = pd.to_numeric(working_df["response_value"], errors="coerce")

    inferred_readiness = {
        "Comprehension": 4.2,
        "Applied Transfer Difficulty": 2.7,
        "Confusion": 2.3,
        "Pacing Concern": 2.6,
        "Support Need": 3.0,
    }

    working_df["readiness_score"] = working_df.apply(
        lambda row: row["numeric_response"]
        if pd.notna(row["numeric_response"])
        else inferred_readiness.get(row.get("learning_signal"), 3.0),
        axis=1,
    )

    chart_df = (
        working_df.groupby("linked_module_week")["readiness_score"]
        .mean()
        .reset_index()
        .sort_values("linked_module_week")
    )

    chart_df.columns = ["Module Week", "Survey Readiness"]
    return chart_df.set_index("Module Week")


def grade_vs_readiness_chart(df, survey_df):
    grade_df = (
        df.groupby("week")["assignment_grade"]
        .mean()
        .reset_index()
    )
    grade_df.columns = ["Module Week", "Assignment Outcome"]
    grade_df = grade_df.set_index("Module Week")

    readiness_df = survey_readiness_by_week_chart(survey_df)
    if readiness_df.empty:
        return grade_df

    combined = grade_df.join(readiness_df, how="left")
    combined["Survey Readiness"] = combined["Survey Readiness"] * 20
    combined = combined.rename(columns={"Survey Readiness": "Survey Readiness (scaled to %)"})
    combined["Survey Readiness (scaled to %)"] = combined["Survey Readiness (scaled to %)"].interpolate(limit_direction="both")
    return combined


def module_status_chip(status):
    status = str(status or "Mixed")
    normalized = status.lower()
    if "working" in normalized:
        return "Working"
    if "struggling" in normalized:
        return "Struggling"
    if "support" in normalized:
        return "Needs Support"
    return "Mixed"


def action_tags(action_title, action_description=""):
    text = f"{action_title} {action_description}".lower()
    tags = []

    if any(word in text for word in ["framework", "decision", "checklist", "tool"]):
        tags.append("Framework tool")
    if any(word in text for word in ["example", "case", "practice", "worked"]):
        tags.append("Applied practice")
    if any(word in text for word in ["clarify", "distinction", "comparison", "visual"]):
        tags.append("Concept clarity")
    if any(word in text for word in ["pace", "pacing", "recap", "slow"]):
        tags.append("Pacing support")
    if any(word in text for word in ["client", "project"]):
        tags.append("Before client work")

    if not tags:
        tags.append("Instructional support")

    if len(tags) < 3:
        tags.append("High impact")

    return tags[:4]


def render_chip(label):
    st.markdown(f'<span class="pill">{h(label)}</span>', unsafe_allow_html=True)


def render_metric_card(title, value, caption=""):
    st.markdown(
        f"""
        <div class="data-card" style="min-height: 132px; overflow-wrap: anywhere;">
            <h4 style="font-size: 1.05rem; margin-bottom: 0.65rem;">{h(title)}</h4>
            <p style="font-size: 1.35rem; line-height: 1.18; font-weight: 800; margin: 0.2rem 0; color: #57068c;">{h(shorten_text(value, 72))}</p>
            <p style="margin-bottom: 0; color: #555; font-size: 0.92rem; line-height: 1.35;">{h(shorten_text(caption, 95))}</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_compact_action_card(title, description, why_it_matters, tags=None):
    tag_html = ""
    for tag in tags or []:
        tag_html += f'<span class="pill">{h(tag)}</span>'

    st.markdown(
        f"""
        <div class="gap-card">
            <h4>{h(title)}</h4>
            <p>{h(description)}</p>
            <p><strong>Why it matters:</strong> {h(why_it_matters)}</p>
            <div>{tag_html}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

if "brightspace_connected" not in st.session_state:
    st.session_state.brightspace_connected = False

if "last_sync" not in st.session_state:
    st.session_state.last_sync = None

if "course_evidence_loaded" not in st.session_state:
    st.session_state.course_evidence_loaded = False

if "course_evidence_df" not in st.session_state:
    st.session_state.course_evidence_df = pd.DataFrame()

if "ai_summary_generated" not in st.session_state:
    st.session_state.ai_summary_generated = False

if "midterm_feedback_synced" not in st.session_state:
    st.session_state.midterm_feedback_synced = False

if "midterm_feedback_df" not in st.session_state:
    st.session_state.midterm_feedback_df = pd.DataFrame()

if "uploaded_course_context" not in st.session_state:
    st.session_state.uploaded_course_context = []

if "live_ai_report" not in st.session_state:
    st.session_state.live_ai_report = None

if "live_ai_generated" not in st.session_state:
    st.session_state.live_ai_generated = False


def reset_demo():
    st.session_state.brightspace_connected = False
    st.session_state.last_sync = None
    st.session_state.course_evidence_loaded = False
    st.session_state.course_evidence_df = pd.DataFrame()
    st.session_state.ai_summary_generated = False
    st.session_state.midterm_feedback_synced = False
    st.session_state.midterm_feedback_df = pd.DataFrame()
    st.session_state.uploaded_course_context = []
    st.session_state.live_ai_report = None
    st.session_state.live_ai_generated = False
    st.session_state.reset_counter += 1
    st.rerun()


def render_topbar():
    st.markdown(
        """
        <div class="topbar">
            <div class="brand">
                <div class="brand-badge">NYU</div>
                <div>
                    <div class="brand-title">SYNTRA</div>
                    <div class="brand-subtitle">Faculty Dashboard MVP</div>
                </div>
            </div>
            <div class="topbar-status">Professor Smith · Fall 2026</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_hero():
    st.markdown(
        """
        <div class="hero">
            <h1>Welcome Professor Smith!</h1>
            <p>Connect course context, learning evidence, and anonymous feedback to identify class-level learning gaps.</p>
        </div>
        """,
        unsafe_allow_html=True
    )


render_topbar()
render_hero()

reset_col1, reset_col2 = st.columns([5, 1])
with reset_col2:
    if st.button("Reset Demo"):
        reset_demo()


tab_setup, tab_sync, tab_dashboard, tab_live_ai = st.tabs(
    [
        "1. Course Setup",
        "2. Evidence & Feedback Sync",
        "3. Faculty Dashboard",
        "4. Live AI Intelligence Layer"
    ]
)


with tab_setup:
    st.markdown(
        """
        <div class="section-card">
            <h3>Start a New Semester</h3>
            <p>
            Enter the Brightspace course code and connect course materials so the platform can compare
            learning evidence against course goals, learning outcomes, assignments, rubrics, and professor feedback.
            This MVP does not grade, rank, or monitor students. It summarizes class-level learning patterns
            to support instructional decisions.
            </p>
            <span class="pill">Course context</span>
            <span class="pill">Brightspace connector</span>
            <span class="pill">Responsible AI</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    left_col, right_col = st.columns([2, 1], gap="large")

    with left_col:
        st.subheader("Brightspace Course Connector")

        course_code = st.text_input(
            "Enter Brightspace Course Code",
            value="",
            placeholder="Example: MCI-FALL26-001",
            key=f"course_code_{st.session_state.reset_counter}"
        )

        semester = st.selectbox(
            "Semester",
            ["Fall 2026", "Spring 2027", "Summer 2027"],
            key=f"semester_{st.session_state.reset_counter}"
        )

        professor_name = st.text_input(
            "Professor Name",
            value="Professor Smith",
            key=f"professor_name_{st.session_state.reset_counter}"
        )

        course_name = st.text_input(
            "Course Name",
            value="Managing Change and Innovation",
            placeholder="Example: Managing Change and Innovation",
            key=f"course_name_{st.session_state.reset_counter}"
        )

        st.markdown("---")
        st.subheader("Connect Course Materials")

        brightspace_col, sync_col = st.columns([2, 1])

        with brightspace_col:
            st.markdown(
                """
                **Brightspace Connection**

                In the full version, this platform would connect directly to Brightspace using the course code to gather:
                syllabi, assignments, rubrics, grade outputs, professor feedback, and anonymous student feedback.
                """
            )

        with sync_col:
            if st.button("Connect to Brightspace", key=f"connect_btn_{st.session_state.reset_counter}"):
                st.session_state.brightspace_connected = True
                st.session_state.last_sync = datetime.now().strftime("%B %d, %Y at %I:%M %p")

        if st.session_state.brightspace_connected:
            st.markdown(
                f"""
                <div class="success-box">
                Brightspace connected. Last refreshed: {st.session_state.last_sync}
                </div>
                """,
                unsafe_allow_html=True
            )
        else:
            st.warning("Brightspace not connected yet.")

        st.markdown("### Course Context Uploads")
        st.caption("These uploads represent course materials that would be connected through Brightspace in a full implementation.")

        syllabus_file = st.file_uploader(
            "Upload Syllabus",
            type=["pdf", "docx", "txt"],
            key=f"syllabus_file_{st.session_state.reset_counter}"
        )

        if syllabus_file is not None:
            st.markdown(
                f"""
                <div class="success-box">
                Syllabus uploaded successfully: {syllabus_file.name}
                </div>
                <div class="info-box">
                System update: Course name, weekly modules, and course context are now available for comparison.
                </div>
                """,
                unsafe_allow_html=True
            )

        materials_files = st.file_uploader(
            "Upload Learning Materials",
            type=["pdf", "docx", "pptx", "txt", "zip"],
            accept_multiple_files=True,
            key=f"materials_files_{st.session_state.reset_counter}"
        )

        if materials_files:
            uploaded_material_names = [file.name for file in materials_files]

            st.markdown(
                f"""
                <div class="success-box">
                {len(uploaded_material_names)} learning material file(s) uploaded successfully.
                </div>
                <div class="info-box">
                System update: Readings, slides, and instructional materials are now available as course context.
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander("View uploaded learning materials"):
                for file_name in uploaded_material_names:
                    st.markdown(f"✅ {file_name}")

        assignments_files = st.file_uploader(
            "Upload Assignments / Rubrics",
            type=["pdf", "docx", "csv", "xlsx", "zip"],
            accept_multiple_files=True,
            key=f"assignments_files_{st.session_state.reset_counter}"
        )

        if assignments_files:
            uploaded_assignment_names = [file.name for file in assignments_files]

            st.markdown(
                f"""
                <div class="success-box">
                {len(uploaded_assignment_names)} assignment/rubric file(s) uploaded successfully.
                </div>
                <div class="info-box">
                System update: Assignment expectations and rubric criteria are now available for learning gap analysis.
                </div>
                """,
                unsafe_allow_html=True
            )

            with st.expander("View uploaded assignments and rubrics"):
                for file_name in uploaded_assignment_names:
                    st.markdown(f"✅ {file_name}")

        uploaded_context_items = update_uploaded_course_context(syllabus_file, materials_files, assignments_files)
        if uploaded_context_items:
            st.markdown("### Course Context Extraction Status")
            context_status_df = pd.DataFrame([
                {
                    "File": item["file_name"],
                    "Type": item["category"],
                    "Status": item["status"],
                    "Characters": item["character_count"],
                }
                for item in uploaded_context_items
            ])
            st.dataframe(context_status_df, use_container_width=True, hide_index=True)

    with right_col:
        st.markdown(
            """
            <div class="guardrail-card">
                <h4>Course Setup Status</h4>
                <p>Complete the course connector steps to prepare for evidence sync.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        setup_items = {
            "Brightspace Course Code": bool(course_code),
            "Semester Selected": bool(semester),
            "Professor Name": bool(professor_name),
            "Course Name Added": bool(course_name),
            "Brightspace Connected": st.session_state.brightspace_connected,
            "Syllabus Available": syllabus_file is not None,
            "Learning Materials Available": bool(materials_files),
            "Assignments / Rubrics Available": bool(assignments_files),
            "Course Context Extracted": bool(st.session_state.get("uploaded_course_context", [])),
        }

        completed = sum(setup_items.values())
        total = len(setup_items)

        st.metric("Setup Progress", f"{completed}/{total}")
        st.progress(completed / total)

        for item, status in setup_items.items():
            st.markdown(f"{'✅' if status else '⚠️'} **{item}**")

        st.markdown("---")

        st.markdown(
            """
            <div class="guardrail-card">
                <h4>Responsible Use Reminder</h4>
                <p>
                This system supports faculty insight only. It does not assign grades, rank students,
                or generate disciplinary recommendations.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    if completed >= 5:
        st.success("Course setup is ready for evidence and feedback sync.")
    else:
        st.warning("Complete the course setup criteria before running the evidence and feedback sync.")


with tab_sync:
    st.markdown(
        """
        <div class="section-card">
            <h3>Course Evidence & Feedback Sync</h3>
            <p>
            Retrieve existing course evidence from Brightspace and an approved student feedback system.
            This page shows data availability only. AI interpretation appears on the Faculty Dashboard.
            </p>
            <span class="pill">Assignment evidence</span>
            <span class="pill">Professor feedback</span>
            <span class="pill">Anonymous reflections</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    left_col, right_col = st.columns([2, 1], gap="large")

    with left_col:
        st.subheader("Refresh Course Evidence")

        st.markdown(
            """
            This step simulates a secure course evidence connection. In the full implementation,
            the platform would retrieve assignment records, professor feedback, rubrics, and anonymous
            student feedback responses from approved university systems.
            """
        )

        if st.button("Refresh Course Evidence", key=f"refresh_evidence_{st.session_state.reset_counter}"):
            st.session_state.brightspace_connected = True
            st.session_state.course_evidence_loaded = True
            st.session_state.ai_summary_generated = False
            st.session_state.last_sync = datetime.now().strftime("%B %d, %Y at %I:%M %p")
            st.session_state.course_evidence_df = load_mock_course_evidence()

        if st.session_state.course_evidence_loaded:
            df = st.session_state.course_evidence_df

            st.markdown(
                f"""
                <div class="success-box">
                Course evidence refreshed successfully. Last refreshed: {st.session_state.last_sync}
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("### Brightspace Assignment Evidence")

            b1, b2, b3 = st.columns(3)
            with b1:
                st.metric("Assignment Records", len(df))
            with b2:
                st.metric("Feedback Comments", df["professor_feedback"].count())
            with b3:
                st.metric("Modules Matched", df["week"].nunique())

            st.markdown("✅ Assignment letter grades retrieved")
            st.markdown("✅ Professor assignment feedback retrieved")
            st.markdown("✅ Assignment names matched to course modules")
            st.markdown("✅ Rubrics and learning outcomes available for comparison")

            st.markdown("---")
            st.markdown("### Connected Student Feedback Portal")

            portal_col1, portal_col2 = st.columns(2, gap="large")

            with portal_col1:
                st.markdown(
                    """
                    <div class="data-card">
                        <h4>Mid-Semester Student Feedback</h4>
                        <p><strong>Status:</strong> Available</p>
                        <p><strong>Available Date:</strong> October 20, 2026</p>
                        <p><strong>Use:</strong> Timely instructional adjustment while the course is active.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with portal_col2:
                st.markdown(
                    """
                    <div class="data-card">
                        <h4>End-of-Semester Student Feedback</h4>
                        <p><strong>Status:</strong> Scheduled</p>
                        <p><strong>Available Date:</strong> December 15, 2026</p>
                        <p><strong>Use:</strong> Future course planning and long-term improvement.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            st.markdown("✅ Anonymous mid-semester student reflections retrieved")
            st.markdown("✅ Confidence scores retrieved")
            st.markdown("✅ Career relevance scores retrieved")
            st.markdown("✅ Student support comments retrieved")

            with st.expander("View student reflection prompt preview"):
                st.markdown("**Prompt 1:** What concept was clearest to you this week?")
                st.markdown("**Prompt 2:** What concept still feels unclear or difficult?")
                st.markdown("**Prompt 3:** How confident are you applying this week’s material?")
                st.markdown("**Prompt 4:** What support would help you learn this better?")
                st.markdown("**Prompt 5:** How relevant does this week’s material feel to your academic or career goals?")

            st.markdown("---")
            st.markdown("### Midterm Feedback Survey Sync")
            st.markdown(
                "This simulates connecting to an approved mid-semester student feedback platform and retrieving anonymous question-level responses."
            )

            if st.button("Midterm Feedback Available — Sync Now", key=f"sync_midterm_{st.session_state.reset_counter}"):
                st.session_state.midterm_feedback_synced = True
                st.session_state.midterm_feedback_df = load_mock_midterm_feedback()

            if st.session_state.midterm_feedback_synced:
                survey_df = st.session_state.midterm_feedback_df
                s1, s2, s3 = st.columns(3)
                with s1:
                    st.metric("Survey Responses", len(survey_df))
                with s2:
                    st.metric("Survey Questions", survey_df["question_id"].nunique())
                with s3:
                    st.metric("Anonymous Students", survey_df["student_id"].nunique())

                st.markdown("✅ Midterm survey questions retrieved")
                st.markdown("✅ Anonymous student responses retrieved")
                st.markdown("✅ Learning style, pacing, confidence, and career-value feedback available")

                with st.expander("Preview synced midterm feedback questions and responses"):
                    st.dataframe(
                        survey_df[[
                            "student_id",
                            "question_id",
                            "question_text",
                            "response_text",
                            "feedback_theme",
                            "learning_signal",
                            "linked_module_topic",
                        ]].head(20),
                        use_container_width=True,
                        hide_index=True,
                    )
            else:
                st.warning("Midterm feedback has not been synced yet.")

            st.markdown("---")
            st.markdown("### Raw Evidence Preview")
            st.caption("Preview is limited to raw/source evidence. AI interpretation fields are intentionally hidden on this page.")

            preview_cols = [
                "student_id",
                "week",
                "module_topic",
                "assignment_name",
                "assignment_grade",
                "confidence_score",
                "career_relevance_score"
            ]

            st.dataframe(df[preview_cols].head(10), use_container_width=True)

            st.success("Data is ready for AI learning gap analysis on the Faculty Dashboard.")

        else:
            st.warning("Course evidence has not been refreshed yet.")

    with right_col:
        st.markdown(
            """
            <div class="guardrail-card">
                <h4>Data Readiness Summary</h4>
                <p>Refresh course evidence to prepare the faculty dashboard.</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        if st.session_state.course_evidence_loaded:
            df = st.session_state.course_evidence_df

            st.metric("Anonymous Students", df["student_id"].nunique())
            st.metric("Student Reflections", df["reflection_text"].count())
            st.metric("Average Confidence", f"{round(df['confidence_score'].mean(), 2)}/5")
            st.metric("Average Assignment Outcome", f"{round(df['assignment_grade'].mean(), 1)}%")
            if st.session_state.midterm_feedback_synced:
                st.metric("Midterm Survey Responses", len(st.session_state.midterm_feedback_df))
            else:
                st.metric("Midterm Survey Responses", "0")

            st.markdown("---")
            st.markdown("✅ Course goals available")
            st.markdown("✅ Assignment outcomes available")
            st.markdown("✅ Professor feedback available")
            st.markdown("✅ Anonymous student feedback available")
            if st.session_state.midterm_feedback_synced:
                st.markdown("✅ Midterm survey feedback available")
            if st.session_state.get("uploaded_course_context", []):
                st.markdown("✅ Uploaded course context available for matching")
            st.markdown("✅ Ready for AI analysis")

        else:
            st.metric("Anonymous Students", "0")
            st.metric("Student Reflections", "0")
            st.metric("Average Confidence", "—")
            st.metric("Average Assignment Outcome", "—")

        st.markdown("---")

        st.markdown(
            """
            <div class="guardrail-card">
                <h4>Privacy Guardrail</h4>
                <p>
                Retrieved records use anonymous student IDs. The dashboard summarizes patterns
                at the class and learning-outcome level, not as individual student profiles.
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )


with tab_dashboard:
    st.markdown(
        """
        <div class="section-card">
            <h3>Faculty Learning Intelligence Dashboard</h3>
            <p>
            Generate a class-level learning intelligence summary across course goals,
            assignment outcomes, professor feedback, and anonymous student reflections.
            </p>
            <span class="pill">Learning report</span>
            <span class="pill">Signal categories</span>
            <span class="pill">Charts & trends</span>
            <span class="pill">Recommended actions</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.course_evidence_loaded:
        st.warning("No course evidence loaded yet. Go to Page 2 and click Refresh Course Evidence first.")

    else:
        df = st.session_state.course_evidence_df

        if st.button("Generate AI Learning Gap Summary", key=f"generate_ai_{st.session_state.reset_counter}"):
            st.session_state.ai_summary_generated = True

        if not st.session_state.ai_summary_generated:
            st.markdown(
                """
                <div class="warning-box">
                Course evidence is available. Click “Generate AI Learning Gap Summary” to produce faculty-facing learning intelligence.
                </div>
                """,
                unsafe_allow_html=True
            )

            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Records Available", len(df))
            with c2:
                st.metric("Modules Covered", df["week"].nunique())
            with c3:
                st.metric("Anonymous Students", df["student_id"].nunique())

        else:
            signal_counts = df["signal_category"].value_counts()
            most_common_signal = signal_counts.index[0]
            avg_confidence = round(df["confidence_score"].mean(), 2)
            avg_grade = round(df["assignment_grade"].mean(), 1)

            weekly_summary = (
                df.groupby(["week", "module_topic"])
                .agg(
                    avg_grade=("assignment_grade", "mean"),
                    avg_confidence=("confidence_score", "mean")
                )
                .reset_index()
            )

            lowest_confidence_row = weekly_summary.sort_values("avg_confidence").iloc[0]
            lowest_grade_row = weekly_summary.sort_values("avg_grade").iloc[0]

            st.markdown(
                """
                <div class="success-box">
                AI learning gap summary generated. Results are aggregated at the class level.
                </div>
                """,
                unsafe_allow_html=True
            )

            report_tab, signal_tab, charts_tab, actions_tab, responsible_tab = st.tabs(
                [
                    "Learning Report",
                    "Signal Categories",
                    "Charts & Trends",
                    "Recommended Actions",
                    "Responsible Use"
                ]
            )

            with report_tab:
                st.markdown("### Executive Learning Summary")

                st.markdown(
                    f"""
                    <div class="ai-card">
                        <h4>Class-Level Interpretation</h4>
                        <p>
                        The analysis indicates that students are generally engaging with the course concepts,
                        but the strongest recurring pattern is <strong>{most_common_signal}</strong>.
                        Assignment outcomes and anonymous student feedback suggest that the class is strongest
                        when explaining core concepts, but needs additional support translating change and innovation
                        frameworks into applied recommendations for realistic organizational or client scenarios.
                        </p>
                        <p>
                        The lowest confidence area is <strong>Week {int(lowest_confidence_row['week'])}: {lowest_confidence_row['module_topic']}</strong>,
                        while the lowest assignment outcome appears in <strong>Week {int(lowest_grade_row['week'])}: {lowest_grade_row['module_topic']}</strong>.
                        Faculty attention should focus on applied-transfer practice, framework selection, and clearer model examples.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("### Course Learning Health")

                k1, k2, k3, k4 = st.columns(4)
                with k1:
                    st.metric("Records Analyzed", len(df))
                with k2:
                    st.metric("Avg Confidence", f"{avg_confidence}/5")
                with k3:
                    st.metric("Avg Assignment Outcome", f"{avg_grade}%")
                with k4:
                    st.metric("Most Common Signal", most_common_signal)

                st.markdown("### Learning Outcome Gap Analysis")
                gap_table = generate_learning_gap_table(df)
                st.dataframe(gap_table, use_container_width=True, hide_index=True)

            with signal_tab:
                st.markdown("### Learning Signal Categories")

                signal_chart = signal_counts.reset_index()
                signal_chart.columns = ["Learning Signal", "Count"]

                st.dataframe(signal_chart, use_container_width=True, hide_index=True)

                st.markdown(
                    f"""
                    <div class="ai-card">
                        <h4>Signal Interpretation</h4>
                        <p>
                        The most common learning signal is <strong>{most_common_signal}</strong>.
                        This suggests that the primary instructional opportunity is not simply explaining concepts again,
                        but helping students transfer course frameworks into applied recommendations and real organizational contexts.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("### Signal Distribution")
                st.bar_chart(signal_chart.set_index("Learning Signal"))

            with charts_tab:
                st.markdown("### Learning Signal Distribution")
                signal_chart = signal_counts.reset_index()
                signal_chart.columns = ["Learning Signal", "Count"]
                st.bar_chart(signal_chart.set_index("Learning Signal"))

                st.markdown(
                    f"""
                    <div class="info-box">
                    Chart insight: <strong>{most_common_signal}</strong> appears most often in the simulated evidence.
                    This indicates that the dashboard should prioritize instructional recommendations tied to this pattern.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("### Average Confidence by Week")
                confidence_chart = (
                    df.groupby("week")["confidence_score"]
                    .mean()
                    .reset_index()
                    .set_index("week")
                )
                st.line_chart(confidence_chart)

                lowest_conf_week = int(confidence_chart["confidence_score"].idxmin())
                lowest_conf_value = round(confidence_chart["confidence_score"].min(), 2)

                st.markdown(
                    f"""
                    <div class="info-box">
                    Chart insight: Average confidence is lowest in Week {lowest_conf_week}, at {lowest_conf_value}/5.
                    This suggests students may need additional support around that module before moving into later assignments.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("### Average Assignment Outcome by Week")
                grade_chart = (
                    df.groupby("week")["assignment_grade"]
                    .mean()
                    .reset_index()
                    .set_index("week")
                )
                st.line_chart(grade_chart)

                lowest_grade_week = int(grade_chart["assignment_grade"].idxmin())
                lowest_grade_value = round(grade_chart["assignment_grade"].min(), 1)

                st.markdown(
                    f"""
                    <div class="info-box">
                    Chart insight: Average assignment outcomes are lowest in Week {lowest_grade_week}, at {lowest_grade_value}%.
                    This points to a possible gap between the course learning objective and students’ ability to demonstrate it in assignment work.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with actions_tab:
                st.markdown("### Recommended Faculty Actions")

                action_table = get_top_faculty_actions(df)
                default_actions = action_table["Recommended Action"].tolist()

                while len(default_actions) < 3:
                    default_actions.append("Provide an additional applied example connected to the next assignment.")

                action_1, action_2, action_3 = st.columns(3, gap="large")

                with action_1:
                    st.markdown(
                        f"""
                        <div class="gap-card">
                            <h4>1. Add Applied Examples</h4>
                            <p>{default_actions[0]}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with action_2:
                    st.markdown(
                        f"""
                        <div class="gap-card">
                            <h4>2. Reinforce Framework Selection</h4>
                            <p>{default_actions[1]}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                with action_3:
                    st.markdown(
                        f"""
                        <div class="gap-card">
                            <h4>3. Support Evidence-Based Recommendations</h4>
                            <p>{default_actions[2]}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                st.markdown("### Supporting Recommendation Evidence")
                st.dataframe(action_table, use_container_width=True, hide_index=True)

            with responsible_tab:
                st.markdown(
                    """
                    <div class="guardrail-card">
                        <h4>Responsible AI Guardrail</h4>
                        <p>
                        This dashboard does not grade, rank, discipline, or profile individual students.
                        Assignment outcomes and student reflections are used only as aggregated evidence
                        to identify class-level learning patterns and instructional attention areas.
                        Professor Smith remains the final decision-maker.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown("### Governance Controls Shown in MVP")
                st.markdown("✅ Anonymous student identifiers only")
                st.markdown("✅ Aggregated class-level summaries")
                st.markdown("✅ No individual ranking or risk scoring")
                st.markdown("✅ No grading decisions made by the system")
                st.markdown("✅ Human faculty oversight required")
                st.markdown("✅ Simulated student reflections used for testing")

# -----------------------------
# Tab 4: Live AI Intelligence Layer
# -----------------------------
with tab_live_ai:
    st.markdown(
        """
        <div class="section-card">
            <h3>Live AI Intelligence Layer</h3>
            <p>
            This tab uses the OpenAI API to analyze anonymous course evidence, uploaded course context excerpts,
            and synced midterm feedback survey responses. The AI generates the interpretation from raw evidence;
            it is not simply displaying pre-labeled mock scores.
            </p>
            <span class="pill">OpenAI API</span>
            <span class="pill">Raw evidence interpretation</span>
            <span class="pill">Module deep dives</span>
            <span class="pill">Class-level only</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    if not st.session_state.course_evidence_loaded:
        st.warning("No course evidence loaded yet. Go to Page 2 and click Refresh Course Evidence first.")

    else:
        df = st.session_state.course_evidence_df
        context_items = st.session_state.get("uploaded_course_context", [])
        survey_df = st.session_state.get("midterm_feedback_df", pd.DataFrame())
        context_summary = generate_context_match_summary(df, context_items)

        st.markdown(
            """
            <div class="info-box">
            This live layer sends a small anonymous sample of course evidence to OpenAI, plus uploaded course-context excerpts
            and midterm survey response summaries when available. Student identifiers are anonymous and the analysis stays at the class/module level.
            </div>
            """,
            unsafe_allow_html=True
        )

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Anonymous Records", len(df))
        with c2:
            st.metric("Rows Sent to Live AI", "25")
        with c3:
            st.metric("Course Files Parsed", len(context_items))
        with c4:
            api_status = "Configured" if os.getenv("OPENAI_API_KEY") else "Missing"
            st.metric("API Key Status", api_status)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Midterm Survey Synced", "Yes" if st.session_state.midterm_feedback_synced else "No")
        with m2:
            st.metric("Survey Responses", len(survey_df) if st.session_state.midterm_feedback_synced else 0)
        with m3:
            st.metric("Context Keyword Matches", len(context_summary))

        if context_items:
            with st.expander("View uploaded course context available to Live AI"):
                st.dataframe(
                    pd.DataFrame([
                        {
                            "File": item["file_name"],
                            "Type": item["category"],
                            "Status": item["status"],
                            "Characters": item["character_count"],
                        }
                        for item in context_items
                    ]),
                    use_container_width=True,
                    hide_index=True,
                )
        else:
            st.warning("No uploaded course context is available yet. Upload syllabus/modules/assignments on Page 1 for stronger module deep dives.")

        if st.button("Run Live AI Interpretation", key=f"run_live_ai_{st.session_state.reset_counter}"):
            with st.spinner("Running live AI analysis against course context, Brightspace evidence, and midterm feedback..."):
                st.session_state.live_ai_report = run_live_learning_intelligence_agent(df)
                st.session_state.live_ai_generated = True

        if not st.session_state.live_ai_generated:
            st.markdown(
                """
                <div class="warning-box">
                Click “Run Live AI Interpretation” to generate a live AI report from synced course evidence.
                </div>
                """,
                unsafe_allow_html=True
            )

        else:
            report = st.session_state.live_ai_report

            if report is None:
                st.error("No live AI report was returned.")

            elif "error" in report:
                st.error(report["error"])

            else:
                st.markdown(
                    """
                    <div class="success-box">
                    Live AI intelligence report generated successfully.
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                live_report_tab, module_tab, live_gap_tab, live_actions_tab, live_responsible_tab = st.tabs(
                    [
                        "Live Learning Report",
                        "Module Deep Dives",
                        "Learning Gaps",
                        "Live Actions",
                        "Responsible Use"
                    ]
                )

                grade_chart = df.groupby("week")["assignment_grade"].mean().reset_index().set_index("week")
                grade_readiness_chart = pd.DataFrame()
                survey_readiness_chart = pd.DataFrame()
                if st.session_state.midterm_feedback_synced and not survey_df.empty:
                    survey_readiness_chart = survey_readiness_by_week_chart(survey_df)
                    grade_readiness_chart = grade_vs_readiness_chart(df, survey_df)

                module_deep_dives = report.get("module_deep_dives", [])
                if not module_deep_dives and report.get("context_matches"):
                    module_deep_dives = [
                        {
                            "module_or_topic": item.get("module_or_topic", "Module"),
                            "module_status": "Mixed",
                            "what_is_working": item.get("instructional_meaning", "Some evidence of learning is visible."),
                            "where_students_are_struggling": item.get("evidence_alignment", "Additional review may be useful."),
                            "evidence": item.get("matched_course_context", "Course context was matched to this module."),
                            "faculty_adjustment": "Use this module as a discussion point for the next instructional adjustment."
                        }
                        for item in report.get("context_matches", [])
                    ]

                gaps = report.get("learning_gaps", [])
                gap_chart = gap_frequency_chart_from_gaps(gaps)
                top_gap = gaps[0] if gaps else {}
                headline_findings = report.get("headline_findings", [])

                # -----------------------------
                # Live Learning Report
                # -----------------------------
                with live_report_tab:
                    st.markdown("### Live Learning Report")

                    summary = shorten_text(report.get("executive_summary", "No executive summary returned."), 430)
                    st.markdown(
                        f"""
                        <div class="ai-card">
                            <h4>AI Summary</h4>
                            <p>{h(summary)}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    k1, k2, k3, k4 = st.columns(4)
                    with k1:
                        render_metric_card("Learning Health", report.get("overall_learning_health", "Moderate"), "AI-generated class-level status")
                    with k2:
                        render_metric_card("Top Gap", top_gap.get("gap_title", "—"), "Most frequent expectation mismatch")
                    with k3:
                        render_metric_card("Priority Area", top_gap.get("where_it_shows_up", "—"), "Where the issue appears")
                    with k4:
                        render_metric_card("Evidence Used", f"{len(df)} rows", "Brightspace-style evidence + surveys")

                    if headline_findings:
                        st.markdown("### What The AI Is Seeing")
                        cols = st.columns(min(3, len(headline_findings)))
                        for i, finding in enumerate(headline_findings[:3]):
                            with cols[i % len(cols)]:
                                st.markdown(
                                    f"""
                                    <div class="gap-card" style="min-height: 210px;">
                                        <h4>{h(finding.get("finding", "Learning pattern"))}</h4>
                                        <p><strong>Meaning:</strong> {h(finding.get("what_it_means", ""))}</p>
                                        <p><strong>Shows up in:</strong> {h(finding.get("where_it_shows_up", ""))}</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )

                    st.markdown("### Evidence Trends")
                    chart_col1, insight_col1 = st.columns([2, 1], gap="large")
                    with chart_col1:
                        st.markdown("#### Assignment Outcome vs. Survey Readiness")
                        if not grade_readiness_chart.empty:
                            st.line_chart(grade_readiness_chart)
                        else:
                            st.line_chart(grade_chart)
                    with insight_col1:
                        st.markdown(
                            f"""
                            <div class="info-box">
                            <strong>AI interpretation:</strong> {h(report.get("chart_explanations", {}).get("assignment_outcome_by_week", "Assignment outcomes and survey readiness together show where student confidence may or may not align with demonstrated performance."))}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                        if not grade_readiness_chart.empty:
                            st.caption("Survey readiness is scaled from 1–5 to 0–100 so it can be compared visually with assignment outcomes.")

                    if not gap_chart.empty:
                        chart_col3, insight_col3 = st.columns([2, 1], gap="large")
                        with chart_col3:
                            st.markdown("#### Top Learning Gaps by Frequency")
                            st.bar_chart(gap_chart)
                        with insight_col3:
                            st.markdown(
                                f"""
                                <div class="info-box">
                                <strong>AI interpretation:</strong> {h(report.get("chart_explanations", {}).get("gap_frequency", "The most frequent gaps should guide near-term instructional adjustments."))}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                # -----------------------------
                # Module Deep Dives
                # -----------------------------
                with module_tab:
                    st.markdown("### Module Deep Dives")
                    st.caption("This view summarizes what is working and where students are struggling by module. It replaces technical context-match language with professor-facing module patterns.")

                    status_counts = {"Working": 0, "Struggling": 0, "Mixed": 0, "Needs Support": 0}
                    for dive in module_deep_dives:
                        status_counts[module_status_chip(dive.get("module_status"))] += 1

                    md1, md2, md3, md4 = st.columns(4)
                    with md1:
                        render_metric_card("Working", status_counts["Working"], "Modules showing clear understanding")
                    with md2:
                        render_metric_card("Struggling", status_counts["Struggling"], "Modules needing attention")
                    with md3:
                        render_metric_card("Mixed", status_counts["Mixed"], "Some strengths and some gaps")
                    with md4:
                        render_metric_card("Needs Support", status_counts["Needs Support"], "Modules needing scaffolding")

                    with st.expander("View course-context keyword summary sent to AI"):
                        deterministic_df = pd.DataFrame(context_summary)
                        if not deterministic_df.empty:
                            st.dataframe(deterministic_df, use_container_width=True, hide_index=True)
                        else:
                            st.warning("No uploaded course context summary is available yet.")

                    if module_deep_dives:
                        st.markdown("### Module Patterns")
                        for index, dive in enumerate(module_deep_dives, start=1):
                            module_name = dive.get("module_or_topic", f"Module {index}")
                            status = module_status_chip(dive.get("module_status"))
                            with st.expander(f"{module_name} — {status}", expanded=(index <= 2)):
                                render_chip(status)
                                st.markdown(
                                    f"""
                                    <div class="gap-card">
                                        <p><strong>What is working:</strong> {h(dive.get("what_is_working", ""))}</p>
                                        <p><strong>Where students are struggling:</strong> {h(dive.get("where_students_are_struggling", ""))}</p>
                                        <p><strong>Evidence:</strong> {h(dive.get("evidence", ""))}</p>
                                        <p><strong>Faculty adjustment:</strong> {h(dive.get("faculty_adjustment", ""))}</p>
                                    </div>
                                    """,
                                    unsafe_allow_html=True
                                )
                    else:
                        st.warning("No module deep dives were returned.")

                # -----------------------------
                # Learning Gaps
                # -----------------------------
                with live_gap_tab:
                    st.markdown("### Learning Gaps")
                    st.caption("This view ranks where student reflections, assignment evidence, and professor expectations appear misaligned.")

                    gap_df = pd.DataFrame(gaps) if gaps else pd.DataFrame()
                    top_frequency = 0
                    if gaps:
                        try:
                            top_frequency = int(first_nonempty(top_gap.get("frequency_count"), default=0))
                        except Exception:
                            top_frequency = 0

                    g1, g2, g3, g4 = st.columns(4)
                    with g1:
                        render_metric_card("Top Gap", top_gap.get("gap_title", "—"), "Most repeated mismatch")
                    with g2:
                        render_metric_card("How Often", top_frequency if top_frequency else top_gap.get("frequency_label", "—"), "Frequency across evidence")
                    with g3:
                        render_metric_card("Priority", top_gap.get("priority", "—"), "Near-term instructional importance")
                    with g4:
                        render_metric_card("Main Area", top_gap.get("where_it_shows_up", "—"), "Module or assignment area")

                    chart_col, insight_col = st.columns([2, 1], gap="large")
                    with chart_col:
                        st.markdown("#### Top Learning Gaps by Frequency")
                        if not gap_chart.empty:
                            st.bar_chart(gap_chart)
                        else:
                            st.info("No gap frequency chart is available yet.")
                    with insight_col:
                        st.markdown(
                            f"""
                            <div class="info-box">
                            <strong>Interpretation:</strong> {h(report.get("chart_explanations", {}).get("gap_frequency", "Ranked gaps show which expectation mismatches are appearing most often."))}
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                    with st.expander("View full learning gaps table"):
                        if not gap_df.empty:
                            st.dataframe(gap_df, use_container_width=True, hide_index=True)
                        else:
                            st.warning("No live learning gaps were returned.")

                    if gaps:
                        st.markdown("### Ranked Gap Interpretation")
                        for rank, gap in enumerate(gaps, start=1):
                            title = first_nonempty(gap.get("gap_title"), gap.get("module_or_topic"), f"Learning Gap {rank}")
                            frequency = first_nonempty(gap.get("frequency_count"), gap.get("frequency_label"))
                            priority = gap.get("priority", "")
                            st.markdown(
                                f"""
                                <div class="gap-card">
                                    <h4>#{rank} {h(title)}</h4>
                                    <div><span class="pill">Frequency: {h(frequency)}</span><span class="pill">Priority: {h(priority)}</span></div>
                                    <p><strong>Where it shows up:</strong> {h(gap.get("where_it_shows_up", ""))}</p>
                                    <p><strong>Professor expectation:</strong> {h(gap.get("professor_expectation", ""))}</p>
                                    <p><strong>Student evidence:</strong> {h(gap.get("student_evidence", ""))}</p>
                                    <p><strong>Grade / feedback evidence:</strong> {h(gap.get("grade_feedback_evidence", ""))}</p>
                                    <p><strong>Faculty next move:</strong> {h(gap.get("suggested_faculty_action", ""))}</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.warning("No live learning gaps were returned.")

                # -----------------------------
                # Live Actions
                # -----------------------------
                with live_actions_tab:
                    st.markdown("### Live Recommended Faculty Actions")
                    st.caption("This view turns the live AI findings into a practical action plan for Professor Smith.")

                    actions = report.get("recommended_actions", [])

                    if actions:
                        a1, a2, a3, a4 = st.columns(4)
                        with a1:
                            render_metric_card("Priority 1", actions[0].get("action_title", "—"), "Start here")
                        with a2:
                            render_metric_card("Priority 2", actions[1].get("action_title", "—") if len(actions) > 1 else "—", "Second move")
                        with a3:
                            render_metric_card("Timing", "Next 1–2 classes", "Best demo action window")
                        with a4:
                            render_metric_card("Action Type", "Faculty-led support", "Human decision required")

                        st.markdown("### Suggested Next-Class Plan")
                        st.markdown(
                            """
                            <div class="ai-card">
                                <h4>Professor Smith's next class plan</h4>
                                <p><strong>1.</strong> Start with a short recap of the most common expectation mismatch.</p>
                                <p><strong>2.</strong> Show one worked example connecting a framework to a recommendation.</p>
                                <p><strong>3.</strong> Use a short group case to practice applying the framework before the next assignment.</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )

                        action_groups = {
                            "Support Application": [],
                            "Clarify Concepts": [],
                            "Adjust Pacing": [],
                            "Leverage Strengths": [],
                        }

                        for action in actions:
                            title = action.get("action_title", "")
                            description = action.get("action_description", "")
                            combined = f"{title} {description}".lower()
                            if any(word in combined for word in ["pace", "pacing", "recap", "slow"]):
                                action_groups["Adjust Pacing"].append(action)
                            elif any(word in combined for word in ["clarify", "distinction", "compare", "comparison", "visual"]):
                                action_groups["Clarify Concepts"].append(action)
                            elif any(word in combined for word in ["strength", "leverage", "leadership", "confidence"]):
                                action_groups["Leverage Strengths"].append(action)
                            else:
                                action_groups["Support Application"].append(action)

                        st.markdown("### Action Plan by Category")
                        for group_name, group_actions in action_groups.items():
                            if not group_actions:
                                continue
                            with st.expander(group_name, expanded=(group_name == "Support Application")):
                                for action in group_actions:
                                    tags = action_tags(action.get("action_title", ""), action.get("action_description", ""))
                                    render_compact_action_card(
                                        action.get("action_title", "Recommended Action"),
                                        action.get("action_description", ""),
                                        action.get("why_it_matters", ""),
                                        tags,
                                    )
                    else:
                        st.warning("No live recommended actions were returned.")

                # -----------------------------
                # Responsible Use
                # -----------------------------
                with live_responsible_tab:
                    st.markdown("### Responsible Use Note")
                    st.markdown(
                        f"""
                        <div class="guardrail-card">
                            <h4>Live AI Guardrail</h4>
                            <p>{h(report.get("responsible_use_note", "No responsible use note returned."))}</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    st.markdown("### Limitations")
                    st.markdown(
                        f"""
                        <div class="warning-box">
                        {h(report.get("limitations", "No limitations returned."))}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

                    with st.expander("View raw live AI JSON"):
                        st.json(report)

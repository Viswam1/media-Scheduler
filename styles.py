"""Custom CSS for a clean, professional look."""
import streamlit as st


def apply_styles():
    st.markdown("""
    <style>
        /* Main container */
        .main .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            max-width: 1200px;
        }

        /* Header */
        .app-header {
            background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
            color: white;
            padding: 1.75rem 2rem;
            border-radius: 12px;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 12px rgba(30, 58, 138, 0.15);
        }
        .app-header h1 {
            margin: 0;
            font-size: 1.8rem;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .app-header p {
            margin: 0.4rem 0 0 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }

        /* Cards */
        .card {
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 10px;
            padding: 1.25rem;
            margin-bottom: 1rem;
            box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        }
        .card-title {
            font-weight: 600;
            font-size: 1.05rem;
            color: #111827;
            margin-bottom: 0.4rem;
        }
        .card-meta {
            font-size: 0.85rem;
            color: #6b7280;
        }

        /* Status badges */
        .badge {
            display: inline-block;
            padding: 0.2rem 0.6rem;
            border-radius: 999px;
            font-size: 0.75rem;
            font-weight: 600;
        }
        .badge-pending { background: #fef3c7; color: #92400e; }
        .badge-progress { background: #dbeafe; color: #1e40af; }
        .badge-done { background: #d1fae5; color: #065f46; }

        /* Metric cards */
        [data-testid="stMetricValue"] {
            font-size: 1.6rem;
            color: #1e3a8a;
        }

        /* Buttons */
        .stButton > button {
            border-radius: 8px;
            font-weight: 500;
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 4px;
        }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 0.5rem 1rem;
        }
    </style>
    """, unsafe_allow_html=True)


def header(title, subtitle):
    st.markdown(f"""
    <div class="app-header">
        <h1>🎬 {title}</h1>
        <p>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)


def status_badge(status):
    cls = {
        "Pending": "badge-pending",
        "In Progress": "badge-progress",
        "Completed": "badge-done",
    }.get(status, "badge-pending")
    return f'<span class="badge {cls}">{status}</span>'

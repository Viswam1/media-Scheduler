"""Church Media Team Scheduler — Streamlit app."""
from datetime import date, datetime
import pandas as pd
import streamlit as st

import database as db
from styles import apply_styles, header, status_badge

# ---------- Page config ----------
st.set_page_config(
    page_title="Church Media Scheduler",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_styles()
db.init_db()

TASK_TYPES = [
    "Camera",
    "Live Mixing (Audio)",
    "Livestream",
    "Video Editing",
    "Graphics / Slides",
    "Photography",
    "Lighting",
    "Sound Check",
    "Other",
]
STATUS_OPTIONS = ["Pending", "In Progress", "Completed"]


# ---------- Sidebar ----------
with st.sidebar:
    st.markdown("### 🎬 Media Scheduler")
    st.caption("Church Media Team Management")
    st.divider()
    page = st.radio(
        "Navigate",
        ["📊 Dashboard", "📅 Events", "👥 Members", "✅ Assign Tasks"],
        label_visibility="collapsed",
    )
    st.divider()
    st.caption(f"Today: {date.today().strftime('%b %d, %Y')}")


# =========================================================
# DASHBOARD
# =========================================================
if page == "📊 Dashboard":
    header("Dashboard", "Overview of upcoming events and assignments")

    members = db.get_members()
    events = db.get_events()
    tasks = db.get_all_tasks()

    pending = sum(1 for t in tasks if t["status"] == "Pending")
    completed = sum(1 for t in tasks if t["status"] == "Completed")
    upcoming = [e for e in events if e["event_date"] >= str(date.today())]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Active Members", len(members))
    c2.metric("Upcoming Events", len(upcoming))
    c3.metric("Pending Tasks", pending)
    c4.metric("Completed Tasks", completed)

    st.divider()

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader("📅 Upcoming Events")
        if not upcoming:
            st.info("No upcoming events. Add one in the **Events** tab.")
        else:
            for ev in sorted(upcoming, key=lambda x: x["event_date"])[:5]:
                ev_tasks = db.get_tasks_for_event(ev["id"])
                assigned = sum(1 for t in ev_tasks if t["assigned_member_id"])
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{ev['title']}</div>
                    <div class="card-meta">
                        📆 {ev['event_date']} &nbsp;•&nbsp; ⏰ {ev['start_time'] or 'TBD'} &nbsp;•&nbsp; 📍 {ev['location'] or 'TBD'}
                    </div>
                    <div class="card-meta" style="margin-top:0.5rem;">
                        🎯 {assigned}/{len(ev_tasks)} tasks assigned
                    </div>
                </div>
                """, unsafe_allow_html=True)

    with col_right:
        st.subheader("👥 Team Members")
        if not members:
            st.info("No members yet. Add some in the **Members** tab.")
        else:
            for m in members:
                skills = m["skills"] or "—"
                st.markdown(f"""
                <div class="card" style="padding:0.75rem 1rem;">
                    <div class="card-title" style="font-size:0.95rem;">{m['name']}</div>
                    <div class="card-meta">🎨 {skills}</div>
                </div>
                """, unsafe_allow_html=True)


# =========================================================
# EVENTS
# =========================================================
elif page == "📅 Events":
    header("Events", "Create and manage upcoming media events")

    with st.expander("➕ Add New Event", expanded=False):
        with st.form("add_event_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            title = c1.text_input("Event Title *", placeholder="Sunday Service")
            event_date = c2.date_input("Date *", value=date.today())

            c3, c4 = st.columns(2)
            start_time = c3.text_input("Start Time", placeholder="09:00 AM")
            location = c4.text_input("Location", placeholder="Main Sanctuary")

            description = st.text_area("Description / Notes", placeholder="Any special details...")

            if st.form_submit_button("Create Event", use_container_width=True, type="primary"):
                if not title.strip():
                    st.error("Event title is required.")
                else:
                    db.add_event(title.strip(), str(event_date), start_time, location, description)
                    st.success(f"Event '{title}' created!")
                    st.rerun()

    st.divider()

    events = db.get_events()
    if not events:
        st.info("No events yet. Create your first one above.")
    else:
        st.subheader(f"All Events ({len(events)})")
        for ev in events:
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.markdown(f"""
                    <div class="card">
                        <div class="card-title">🎬 {ev['title']}</div>
                        <div class="card-meta">
                            📆 {ev['event_date']} &nbsp;•&nbsp; ⏰ {ev['start_time'] or 'TBD'} &nbsp;•&nbsp; 📍 {ev['location'] or 'TBD'}
                        </div>
                        {f'<div class="card-meta" style="margin-top:0.5rem;">{ev["description"]}</div>' if ev['description'] else ''}
                    </div>
                    """, unsafe_allow_html=True)
                with col2:
                    if st.button("🗑️ Delete", key=f"del_ev_{ev['id']}", use_container_width=True):
                        db.delete_event(ev["id"])
                        st.rerun()


# =========================================================
# MEMBERS
# =========================================================
elif page == "👥 Members":
    header("Team Members", "Manage your media team roster")

    with st.expander("➕ Add New Member", expanded=False):
        with st.form("add_member_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            name = c1.text_input("Full Name *", placeholder="John Doe")
            email = c2.text_input("Email", placeholder="john@example.com")

            c3, c4 = st.columns(2)
            phone = c3.text_input("Phone", placeholder="+1 555 0100")
            skills = c4.text_input("Skills", placeholder="Camera, Audio, Editing")

            if st.form_submit_button("Add Member", use_container_width=True, type="primary"):
                if not name.strip():
                    st.error("Name is required.")
                else:
                    db.add_member(name.strip(), email, phone, skills)
                    st.success(f"Member '{name}' added!")
                    st.rerun()

    st.divider()

    members = db.get_members(active_only=False)
    if not members:
        st.info("No members yet. Add your first team member above.")
    else:
        st.subheader(f"Roster ({len(members)})")
        for m in members:
            status_text = "Active" if m["active"] else "Inactive"
            with st.expander(f"👤 {m['name']}  —  {status_text}"):
                c1, c2 = st.columns(2)
                new_name = c1.text_input("Name", value=m["name"], key=f"n_{m['id']}")
                new_email = c2.text_input("Email", value=m["email"] or "", key=f"e_{m['id']}")
                new_phone = c1.text_input("Phone", value=m["phone"] or "", key=f"p_{m['id']}")
                new_skills = c2.text_input("Skills", value=m["skills"] or "", key=f"s_{m['id']}")
                new_active = st.checkbox("Active", value=bool(m["active"]), key=f"a_{m['id']}")

                c1, c2 = st.columns(2)
                if c1.button("💾 Save", key=f"save_{m['id']}", use_container_width=True, type="primary"):
                    db.update_member(m["id"], new_name, new_email, new_phone, new_skills, int(new_active))
                    st.success("Updated!")
                    st.rerun()
                if c2.button("🗑️ Delete", key=f"delm_{m['id']}", use_container_width=True):
                    db.delete_member(m["id"])
                    st.rerun()


# =========================================================
# ASSIGN TASKS
# =========================================================
elif page == "✅ Assign Tasks":
    header("Task Assignment", "Assign team members to event tasks")

    events = db.get_events()
    members = db.get_members()

    if not events:
        st.warning("Create an event first in the **Events** tab.")
        st.stop()
    if not members:
        st.warning("Add team members first in the **Members** tab.")
        st.stop()

    event_map = {f"{e['title']} — {e['event_date']}": e["id"] for e in events}
    selected_event_label = st.selectbox("Select Event", list(event_map.keys()))
    selected_event_id = event_map[selected_event_label]

    st.divider()

    with st.expander("➕ Add Task / Assignment", expanded=True):
        with st.form("add_task_form", clear_on_submit=True):
            c1, c2 = st.columns(2)
            task_name = c1.text_input("Task Name *", placeholder="Camera 1 Operator")
            task_type = c2.selectbox("Task Type", TASK_TYPES)

            member_map = {"— Unassigned —": None}
            member_map.update({m["name"]: m["id"] for m in members})
            assigned_name = c1.selectbox("Assign To", list(member_map.keys()))
            status = c2.selectbox("Status", STATUS_OPTIONS)

            notes = st.text_area("Notes", placeholder="Any specific instructions...")

            if st.form_submit_button("Add Task", use_container_width=True, type="primary"):
                if not task_name.strip():
                    st.error("Task name is required.")
                else:
                    db.add_task(
                        selected_event_id,
                        task_name.strip(),
                        task_type,
                        member_map[assigned_name],
                        notes,
                        status,
                    )
                    st.success("Task added!")
                    st.rerun()

    st.divider()
    st.subheader("📋 Tasks for this Event")

    tasks = db.get_tasks_for_event(selected_event_id)
    if not tasks:
        st.info("No tasks yet for this event.")
    else:
        for t in tasks:
            c1, c2 = st.columns([4, 1])
            with c1:
                st.markdown(f"""
                <div class="card">
                    <div class="card-title">{t['task_name']} &nbsp; {status_badge(t['status'])}</div>
                    <div class="card-meta">
                        🏷️ {t['task_type'] or '—'} &nbsp;•&nbsp; 👤 {t['member_name'] or 'Unassigned'}
                    </div>
                    {f'<div class="card-meta" style="margin-top:0.4rem;">📝 {t["notes"]}</div>' if t['notes'] else ''}
                </div>
                """, unsafe_allow_html=True)
            with c2:
                new_status = st.selectbox(
                    "Update",
                    STATUS_OPTIONS,
                    index=STATUS_OPTIONS.index(t["status"]) if t["status"] in STATUS_OPTIONS else 0,
                    key=f"st_{t['id']}",
                    label_visibility="collapsed",
                )
                if new_status != t["status"]:
                    db.update_task(
                        t["id"], t["task_name"], t["task_type"],
                        t["assigned_member_id"], t["notes"], new_status,
                    )
                    st.rerun()
                if st.button("🗑️", key=f"delt_{t['id']}", use_container_width=True):
                    db.delete_task(t["id"])
                    st.rerun()

    st.divider()
    with st.expander("📤 Export Tasks as CSV"):
        if tasks:
            df = pd.DataFrame(tasks)[["task_name", "task_type", "member_name", "status", "notes"]]
            df.columns = ["Task", "Type", "Assigned To", "Status", "Notes"]
            st.dataframe(df, use_container_width=True, hide_index=True)
            st.download_button(
                "Download CSV",
                df.to_csv(index=False).encode("utf-8"),
                file_name=f"tasks_event_{selected_event_id}.csv",
                mime="text/csv",
            )

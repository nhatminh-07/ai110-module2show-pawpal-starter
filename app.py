import streamlit as st

from models import Owner, Pet, Task
from scheduler import Scheduler

st.set_page_config(page_title="PawPal+", page_icon="P", layout="centered")

st.title("PawPal+")

st.markdown(
    """
Welcome to PawPal+.

This version includes the first full backend implementation for pet-care planning:
it captures owner and pet details, stores tasks, builds a daily plan, and explains why
each task was chosen.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet based on constraints like time, priority, and preferences.
"""
    )

with st.expander("What this demo does", expanded=True):
    st.markdown(
        """
This app currently lets you:
- enter owner and pet details
- add pet care tasks with duration, priority, category, and timing preferences
- generate a simple daily schedule
- view the scheduler's reasoning for the chosen plan
"""
    )

st.divider()

st.subheader("Owner and Pet")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")

col1, col2 = st.columns(2)
with col1:
    species = st.selectbox("Species", ["dog", "cat", "other"])
    pet_age = st.number_input("Pet age", min_value=0, max_value=30, value=3)
with col2:
    available_minutes = st.number_input(
        "Owner available time today (minutes)",
        min_value=1,
        max_value=480,
        value=90,
    )
    owner_preferences = st.multiselect(
        "Preferred task categories",
        ["walk", "feeding", "meds", "enrichment", "grooming"],
        default=["walk", "feeding"],
    )

pet_notes = st.text_area(
    "Pet care notes",
    value="Enjoys short walks, meals on time, and puzzle-based enrichment.",
)

st.markdown("### Tasks")
st.caption("Add tasks below. These will be passed into the scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col3, col4, col5 = st.columns(3)
with col3:
    task_title = st.text_input("Task title", value="Morning walk")
with col4:
    category = st.selectbox("Category", ["walk", "feeding", "meds", "enrichment", "grooming"])
with col5:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)

col6, col7, col8 = st.columns(3)
with col6:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col7:
    preferred_time = st.selectbox("Preferred time", ["any", "morning", "afternoon", "evening"])
with col8:
    required = st.checkbox("Required", value=False)

if st.button("Add task"):
    st.session_state.tasks.append(
        {
            "title": task_title,
            "category": category,
            "duration_minutes": int(duration),
            "priority": priority,
            "preferred_time": preferred_time,
            "required": required,
        }
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a daily plan from the current task list.")

if st.button("Generate schedule"):
    owner = Owner(
        name=owner_name,
        available_minutes=int(available_minutes),
        preferences=owner_preferences,
    )
    pet = Pet(name=pet_name, species=species, age=int(pet_age), notes=pet_notes)
    tasks = [
        Task(
            title=item["title"],
            category=item["category"],
            duration_minutes=item["duration_minutes"],
            priority=item["priority"],
            preferred_time=item["preferred_time"],
            required=item["required"],
        )
        for item in st.session_state.tasks
    ]

    scheduler = Scheduler()
    plan = scheduler.build_plan(owner, pet, tasks)

    st.markdown("### Daily Plan")
    st.write(pet.get_profile())

    if plan.scheduled_tasks:
        for item in plan.scheduled_tasks:
            st.markdown(f"**{item.start_time}-{item.end_time} | {item.task.title}**")
            st.write(
                f"Category: {item.task.category} | Duration: {item.task.duration_minutes} minutes"
            )
            st.caption(item.reason)
        st.success(
            f"Scheduled {len(plan.scheduled_tasks)} task(s) for {plan.total_minutes} minutes."
        )
        st.info(f"Remaining owner time: {plan.get_remaining_time()} minutes.")
    else:
        st.warning("No tasks fit the available time today.")

    st.markdown("### Why This Plan Was Chosen")
    st.text(scheduler.explain_plan(plan))

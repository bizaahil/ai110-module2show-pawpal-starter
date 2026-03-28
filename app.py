import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")

# --- Step 1: Owner & Pet Setup ---
st.subheader("Owner & Pet Info")

col1, col2 = st.columns(2)
with col1:
    owner_name = st.text_input("Owner name", value="Jordan")
    available_time = st.number_input("Available minutes per day", min_value=10, max_value=480, value=90)
with col2:
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "rabbit", "other"])
    special_needs = st.text_input("Special needs (optional)", value="")

# --- Step 2: Persist Owner in session state ---
if "owner" not in st.session_state:
    st.session_state.owner = None

if st.button("Save Owner & Pet"):
    pet = Pet(
        name=pet_name,
        species=species,
        special_needs=special_needs if special_needs else None,
        age=0
    )
    if st.session_state.owner is None:
        # First save — create a new owner
        owner = Owner(name=owner_name, available_minutes_per_day=int(available_time))
        st.session_state.owner = owner
    else:
        # Owner already exists — update their info and keep existing pets/tasks
        st.session_state.owner.name = owner_name
        st.session_state.owner.available_minutes_per_day = int(available_time)

    # Only add the pet if a pet with that name doesn't already exist
    existing_names = [p.name for p in st.session_state.owner.pets]
    if pet_name not in existing_names:
        st.session_state.owner.add_pet(pet)
        st.success(f"Added pet {pet_name} ({species}) to {owner_name}'s profile.")
    else:
        st.info(f"{pet_name} is already in the system. Owner info updated.")

st.divider()

# --- Step 3: Add Tasks ---
st.subheader("Add Tasks")

if st.session_state.owner is None:
    st.info("Save an owner and pet above before adding tasks.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        task_title = st.text_input("Task name", value="Morning walk")
    with col2:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
    with col3:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

    col4, col5, col6 = st.columns(3)
    with col4:
        time_slot = st.selectbox("Time slot", ["anytime", "morning", "afternoon", "evening"])
    with col5:
        frequency = st.selectbox("Frequency", ["daily", "weekly"])
    with col6:
        recur_day = None
        if frequency == "weekly":
            day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
            recur_day = day_names.index(st.selectbox("Repeat on", day_names))

    if st.button("Add task"):
        task = Task(
            name=task_title,
            category="general",
            duration_minutes=int(duration),
            priority=priority,
            time_slot=time_slot,
            frequency=frequency,
            recur_day=recur_day,
        )
        # Add task to the first pet
        st.session_state.owner.pets[0].add_task(task)
        st.success(f"Added task: {task_title}")

    # --- Filter controls ---
    st.markdown("**Filter tasks**")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        pet_names = [p.name for p in st.session_state.owner.pets]
        filter_pet = st.selectbox("Show tasks for pet", ["All"] + pet_names, key="filter_pet")
    with col_f2:
        filter_status = st.selectbox("Show by status", ["All", "Pending", "Completed"], key="filter_status")

    # Show current tasks with filters applied
    scheduler_preview = Scheduler(st.session_state.owner)
    all_tasks = st.session_state.owner.get_all_tasks()
    filtered = scheduler_preview.filter_tasks(
        all_tasks,
        pet_name=filter_pet if filter_pet != "All" else None,
        status=filter_status.lower() if filter_status != "All" else None,
    )
    if filtered:
        st.write("Current tasks:")
        st.table([
            {
                "Task": t.name,
                "Duration (min)": t.duration_minutes,
                "Priority": t.priority,
                "Time Slot": t.time_slot,
                "Frequency": t.frequency,
                "Done": t.is_completed,
            }
            for t in filtered
        ])
    else:
        st.info("No tasks match the current filter.")

st.divider()

# --- Step 4: Generate Schedule ---
st.subheader("Generate Today's Schedule")

if st.session_state.owner is None:
    st.info("Save an owner and pet above to generate a schedule.")
elif not st.session_state.owner.get_all_tasks():
    st.info("Add at least one task before generating a schedule.")
else:
    if st.button("Generate schedule"):
        scheduler = Scheduler(st.session_state.owner)
        plan = scheduler.generate_plan()

        st.success(f"Plan generated for {plan.date} — {plan.total_duration} of {st.session_state.owner.get_available_time()} minutes used.")

        if plan.conflicts:
            st.markdown("### ⚠️ Conflicts Detected")
            for c in plan.conflicts:
                st.warning(c)

        st.markdown("### Today's Plan")
        for task in plan.scheduled_tasks:
            status = "✅" if task.is_completed else "⬜"
            slot_label = f" `@{task.time_slot}`" if task.time_slot != "anytime" else ""
            st.markdown(f"{status} **{task.name}**{slot_label} — {task.duration_minutes} min `[{task.priority}]`")

        st.markdown("### Reasoning")
        st.info(plan.explanation)

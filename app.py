from datetime import date, datetime, timedelta

import streamlit as st
from pawpal_system import Pet, Task, User, Schedule, Priority
st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")


def remove_task_everywhere(user: User, schedule: Schedule, task_id: str) -> None:
    """Remove a task from its schedule and from the owning pet's task list."""
    task = next((t for t in schedule.tasks if t.task_id == task_id), None)
    schedule.remove_task(task_id)
    if task is not None:
        pet = next((p for p in user.pets if p.pet_id == task.pet_id), None)
        if pet is not None:
            pet.tasks = [t for t in pet.tasks if t.task_id != task_id]

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Owner ---
st.subheader("Owner")
owner_name = st.text_input("Owner name", value="")

# Create the User once per session; keep it in the vault instead of rebuilding
# it (and losing pets/schedules) on every rerun.
if "user" not in st.session_state:
    st.session_state.user = User(
        user_id="owner-1",
        name=owner_name,
        email="",
        phone_number="",
        address="",
    )
user: User = st.session_state.user
user.name = owner_name  # keep the object's name in sync without recreating it

st.divider()

# --- Add a Pet ---
st.subheader("Add a Pet")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

if st.button("Add pet"):
    # pet_id derived from current pet count; fine for a single-session demo
    # but not collision-safe if pets are ever removed.
    pet = Pet(
        pet_id=f"pet-{len(user.pets) + 1}",
        animal_type=species,
        name=pet_name,
        owner_id=user.user_id,
    )
    user.add_pet(pet)  # mutates user.pets in place, so it persists via session_state.user

if user.pets:
    st.write("Current pets:")
    st.table([{"pet_id": p.pet_id, "name": p.name, "species": p.animal_type} for p in user.pets])
else:
    st.info("No pets yet. Add one above.")

st.divider()

# --- Schedule a Task ---
st.subheader("Schedule a Task")
st.caption("Tasks are added to today's schedule for the selected pet.")

if not user.pets:
    st.info("Add a pet first before scheduling a task.")
else:
    col1, col2, col3 = st.columns(3)
    with col1:
        # Selectbox stores pet_id (stable key); format_func just controls the
        # label shown to the user so we don't have to store Pet objects as options.
        selected_pet_id = st.selectbox(
            "Pet", options=[p.pet_id for p in user.pets],
            format_func=lambda pid: next(p.name for p in user.pets if p.pet_id == pid),
        )
    with col2:
        task_title = st.text_input("Task title", value="Morning walk")
    with col3:
        duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)

    col4, col5 = st.columns(2)
    with col4:
        priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
    with col5:
        start_time = st.text_input("Start time (HH:MM)", value="09:00")

    if st.button("Add task"):
        pet = next(p for p in user.pets if p.pet_id == selected_pet_id)
        today = date.today().isoformat()

        # Find-or-create today's Schedule, mirroring the lookup pattern used
        # in User.schedule_pet_walk, but generalized to any task (not just walks).
        schedule = next((s for s in user.schedules if s.schedule_date == today), None)
        if schedule is None:
            schedule = Schedule(
                schedule_id=f"{user.user_id}-{today}",
                schedule_date=today,
                owner_id=user.user_id,
            )
            user.schedules.append(schedule)

        # Task only stores a start_time/end_time string pair, so compute end_time
        # here from the chosen start_time + duration rather than asking for it directly.
        start = datetime.strptime(start_time, "%H:%M")
        end = start + timedelta(minutes=int(duration))

        task = Task.create(
            task_id=f"{pet.pet_id}-task-{len(schedule.tasks) + 1}",
            task_description=task_title,
            task_duration=int(duration),
            task_priority=Priority(priority),
            pet_id=pet.pet_id,
            start_time=start.strftime("%H:%M"),
            end_time=end.strftime("%H:%M"),
        )
        conflict_warnings = schedule.find_conflicts(candidate=task)
        schedule.add_task(task)
        pet.tasks.append(task)  # keep Pet.tasks in sync, same as schedule_pet_walk does
        if conflict_warnings:
            for warning in conflict_warnings:
                st.warning(warning)
        else:
            st.success(f"'{task_title}' added to today's schedule.")

    today = date.today().isoformat()
    todays_schedule = next((s for s in user.schedules if s.schedule_date == today), None)
    if todays_schedule and todays_schedule.tasks:
        st.write("Today's tasks:")

        conflict_pairs = todays_schedule.find_conflict_pairs()
        if conflict_pairs:
            st.error(f"⚠️ {len(conflict_pairs)} scheduling conflict(s) found today. Resolve by removing one of the overlapping tasks:")
            for i, (t1, t2) in enumerate(conflict_pairs):
                with st.container(border=True):
                    st.warning(
                        f"'{t1.task_description}' ({t1.start_time}-{t1.end_time}) overlaps with "
                        f"'{t2.task_description}' ({t2.start_time}-{t2.end_time})"
                    )
                    rc1, rc2 = st.columns(2)
                    with rc1:
                        if st.button(f"Remove '{t1.task_description}'", key=f"remove_{t1.task_id}_{i}"):
                            remove_task_everywhere(user, todays_schedule, t1.task_id)
                            st.rerun()
                    with rc2:
                        if st.button(f"Remove '{t2.task_description}'", key=f"remove_{t2.task_id}_{i}"):
                            remove_task_everywhere(user, todays_schedule, t2.task_id)
                            st.rerun()
        else:
            st.success("No scheduling conflicts today.")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            pet_filter = st.selectbox(
                "Filter by pet",
                options=["All"] + [p.pet_id for p in user.pets],
                format_func=lambda pid: "All" if pid == "All" else next(
                    p.name for p in user.pets if p.pet_id == pid
                ),
            )
        with col_f2:
            status_filter = st.selectbox("Filter by status", ["All", "pending", "complete"])
        with col_f3:
            sort_by_time = st.checkbox("Sort by time")

        filtered_tasks = todays_schedule.filter_tasks(
            pet_id=None if pet_filter == "All" else pet_filter,
            status=None if status_filter == "All" else status_filter,
        )
        if sort_by_time:
            filtered_tasks = todays_schedule.sort_by_time(filtered_tasks)

        st.table(
            [
                {
                    "pet_id": t.pet_id,
                    "title": t.task_description,
                    "priority": t.task_priority.value,
                    "start": t.start_time,
                    "end": t.end_time,
                    "status": t.get_status(),
                    "recurrence": t.recurrence,
                }
                for t in filtered_tasks
            ]
        )

        pending_tasks = [t for t in filtered_tasks if t.get_status() == "pending"]
        if pending_tasks:
            col_c1, col_c2 = st.columns([3, 1])
            with col_c1:
                complete_task_id = st.selectbox(
                    "Mark a task complete",
                    options=[t.task_id for t in pending_tasks],
                    format_func=lambda tid: next(
                        t.task_description for t in pending_tasks if t.task_id == tid
                    ),
                )
            with col_c2:
                st.write("")
                st.write("")
                if st.button("Mark complete"):
                    next_task = user.complete_task(complete_task_id)
                    if next_task is not None:
                        st.success(f"Next occurrence scheduled for {next_task.due_date}")
    else:
        st.info("No tasks scheduled for today yet.")

st.divider()

# --- Schedule a Recurring Task ---
st.subheader("Schedule a Recurring Task")
st.caption("Automatically creates a task for each occurrence over the given date range.")

if not user.pets:
    st.info("Add a pet first before scheduling a recurring task.")
else:
    col_r1, col_r2, col_r3 = st.columns(3)
    with col_r1:
        recur_pet_id = st.selectbox(
            "Pet", options=[p.pet_id for p in user.pets],
            format_func=lambda pid: next(p.name for p in user.pets if p.pet_id == pid),
            key="recur_pet",
        )
    with col_r2:
        recur_title = st.text_input("Task title", value="Feed", key="recur_title")
    with col_r3:
        recur_duration = st.number_input(
            "Duration (minutes)", min_value=1, max_value=240, value=15, key="recur_duration"
        )

    col_r4, col_r5, col_r6, col_r7 = st.columns(4)
    with col_r4:
        recur_priority = st.selectbox("Priority", ["low", "medium", "high"], index=1, key="recur_priority")
    with col_r5:
        # time_input forces a valid HH:MM selection instead of free-text entry.
        recur_start_time_value = st.time_input(
            "Start time", value=datetime.strptime("08:00", "%H:%M").time(), key="recur_start_time"
        )
    with col_r6:
        recur_start_date = st.date_input("Start date", value=date.today(), key="recur_start_date")
    with col_r7:
        recur_frequency = st.selectbox("Frequency", ["daily", "weekly"], key="recur_frequency")

    recur_days = st.number_input(
        "Number of occurrences", min_value=1, max_value=52, value=7, key="recur_days"
    )

    if st.button("Add recurring task"):
        pet = next(p for p in user.pets if p.pet_id == recur_pet_id)
        created_tasks, conflict_warnings = user.schedule_recurring_task(
            pet=pet,
            description=recur_title,
            duration=int(recur_duration),
            priority=Priority(recur_priority),
            start_time=recur_start_time_value.strftime("%H:%M"),
            start_date=recur_start_date.isoformat(),
            days=int(recur_days),
            frequency=recur_frequency,
        )
        st.success(f"Created {len(created_tasks)} occurrence(s) of '{recur_title}'.")
        for warning in conflict_warnings:
            st.warning(warning)

    # Derived from the actual schedules/tasks (not the button click above), so this
    # list persists across reruns and reflects removals immediately.
    recurring_series: dict = {}
    for schedule in user.schedules:
        for t in schedule.tasks:
            if t.recurrence != "none":
                key = (t.pet_id, t.task_description, t.recurrence, t.start_time, t.end_time)
                recurring_series.setdefault(key, []).append((schedule, t))

    if recurring_series:
        st.write("Recurring task series:")
        for (pet_id, description, recurrence, start_time, end_time), occurrences in recurring_series.items():
            pet = next((p for p in user.pets if p.pet_id == pet_id), None)
            pet_label = pet.name if pet else pet_id
            with st.container(border=True):
                st.write(
                    f"**{description}** for {pet_label} — {recurrence}, {start_time}-{end_time} "
                    f"({len(occurrences)} occurrence(s))"
                )
                with st.expander("View / remove individual occurrences"):
                    for occ_schedule, occ_task in sorted(occurrences, key=lambda pair: pair[1].due_date):
                        occ_col1, occ_col2 = st.columns([3, 1])
                        with occ_col1:
                            st.write(
                                f"{occ_task.due_date}: {occ_task.start_time}-{occ_task.end_time} "
                                f"({occ_task.get_status()})"
                            )
                        with occ_col2:
                            if st.button("Remove", key=f"remove_occ_{occ_task.task_id}"):
                                remove_task_everywhere(user, occ_schedule, occ_task.task_id)
                                st.rerun()
                series_key = f"remove_series_{pet_id}_{description}_{recurrence}_{start_time}_{end_time}"
                if st.button(f"Remove all occurrences of '{description}'", key=series_key):
                    for occ_schedule, occ_task in occurrences:
                        remove_task_everywhere(user, occ_schedule, occ_task.task_id)
                    st.rerun()

st.divider()

# --- Build Schedule ---
st.subheader("Build Schedule")
st.caption("Generates today's plan from the scheduling logic in pawpal_system.py.")

if st.button("Generate schedule"):
    today = date.today().isoformat()
    todays_schedule = next((s for s in user.schedules if s.schedule_date == today), None)
    if todays_schedule is None:
        st.info("No schedule for today yet. Add a task above first.")
    else:
        # generate_daily_plan() is the single source of truth for ordering
        # the plan (priority first, then start time) — no duplicate logic here.
        plan = todays_schedule.generate_daily_plan()
        if not plan:
            st.info(f"No pending tasks scheduled for {todays_schedule.schedule_date}.")
        else:
            st.success(f"Daily plan for {todays_schedule.schedule_date}: {len(plan)} task(s), ordered by priority then start time.")
            st.table(
                [
                    {
                        "priority": t.task_priority.value,
                        "title": t.task_description,
                        "start": t.start_time,
                        "end": t.end_time,
                        "duration (min)": t.task_duration,
                        "pet_id": t.pet_id,
                    }
                    for t in plan
                ]
            )

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Priority, Schedule, Task


def make_task(
    task_id="t1",
    description="Walk Rex",
    duration=30,
    priority=Priority.MEDIUM,
    pet_id="p1",
    start_time="09:00",
    end_time="09:30",
    recurrence="none",
    due_date="",
) -> Task:
    return Task.create(
        task_id=task_id,
        task_description=description,
        task_duration=duration,
        task_priority=priority,
        pet_id=pet_id,
        start_time=start_time,
        end_time=end_time,
        recurrence=recurrence,
        due_date=due_date,
    )


def test_mark_complete_changes_status():
    task = make_task()
    assert task.get_status() == "pending"

    task.mark_complete()

    assert task.get_status() == "complete"


def test_adding_task_increases_pet_task_count():
    pet = Pet(pet_id="p1", animal_type="dog", name="Rex", owner_id="u1")
    assert len(pet.tasks) == 0

    pet.tasks.append(make_task())

    assert len(pet.tasks) == 1


# --- Sorting correctness ---

def test_sort_by_time_returns_chronological_order():
    schedule = Schedule(schedule_id="s1", schedule_date="2026-07-08", owner_id="u1")
    late = make_task(task_id="t-late", start_time="17:00", end_time="17:30")
    early = make_task(task_id="t-early", start_time="08:00", end_time="08:15")
    mid = make_task(task_id="t-mid", start_time="12:00", end_time="12:30")
    schedule.add_task(late)
    schedule.add_task(early)
    schedule.add_task(mid)

    ordered = schedule.sort_by_time()

    assert [t.task_id for t in ordered] == ["t-early", "t-mid", "t-late"]


def test_sort_by_time_is_stable_for_equal_start_times():
    schedule = Schedule(schedule_id="s1", schedule_date="2026-07-08", owner_id="u1")
    first = make_task(task_id="t-first", start_time="09:00", end_time="09:15")
    second = make_task(task_id="t-second", start_time="09:00", end_time="09:20")
    schedule.add_task(first)
    schedule.add_task(second)

    ordered = schedule.sort_by_time()

    # Equal keys must preserve insertion order (stable sort), not an arbitrary order.
    assert [t.task_id for t in ordered] == ["t-first", "t-second"]


def test_empty_schedule_sorts_to_empty_list():
    schedule = Schedule(schedule_id="s1", schedule_date="2026-07-08", owner_id="u1")

    assert schedule.sort_by_time() == []
    assert schedule.generate_daily_plan() == []


# --- Recurrence logic ---

def test_mark_complete_on_daily_task_creates_next_day_occurrence():
    task = make_task(
        task_id="t-daily",
        recurrence="daily",
        due_date="2026-07-08",
        start_time="09:00",
        end_time="09:30",
    )

    next_task = task.mark_complete()

    assert task.get_status() == "complete"
    assert next_task is not None
    assert next_task.due_date == "2026-07-09"
    assert next_task.recurrence == "daily"
    assert next_task.get_status() == "pending"
    # Same time window carries over to the next occurrence.
    assert next_task.start_time == "09:00"
    assert next_task.end_time == "09:30"


def test_mark_complete_on_weekly_task_creates_next_week_occurrence():
    task = make_task(task_id="t-weekly", recurrence="weekly", due_date="2026-07-08")

    next_task = task.mark_complete()

    assert next_task is not None
    assert next_task.due_date == "2026-07-15"


def test_mark_complete_on_non_recurring_task_returns_none():
    task = make_task(recurrence="none")

    assert task.mark_complete() is None


def test_mark_complete_on_recurring_task_without_due_date_returns_none():
    # Edge case: recurrence is set but due_date was never assigned.
    task = make_task(recurrence="daily", due_date="")

    assert task.mark_complete() is None


# --- Conflict detection ---

def test_find_conflicts_flags_duplicate_times():
    schedule = Schedule(schedule_id="s1", schedule_date="2026-07-08", owner_id="u1")
    existing = make_task(task_id="t-existing", start_time="09:00", end_time="09:30")
    schedule.add_task(existing)

    duplicate = make_task(task_id="t-duplicate", start_time="09:00", end_time="09:30")
    warnings = schedule.find_conflicts(candidate=duplicate)

    assert len(warnings) == 1
    assert "Conflict" in warnings[0]


def test_find_conflicts_flags_partial_overlap():
    schedule = Schedule(schedule_id="s1", schedule_date="2026-07-08", owner_id="u1")
    schedule.add_task(make_task(task_id="t-existing", start_time="09:00", end_time="09:30"))

    overlapping = make_task(task_id="t-overlap", start_time="09:15", end_time="09:45")
    warnings = schedule.find_conflicts(candidate=overlapping)

    assert len(warnings) == 1


def test_find_conflicts_does_not_flag_back_to_back_tasks():
    # Boundary case: one task ends exactly when the next starts (not an overlap).
    schedule = Schedule(schedule_id="s1", schedule_date="2026-07-08", owner_id="u1")
    schedule.add_task(make_task(task_id="t-existing", start_time="09:00", end_time="09:30"))

    back_to_back = make_task(task_id="t-next", start_time="09:30", end_time="10:00")
    warnings = schedule.find_conflicts(candidate=back_to_back)

    assert warnings == []


def test_find_conflict_pairs_across_all_tasks():
    schedule = Schedule(schedule_id="s1", schedule_date="2026-07-08", owner_id="u1")
    schedule.add_task(make_task(task_id="t1", start_time="09:00", end_time="09:30"))
    schedule.add_task(make_task(task_id="t2", start_time="09:15", end_time="09:45"))
    schedule.add_task(make_task(task_id="t3", start_time="12:00", end_time="12:30"))

    pairs = schedule.find_conflict_pairs()

    assert len(pairs) == 1
    ids = {pairs[0][0].task_id, pairs[0][1].task_id}
    assert ids == {"t1", "t2"}


def test_find_conflicts_on_empty_schedule_returns_no_warnings():
    schedule = Schedule(schedule_id="s1", schedule_date="2026-07-08", owner_id="u1")

    assert schedule.find_conflicts() == []
    assert schedule.find_conflict_pairs() == []

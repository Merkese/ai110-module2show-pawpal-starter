# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Paste a sample of your app's CLI or Streamlit output here so a reader can see what a generated plan looks like:

```
# Example:
# Today's Schedule
# =================
# 08:00-08:30 | Rex: Morning walk [medium]
# 09:00-09:15 | Luna: Feed breakfast [high]
# 18:00-18:20 | Rex: Evening playtime [low]
```

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

`tests/test_pawpal.py` covers the core scheduling behaviors:

- **Sorting** — `sort_by_time()` returns tasks in chronological order, preserves insertion order for tasks with identical start times (stable sort), and handles an empty schedule without error.
- **Recurrence** — `mark_complete()` on a daily task files the next occurrence exactly one day later, weekly files one week later, a non-recurring task returns `None`, and a recurring task missing a `due_date` also returns `None` instead of crashing.
- **Conflict detection** — `find_conflicts()`/`find_conflict_pairs()` flag exact duplicate time ranges and partial overlaps, correctly treat back-to-back tasks (one ending exactly when the next starts) as non-conflicting, and return no warnings for an empty schedule.

Sample test output:

```
tests\test_pawpal.py ..............                                                                                                  [100%]

=========================================================== 14 passed in 0.08s ============================================================
```

**Confidence in system reliability: ⭐⭐⭐⭐☆ (4/5)**

All 14 tests pass, and the core scheduling contract — chronological sorting, daily/weekly recurrence, and overlap conflict detection — is verified, including tie-break and boundary cases. Not a full 5 stars because coverage doesn't yet include known risk areas: time strings that aren't zero-padded or that wrap past midnight (e.g., a task ending at `"00:20"`), invalid time input crashing the Streamlit form, and `task_id` collisions after removing and re-adding tasks. Those would need targeted tests before calling the scheduler fully reliable.

## 📐 Smarter Scheduling

> Fill in once you've implemented scheduling logic.

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting |Schedule.sort_by_time(), Schedule.generate_daily_plan() | e.g., sorts by start time and by priority |
| Filtering | Schedule.filter_tasks(pet_id, status) | e.g., Filters by pet and/or status independently |
| Conflict handling |Schedule._times_overlap(), Schedule.find_conflicts(candidate)  | e.g., Flags any overlapping time ranges regardless of pet |
| Recurring tasks |schedule_recurring_task() | e.g., daily vs. weekly occurences |

## 📸 Demo Walkthrough

### Main UI features

- **Owner** — enter the owner's name, kept in session state for the duration of the app run.
- **Add a Pet** — enter a name and species (dog/cat/other) and add the pet to a running table of the owner's pets.
- **Schedule a Task** — pick a pet, title, duration, priority, and start time to add a one-off task to today's schedule. The table of today's tasks can be filtered by pet and by status (pending/complete), and optionally sorted by start time.
- **Schedule a Recurring Task** — pick a pet, title, duration, priority, start time/date, frequency (daily/weekly), and number of occurrences to generate an entire series of tasks at once. Each recurring series can be reviewed, and individual occurrences or the whole series can be removed.
- **Build Schedule** — generate and display today's ordered daily plan (priority first, then start time).
- Tasks can be marked complete from the "Today's tasks" table; completing a recurring task automatically files the next occurrence onto its future date.

### Example workflow

1. Enter an owner name and add a pet (e.g., "Mochi", species "dog").
2. Under **Schedule a Task**, add a task for Mochi — e.g., "Morning walk", 20 minutes, high priority, starting at 09:00.
3. Add a second task that overlaps the first, e.g., "Feed breakfast" starting at 09:10 — the app immediately warns that the two tasks conflict.
4. Scroll to "Today's tasks" to see both tasks listed, with the conflict called out again and a button to remove one of the overlapping tasks.
5. Check "Sort by time" to reorder the table chronologically, or use the pet/status filters.
6. Click **Generate schedule** under **Build Schedule** to see the day's plan ordered by priority (high → medium → low), then by start time within each priority.
7. Optionally, add a recurring task, each occurrence appears on its own day's schedule and can be removed individually or as a group.

### Key Scheduler behaviors shown

- **Sorting** — tasks can be sorted by start time (`Schedule.sort_by_time`), and the daily plan is always sorted by priority then start time (`Schedule.generate_daily_plan`).
- **Conflict warnings** — adding a task that overlaps an existing one triggers an immediate warning (`Schedule.find_conflicts`), and any conflicting pairs already on the schedule are flagged with a one-click resolution option (`Schedule.find_conflict_pairs`).
- **Filtering** — the task list can be filtered by pet and/or completion status (`Schedule.filter_tasks`).
- **Recurrence** — daily/weekly series can be created in bulk (`User.schedule_recurring_task`), and completing a recurring task automatically schedules its next occurrence (`Task.mark_complete`).

### Example CLI Output

```
Daily plan (priority, then time)
=================================
Daily plan for 2026-07-08 (4 task(s)):
- [HIGH] Vet check-in call (12:05-12:20, 15 min) for pet p1
- [MEDIUM] Morning walk (08:00-08:30, 30 min) for pet p1
- [MEDIUM] Litter box cleaning (12:00-12:10, 10 min) for pet p2
- [LOW] Evening playtime (18:00-18:20, 20 min) for pet p1
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or link to a demo video here -->

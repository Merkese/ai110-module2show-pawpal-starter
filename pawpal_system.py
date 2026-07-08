## Logic Layer (Backend)

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from enum import Enum
from typing import List, Optional

#FIX: Added helper class for task priority standards
class Priority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


@dataclass
class Task:
    task_id: str
    task_description: str
    task_duration: int
    task_priority: Priority
    pet_id: str
    start_time: str
    end_time: str
    recurrence: str = "none"  # "none" | "daily" | "weekly"
    due_date: str = ""  # ISO date "YYYY-MM-DD" this occurrence is scheduled for
    _complete: bool = field(default=False, repr=False)

    @classmethod
    def create(
        cls,
        task_id: str,
        task_description: str,
        task_duration: int,
        task_priority: Priority,
        pet_id: str,
        start_time: str,
        end_time: str,
        recurrence: str = "none",
        due_date: str = "",
    ) -> "Task":
        """Create a new Task instance with the given attributes."""
        return cls(
            task_id=task_id,
            task_description=task_description,
            task_duration=task_duration,
            task_priority=task_priority,
            pet_id=pet_id,
            start_time=start_time,
            end_time=end_time,
            recurrence=recurrence,
            due_date=due_date,
        )

    def update_priority(self, priority: Priority) -> None:
        """Update the task's priority level."""
        self.task_priority = priority

    def mark_complete(self) -> Optional["Task"]:
        """Mark complete; if recurring, return a new Task for the next occurrence (else None)."""
        self._complete = True
        if self.recurrence == "none" or not self.due_date:
            return None
        delta = timedelta(days=1) if self.recurrence == "daily" else timedelta(weeks=1)
        next_date = date.fromisoformat(self.due_date) + delta
        return Task.create(
            task_id=f"{self.pet_id}-recur-{next_date.isoformat()}",
            task_description=self.task_description,
            task_duration=self.task_duration,
            task_priority=self.task_priority,
            pet_id=self.pet_id,
            start_time=self.start_time,
            end_time=self.end_time,
            recurrence=self.recurrence,
            due_date=next_date.isoformat(),
        )

    def get_status(self) -> str:
        """Return 'complete' or 'pending' based on the task's completion state."""
        return "complete" if self._complete else "pending"


@dataclass
class Pet:
    pet_id: str
    animal_type: str
    name: str
    owner_id: str
    tasks: List[Task] = field(default_factory=list)

    def get_pet_details(self) -> str:
        """Return a formatted string describing the pet."""
        return f"{self.name} ({self.animal_type}, ID: {self.pet_id})"

    def get_upcoming_tasks(self) -> List[Task]:
        """Return the pet's tasks that are not yet complete."""
        return [task for task in self.tasks if not task._complete]


@dataclass
class Schedule:
    schedule_id: str
    schedule_date: str
    owner_id: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to the schedule."""
        self.tasks.append(task)

    def remove_task(self, task_id: str) -> None:
        """Remove the task with the given task_id from the schedule."""
        self.tasks = [task for task in self.tasks if task.task_id != task_id]

    def view_schedule(self) -> List[Task]:
        """Return the schedule's tasks in their original (unsorted) order."""
        return list(self.tasks)

    def sort_by_time(self, tasks: Optional[List[Task]] = None) -> List[Task]:
        """Return the given tasks (or self.tasks) sorted by start time."""
        return sorted(tasks if tasks is not None else self.tasks, key=lambda task: task.start_time)

    def filter_tasks(
        self, pet_id: Optional[str] = None, status: Optional[str] = None
    ) -> List[Task]:
        """Return the schedule's tasks filtered by pet_id and/or status (None skips that filter)."""
        tasks = self.tasks
        if pet_id is not None:
            tasks = [task for task in tasks if task.pet_id == pet_id]
        if status is not None:
            tasks = [task for task in tasks if task.get_status() == status]
        return list(tasks)

    @staticmethod
    def _times_overlap(start1: str, end1: str, start2: str, end2: str) -> bool:
        """True if two HH:MM ranges overlap."""
        return start1 < end2 and start2 < end1

    def find_conflicts(self, candidate: Optional[Task] = None) -> List[str]:
        """Return warning strings for tasks that overlap in time; never raises."""
        # candidate given: existing tasks are assumed already conflict-free among
        # themselves, so only candidate-vs-existing needs checking (O(n) not O(n^2)).
        warnings: List[str] = []

        if candidate is not None:
            for t in self.tasks:
                if self._times_overlap(
                    candidate.start_time, candidate.end_time, t.start_time, t.end_time
                ):
                    warnings.append(
                        f"Conflict: '{candidate.task_description}' ({candidate.start_time}-{candidate.end_time}) "
                        f"overlaps with '{t.task_description}' ({t.start_time}-{t.end_time})"
                    )
            return warnings

        for i, t1 in enumerate(self.tasks):
            for t2 in self.tasks[i + 1:]:
                if self._times_overlap(t1.start_time, t1.end_time, t2.start_time, t2.end_time):
                    warnings.append(
                        f"Conflict: '{t1.task_description}' ({t1.start_time}-{t1.end_time}) "
                        f"overlaps with '{t2.task_description}' ({t2.start_time}-{t2.end_time})"
                    )
        return warnings

    def find_conflict_pairs(self) -> List[tuple[Task, Task]]:
        """Return (task1, task2) pairs among self.tasks whose times overlap."""
        pairs: List[tuple[Task, Task]] = []
        for i, t1 in enumerate(self.tasks):
            for t2 in self.tasks[i + 1:]:
                if self._times_overlap(t1.start_time, t1.end_time, t2.start_time, t2.end_time):
                    pairs.append((t1, t2))
        return pairs

    def generate_daily_plan(self) -> List[Task]:
        """Return incomplete tasks sorted by priority then start time."""
        priority_order = {Priority.HIGH: 0, Priority.MEDIUM: 1, Priority.LOW: 2}
        incomplete_tasks = [task for task in self.tasks if not task._complete]
        return sorted(
            incomplete_tasks,
            key=lambda task: (priority_order[task.task_priority], task.start_time),
        )

    def explain_plan(self) -> str:
        """Return an easily readable summary of the daily plan."""
        plan = self.generate_daily_plan()
        if not plan:
            return f"No pending tasks scheduled for {self.schedule_date}."

        lines = [f"Daily plan for {self.schedule_date} ({len(plan)} task(s)):"]
        for task in plan:
            lines.append(
                f"- [{task.task_priority.value.upper()}] {task.task_description} "
                f"({task.start_time}-{task.end_time}, {task.task_duration} min) "
                f"for pet {task.pet_id}"
            )
        return "\n".join(lines)


class User:
    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        phone_number: str,
        address: str,
    ) -> None:
        """Initialize a User with their contact info and empty pet/schedule lists."""
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.address = address
        self.pets: List[Pet] = []
        self.schedules: List[Schedule] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the user's list of pets."""
        self.pets.append(pet)

    def schedule_pet_walk(self, pet: Pet, date: str) -> Schedule:
        """Schedule a walk task for the pet on the given date, creating the schedule if needed."""
        schedule = next(
            (s for s in self.schedules if s.schedule_date == date),
            None,
        )
        if schedule is None:
            schedule = Schedule(
                schedule_id=f"{self.user_id}-{date}",
                schedule_date=date,
                owner_id=self.user_id,
            )
            self.schedules.append(schedule)

        task = Task.create(
            task_id=f"{pet.pet_id}-walk-{len(schedule.tasks)}",
            task_description=f"Walk {pet.name}",
            task_duration=30,
            task_priority=Priority.MEDIUM,
            pet_id=pet.pet_id,
            start_time="09:00",
            end_time="09:30",
        )
        schedule.add_task(task)
        pet.tasks.append(task)
        return schedule

    def track_appointments(self) -> List[Task]:
        """Return all tasks across all of the user's schedules."""
        appointments: List[Task] = []
        for schedule in self.schedules:
            appointments.extend(schedule.tasks)
        return appointments

    def get_today_tasks(self) -> List[Task]:
        """Return today's generated daily plan, or an empty list if no schedule exists for today."""
        # Delegates to the matching Schedule's generate_daily_plan(),
        # which is the single source of truth for plan generation.
        today = date.today().isoformat()
        for schedule in self.schedules:
            if schedule.schedule_date == today:
                return schedule.generate_daily_plan()
        return []

    def _find_or_create_schedule(self, schedule_date: str) -> Schedule:
        """Return the Schedule for schedule_date, creating one if it doesn't exist."""
        schedule = next((s for s in self.schedules if s.schedule_date == schedule_date), None)
        if schedule is None:
            schedule = Schedule(
                schedule_id=f"{self.user_id}-{schedule_date}",
                schedule_date=schedule_date,
                owner_id=self.user_id,
            )
            self.schedules.append(schedule)
        return schedule

    def complete_task(self, task_id: str) -> Optional[Task]:
        """Mark task_id complete and file its auto-generated next occurrence, if recurring."""
        for schedule in self.schedules:
            task = next((t for t in schedule.tasks if t.task_id == task_id), None)
            if task is None:
                continue
            next_task = task.mark_complete()
            if next_task is None:
                return None
            next_schedule = self._find_or_create_schedule(next_task.due_date)
            next_schedule.add_task(next_task)
            pet = next((p for p in self.pets if p.pet_id == next_task.pet_id), None)
            if pet is not None:
                pet.tasks.append(next_task)
            return next_task
        return None

    def schedule_recurring_task(
        self,
        pet: Pet,
        description: str,
        duration: int,
        priority: Priority,
        start_time: str,
        start_date: str,
        days: int = 7,
        frequency: str = "daily",
    ) -> tuple[List[Task], List[str]]:
        """Create `days` recurring occurrences starting at start_date; return (tasks, conflict_warnings)."""
        start = datetime.strptime(start_time, "%H:%M")
        end = start + timedelta(minutes=int(duration))
        end_time = end.strftime("%H:%M")

        step = timedelta(days=1) if frequency == "daily" else timedelta(weeks=1)
        base_date = date.fromisoformat(start_date)

        created_tasks: List[Task] = []
        warnings: List[str] = []
        for i in range(days):
            occurrence_date = base_date + step * i
            task = Task.create(
                task_id=f"{pet.pet_id}-recur-{occurrence_date.isoformat()}",
                task_description=description,
                task_duration=int(duration),
                task_priority=priority,
                pet_id=pet.pet_id,
                start_time=start_time,
                end_time=end_time,
                recurrence=frequency,
                due_date=occurrence_date.isoformat(),
            )
            schedule = self._find_or_create_schedule(occurrence_date.isoformat())
            warnings.extend(schedule.find_conflicts(candidate=task))
            schedule.add_task(task)
            pet.tasks.append(task)
            created_tasks.append(task)

        return created_tasks, warnings

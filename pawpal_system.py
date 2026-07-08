## Logic Layer (Backend)

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date
from enum import Enum
from typing import List

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
        )

    def update_priority(self, priority: Priority) -> None:
        """Update the task's priority level."""
        self.task_priority = priority

    def mark_complete(self) -> None:
        """Mark the task as complete."""
        self._complete = True

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
        """Return the schedule's tasks sorted by start time."""
        return sorted(self.tasks, key=lambda task: task.start_time)

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

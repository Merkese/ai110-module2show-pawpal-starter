## Logic Layer (Backend)

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Task:
    task_id: str
    task_description: str
    task_duration: int
    task_priority: str
    _complete: bool = field(default=False, repr=False)

    def create_task(self) -> "Task":
        pass

    def update_priority(self, priority: str) -> None:
        pass

    def mark_complete(self) -> None:
        pass

    def get_status(self) -> str:
        pass


@dataclass
class Pet:
    pet_id: str
    animal_type: str
    name: str
    owner_id: str

    def get_pet_details(self) -> str:
        pass

    def get_upcoming_tasks(self) -> List[Task]:
        pass


@dataclass
class Schedule:
    schedule_id: str
    schedule_date: str
    task_id: str
    start_time: str
    end_time: str
    owner_id: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task_id: str) -> None:
        pass

    def view_schedule(self) -> List[Task]:
        pass

    def generate_daily_plan(self) -> List[Task]:
        pass

    def explain_plan(self) -> str:
        pass


class User:
    def __init__(
        self,
        user_id: str,
        name: str,
        email: str,
        phone_number: str,
        address: str,
    ) -> None:
        self.user_id = user_id
        self.name = name
        self.email = email
        self.phone_number = phone_number
        self.address = address
        self.pets: List[Pet] = []
        self.schedule: Optional[Schedule] = None

    def add_pet(self, pet: Pet) -> None:
        pass

    def schedule_pet_walk(self, pet: Pet, date: str) -> Schedule:
        pass

    def track_appointments(self) -> List[Task]:
        pass

    def get_today_tasks(self) -> List[Task]:
        pass

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from pawpal_system import Pet, Priority, Task


def make_task() -> Task:
    return Task.create(
        task_id="t1",
        task_description="Walk Rex",
        task_duration=30,
        task_priority=Priority.MEDIUM,
        pet_id="p1",
        start_time="09:00",
        end_time="09:30",
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

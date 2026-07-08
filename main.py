## Temporary testing grounds

from datetime import date

from pawpal_system import Pet, Priority, Schedule, Task, User
# FIX: Not displaying info within streamlit
user = User(
    user_id="u1",
    name="Jamie Rivera",
    email="jamie@example.com",
    phone_number="555-0100",
    address="123 Main St",
)
# FIX: Pet is called specifically by its pet_id in UI, not name
dog = Pet(pet_id="p1", animal_type="Dog", name="Rex", owner_id=user.user_id)
cat = Pet(pet_id="p2", animal_type="Cat", name="Luna", owner_id=user.user_id)
user.add_pet(dog)
user.add_pet(cat)

today = date.today().isoformat()
schedule = Schedule(schedule_id=f"{user.user_id}-{today}", schedule_date=today, owner_id=user.user_id)
user.schedules.append(schedule)

tasks = [
    # FIX: added out of order (evening before morning) to exercise sort_by_time
    Task.create(
        task_id="t3",
        task_description="Evening playtime",
        task_duration=20,
        task_priority=Priority.LOW,
        pet_id=dog.pet_id,
        start_time="18:00",
        end_time="18:20",
    ),
    Task.create(
        task_id="t2",
        task_description="Feed breakfast",
        task_duration=15,
        task_priority=Priority.HIGH,
        pet_id=cat.pet_id,
        start_time="09:00",
        end_time="09:15",
    ),
    Task.create(
        task_id="t4",
        task_description="Litter box cleaning",
        task_duration=10,
        task_priority=Priority.MEDIUM,
        pet_id=cat.pet_id,
        start_time="12:00",
        end_time="12:10",
    ),
    Task.create(
        task_id="t1",
        task_description="Morning walk",
        task_duration=30,
        task_priority=Priority.MEDIUM,
        pet_id=dog.pet_id,
        # FIX: implement a day/evening difference
        start_time="08:00",
        end_time="08:30",
    ),
]

for task in tasks:
    schedule.add_task(task)
    pet = dog if task.pet_id == dog.pet_id else cat
    pet.tasks.append(task)

# Mark one task complete so filter_tasks(status=...) has something to filter on.
schedule.tasks[1].mark_complete()

# FIX: added a task overlapping t4 (12:00-12:10) to exercise conflict detection
conflict_task = Task.create(
    task_id="t5",
    task_description="Vet check-in call",
    task_duration=15,
    task_priority=Priority.HIGH,
    pet_id=dog.pet_id,
    start_time="12:05",
    end_time="12:20",
)
conflict_warnings = schedule.find_conflicts(candidate=conflict_task)
schedule.add_task(conflict_task)
dog.tasks.append(conflict_task)


def pet_name_for(task: Task) -> str:
    return dog.name if task.pet_id == dog.pet_id else cat.name


print("Schedule as added (out of order)")
print("=================================")
for task in schedule.view_schedule():
    print(
        f"{task.start_time}-{task.end_time} | {pet_name_for(task)}: {task.task_description} "
        f"[{task.task_priority.value}] ({task.get_status()})"
    )

print("\nSorted by time")
print("==============")
for task in schedule.sort_by_time():
    print(f"{task.start_time}-{task.end_time} | {pet_name_for(task)}: {task.task_description}")

print("\nFiltered: only Luna's (cat) tasks")
print("==================================")
for task in schedule.filter_tasks(pet_id=cat.pet_id):
    print(f"{task.start_time}-{task.end_time} | {task.task_description} ({task.get_status()})")

print("\nFiltered: only pending tasks, sorted by time")
print("=============================================")
pending_sorted = schedule.sort_by_time(schedule.filter_tasks(status="pending"))
for task in pending_sorted:
    print(f"{task.start_time}-{task.end_time} | {pet_name_for(task)}: {task.task_description}")

print("\nDaily plan (priority, then time)")
print("=================================")
print(schedule.explain_plan())

print("\nConflict check for new task (t5, 12:05-12:20)")
print("==============================================")
if conflict_warnings:
    for warning in conflict_warnings:
        print(f"WARNING: {warning}")
else:
    print("No conflicts found.")

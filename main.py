## Temporary testing grounds

from datetime import date

from pawpal_system import Pet, Priority, Schedule, Task, User

user = User(
    user_id="u1",
    name="Jamie Rivera",
    email="jamie@example.com",
    phone_number="555-0100",
    address="123 Main St",
)

dog = Pet(pet_id="p1", animal_type="Dog", name="Rex", owner_id=user.user_id)
cat = Pet(pet_id="p2", animal_type="Cat", name="Luna", owner_id=user.user_id)
user.add_pet(dog)
user.add_pet(cat)

today = date.today().isoformat()
schedule = Schedule(schedule_id=f"{user.user_id}-{today}", schedule_date=today, owner_id=user.user_id)
user.schedules.append(schedule)

tasks = [
    Task.create(
        task_id="t1",
        task_description="Morning walk",
        task_duration=30,
        task_priority=Priority.MEDIUM,
        pet_id=dog.pet_id,
        start_time="08:00",
        end_time="08:30",
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
        task_id="t3",
        task_description="Evening playtime",
        task_duration=20,
        task_priority=Priority.LOW,
        pet_id=dog.pet_id,
        start_time="18:00",
        end_time="18:20",
    ),
]

for task in tasks:
    schedule.add_task(task)
    pet = dog if task.pet_id == dog.pet_id else cat
    pet.tasks.append(task)

print("Today's Schedule")
print("=================")
for task in schedule.view_schedule():
    pet_name = dog.name if task.pet_id == dog.pet_id else cat.name
    print(
        f"{task.start_time}-{task.end_time} | {pet_name}: {task.task_description} "
        f"[{task.task_priority.value}]"
    )

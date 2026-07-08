# PawPal+ Project Reflection

## 1. System Design
1. Users can have one or many pets
2. Users should be able to schedule actions with their pets
3. Users should be able see tasks for today

**a. Initial design**

- Briefly describe your initial UML design.

Classes: User, Pet, Task, Schedule

1. A user can have one or many pets, pets must have an owner, which consist of their simple details of both user and pet.
2. A user has a defined schedule (class 3) consistent with a time duration, time starting and ending, and date
3. tasks (class 4) for each user that are inputed by the user, associated with a date, time, and description of the task. * Maybe can be scheduled (Yes/No statement)
4. A pet may or may not have an assigned clinic


- What classes did you include, and what responsibilities did you assign to each?

## Note: Check the listed features above for accuracy with actual logic file.
1. The User class should be able to add pets, schedule walks with pets, Input Tasks for their pet, and see a list of tasks for a specific pet.

2. The Pet class should allow the user to obtain Pet related details and information. The user should also be allowed to see upcoming tasks for a specific Pet.

3. The Tasks class allows the user to create Tasks, give a specific priority (from high, medium, or low), check a specific task as complete, and receive the current status of a Task.

4. The Schedule class should allow the user to add or remove tasks from their schedule, view the user created schedule, generate a plan based on the schedule the user created, and explain why that plan works for their schedule.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

1. After the first UML creation, I wanted to see if there was any other suggests for the *Schedule* class because I felt it was lacking other attributes. It suggested adding "Start" and "End" times, which I felt made sense and added to the class. (This was later changed)

2. Other changes:

- Added pet_id field to Task 
    - This is to help communicate with mainly the pet class

- Collapse Schedule to single task-list model, move start/end time to Task 
    - This mixed two different task models causing an issue that would not allow for multiple tasks within a day's schedule. (Fixed by switching start_time, end_time to Task and deleting task_id on schedule class)

- Change User.schedule to User.schedules list
    - This was to allow multiple schedule to be created for separate days, so schedules would not be simply overwritten. 

- Convert task_priority to Enum
    - Along with creating the priority helper class, it allows for a standardization of inputs for a priority, instead of having any string. This contributes to the generate_daily_plan method

- Fix Task.create_task to be a classmethod factory
    - Allows for the ability to create tasks without needing an existing one to model off of /modify 

- Resolve duplicate plan generation ownership
    - Decided on an owner to produce today's plan (schedule), instead of having two separate objects doing so (User and Schedule). User now call from schedule's function.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

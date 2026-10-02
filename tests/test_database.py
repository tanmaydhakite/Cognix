from database.task_database import (
    create_task,
    list_tasks,
    complete_task,
    delete_task
)


print("\n--- CREATE TASK ---")

task = create_task(
    "Finish Python assignment",
    "Tomorrow"
)

print(task)


print("\n--- LIST TASKS ---")

tasks = list_tasks()

for task in tasks:
    print(task)


print("\n--- COMPLETE TASK ---")

result = complete_task(task["id"])

print(result)


print("\n--- LIST TASKS AGAIN ---")

tasks = list_tasks()

for task in tasks:
    print(task)
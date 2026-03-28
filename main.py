from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Alex", available_minutes_per_day=90)

dog = Pet(name="Biscuit", species="Dog", age=3)
cat = Pet(name="Mochi", species="Cat", age=5, special_needs="Requires medication twice daily")

# --- Tasks for Biscuit (dog) — added OUT OF ORDER intentionally ---
dog.add_task(Task(name="Dinner Feeding", category="feed",       duration_minutes=10, priority="high",   start_time="17:30"))
dog.add_task(Task(name="Fetch / Play",   category="enrichment", duration_minutes=20, priority="medium", start_time="14:00"))
dog.add_task(Task(name="Morning Walk",   category="walk",       duration_minutes=30, priority="high",   start_time="07:00"))

# --- Tasks for Mochi (cat) ---
cat.add_task(Task(name="Medication",     category="meds",       duration_minutes=5,  priority="high",   start_time="08:00"))
cat.add_task(Task(name="Brush Coat",     category="grooming",   duration_minutes=15, priority="low",    start_time="11:00"))

# --- Add pets to owner ---
owner.add_pet(dog)
owner.add_pet(cat)

scheduler = Scheduler(owner)

# --- Demo 1: Sort all tasks by start_time (HH:MM) ---
all_tasks = owner.get_all_tasks()
sorted_by_time = scheduler.sort_by_time(all_tasks)

print("=" * 40)
print("   TASKS SORTED BY START TIME (HH:MM)")
print("=" * 40)
for task in sorted_by_time:
    print(f"  {task.start_time}  {task.name} ({task.priority})")

# --- Demo 2: Filter by pet name ---
biscuit_tasks = scheduler.filter_tasks(all_tasks, pet_name="Biscuit")
print("\n" + "=" * 40)
print("   FILTER: Biscuit's Tasks Only")
print("=" * 40)
for task in biscuit_tasks:
    print(f"  {task.name} — {task.duration_minutes} min [{task.priority}]")

# --- Demo 3: Filter by completion status ---
print("\n" + "=" * 40)
print("   FILTER: Pending Tasks Only")
print("=" * 40)
pending = scheduler.filter_tasks(all_tasks, status="pending")
for task in pending:
    print(f"  [ ] {task.name}")

# Mark one task complete to show completed filter
all_tasks[0].mark_complete()
completed = scheduler.filter_tasks(all_tasks, status="completed")
print("\n" + "=" * 40)
print("   FILTER: Completed Tasks Only")
print("=" * 40)
for task in completed:
    print(f"  [x] {task.name}")

# --- Demo 4: Recurring task auto-renewal ---
print("\n" + "=" * 40)
print("   RECURRING TASK AUTO-RENEWAL")
print("=" * 40)
print(f"Before: Biscuit has {len(dog.tasks)} task(s)")
print("Marking 'Morning Walk' complete...")
next_task = scheduler.mark_task_complete("Morning Walk")
print(f"After:  Biscuit has {len(dog.tasks)} task(s)")
if next_task:
    print(f"Next occurrence created: '{next_task.name}' due {next_task.due_date}")

print("\nMarking 'Dinner Feeding' complete (weekly task)...")
dog.tasks[0].edit(frequency="weekly")  # temporarily make it weekly for demo
next_weekly = scheduler.mark_task_complete("Dinner Feeding")
if next_weekly:
    print(f"Next occurrence created: '{next_weekly.name}' due {next_weekly.due_date} (+7 days)")

# --- Demo 5: Conflict detection ---
print("\n" + "=" * 40)
print("   CONFLICT DETECTION")
print("=" * 40)

# Two tasks from different pets both scheduled at 08:00
dog.add_task(Task(name="Morning Meds",  category="meds", duration_minutes=5, priority="high", start_time="08:00"))
# Mochi's Medication is also at 08:00 — this should trigger a conflict warning

conflict_tasks = owner.get_all_tasks()
conflicts = scheduler.detect_conflicts(conflict_tasks)
if conflicts:
    for warning in conflicts:
        print(warning)
else:
    print("No conflicts found.")

# --- Demo 6: Full schedule (shows conflicts in plan too) ---
plan = scheduler.generate_plan()
print("\n" + "=" * 40)
print("         TODAY'S SCHEDULE")
print("=" * 40)
plan.display()
print("=" * 40)
print(f"Summary: {plan.get_summary()}")

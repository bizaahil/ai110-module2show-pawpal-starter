from pawpal_system import Owner, Pet, Task, Scheduler

# --- Setup ---
owner = Owner(name="Alex", available_minutes_per_day=90)

dog = Pet(name="Biscuit", species="Dog", age=3)
cat = Pet(name="Mochi", species="Cat", age=5, special_needs="Requires medication twice daily")

# --- Tasks for Biscuit (dog) ---
dog.add_task(Task(name="Morning Walk",   category="walk",       duration_minutes=30, priority="high"))
dog.add_task(Task(name="Dinner Feeding", category="feed",       duration_minutes=10, priority="high"))
dog.add_task(Task(name="Fetch / Play",   category="enrichment", duration_minutes=20, priority="medium"))

# --- Tasks for Mochi (cat) ---
cat.add_task(Task(name="Medication",     category="meds",       duration_minutes=5,  priority="high"))
cat.add_task(Task(name="Brush Coat",     category="grooming",   duration_minutes=15, priority="low"))

# --- Add pets to owner ---
owner.add_pet(dog)
owner.add_pet(cat)

# --- Generate and display today's schedule ---
scheduler = Scheduler(owner)
plan = scheduler.generate_plan()

print("=" * 40)
print("         TODAY'S SCHEDULE")
print("=" * 40)
plan.display()
print("=" * 40)
print(f"Summary: {plan.get_summary()}")

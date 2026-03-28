from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_mark_complete_changes_status():
    """Calling mark_complete() should set is_completed to True."""
    task = Task(name="Morning Walk", category="walk", duration_minutes=30, priority="high")
    assert task.is_completed == False
    task.mark_complete()
    assert task.is_completed == True


def test_add_task_increases_pet_task_count():
    """Adding a task to a Pet should increase its task count by 1."""
    pet = Pet(name="Biscuit", species="Dog", age=3)
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Feeding", category="feed", duration_minutes=10, priority="high"))
    assert len(pet.tasks) == 1


# --- Sorting Correctness ---

def test_sort_by_time_returns_chronological_order():
    """Tasks added out of order should come back sorted earliest start_time first."""
    owner = Owner(name="Alex", available_minutes_per_day=90)
    dog = Pet(name="Biscuit", species="Dog", age=3)
    owner.add_pet(dog)
    scheduler = Scheduler(owner)

    tasks = [
        Task("Dinner",   "feed", 10, "high", start_time="17:30"),
        Task("Walk",     "walk", 30, "high", start_time="07:00"),
        Task("Playtime", "enrichment", 20, "medium", start_time="14:00"),
    ]
    sorted_tasks = scheduler.sort_by_time(tasks)
    times = [t.start_time for t in sorted_tasks]
    assert times == ["07:00", "14:00", "17:30"]


# --- Recurrence Logic ---

def test_daily_task_creates_next_occurrence_for_tomorrow():
    """Marking a daily task complete should auto-create a copy due tomorrow."""
    owner = Owner(name="Alex", available_minutes_per_day=90)
    dog = Pet(name="Biscuit", species="Dog", age=3)
    owner.add_pet(dog)
    scheduler = Scheduler(owner)

    today = str(date.today())
    tomorrow = str(date.today() + timedelta(days=1))
    dog.add_task(Task("Walk", "walk", 30, "high", frequency="daily", due_date=today))

    next_task = scheduler.mark_task_complete("Walk")

    assert next_task is not None
    assert next_task.due_date == tomorrow
    assert next_task.is_completed is False


# --- Conflict Detection ---

def test_conflict_detected_for_same_start_time():
    """Two tasks sharing the same start_time should trigger a conflict warning."""
    owner = Owner(name="Alex", available_minutes_per_day=90)
    dog = Pet(name="Biscuit", species="Dog", age=3)
    owner.add_pet(dog)
    scheduler = Scheduler(owner)

    tasks = [
        Task("Walk", "walk", 30, "high", start_time="07:00"),
        Task("Meds", "meds",  5, "high", start_time="07:00"),
    ]
    conflicts = scheduler.detect_conflicts(tasks)
    assert len(conflicts) == 1
    assert "07:00" in conflicts[0]


def test_no_conflict_when_times_are_different():
    """Tasks at different start_times should produce no conflict warnings."""
    owner = Owner(name="Alex", available_minutes_per_day=90)
    dog = Pet(name="Biscuit", species="Dog", age=3)
    owner.add_pet(dog)
    scheduler = Scheduler(owner)

    tasks = [
        Task("Walk", "walk", 30, "high", start_time="07:00"),
        Task("Meds", "meds",  5, "high", start_time="08:00"),
    ]
    assert scheduler.detect_conflicts(tasks) == []

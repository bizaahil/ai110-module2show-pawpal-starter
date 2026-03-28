from datetime import date, timedelta
import pytest
from pawpal_system import Owner, Pet, Task, Scheduler


# ---------------------------------------------------------------------------
# Helpers — reusable setup so each test starts clean
# ---------------------------------------------------------------------------

def make_owner(minutes=90):
    return Owner(name="Alex", available_minutes_per_day=minutes)

def make_scheduler(minutes=90):
    owner = make_owner(minutes)
    dog = Pet(name="Biscuit", species="Dog", age=3)
    owner.add_pet(dog)
    return owner, dog, Scheduler(owner)


# ===========================================================================
# 1. generate_plan() — priority ordering and time budget
# ===========================================================================

def test_high_priority_tasks_scheduled_before_low():
    """High-priority tasks should appear in the plan before low-priority ones."""
    owner, dog, scheduler = make_scheduler(minutes=60)
    dog.add_task(Task("Brush Coat", "grooming", 20, "low"))
    dog.add_task(Task("Medication",  "meds",     10, "high"))
    dog.add_task(Task("Morning Walk","walk",      30, "high"))

    plan = scheduler.generate_plan()
    names = [t.name for t in plan.scheduled_tasks]

    assert "Medication"   in names
    assert "Morning Walk" in names
    # Low-priority task may or may not fit — but if it does, it comes after high ones
    high_indices = [names.index(n) for n in ["Medication", "Morning Walk"]]
    if "Brush Coat" in names:
        assert names.index("Brush Coat") > max(high_indices)


def test_plan_does_not_exceed_available_time():
    """Total scheduled duration must never exceed the owner's available minutes."""
    owner, dog, scheduler = make_scheduler(minutes=30)
    dog.add_task(Task("Walk",    "walk", 20, "high"))
    dog.add_task(Task("Feeding", "feed", 20, "high"))  # together they exceed 30 min

    plan = scheduler.generate_plan()
    assert plan.total_duration <= 30


def test_low_priority_task_dropped_when_time_is_tight():
    """A low-priority task should be left out when the budget is nearly full."""
    owner, dog, scheduler = make_scheduler(minutes=25)
    dog.add_task(Task("Walk",       "walk",     20, "high"))
    dog.add_task(Task("Brush Coat", "grooming", 15, "low"))  # won't fit after walk

    plan = scheduler.generate_plan()
    names = [t.name for t in plan.scheduled_tasks]
    assert "Walk" in names
    assert "Brush Coat" not in names


# ===========================================================================
# 2. generate_plan() edge case — no tasks
# ===========================================================================

def test_empty_plan_when_no_tasks():
    """generate_plan() on a pet with no tasks should return an empty plan, not crash."""
    owner, dog, scheduler = make_scheduler()
    # No tasks added

    plan = scheduler.generate_plan()
    assert plan.scheduled_tasks == []
    assert plan.total_duration == 0


def test_empty_plan_explanation_message():
    """The explanation should acknowledge that nothing was scheduled."""
    owner, dog, scheduler = make_scheduler()
    plan = scheduler.generate_plan()
    assert "No tasks" in plan.explanation


# ===========================================================================
# 3. sort_by_time() — chronological HH:MM ordering
# ===========================================================================

def test_sort_by_time_orders_correctly():
    """Tasks added out of order should come out sorted earliest first."""
    owner, dog, scheduler = make_scheduler()
    tasks = [
        Task("Dinner",    "feed",        10, "high", start_time="17:30"),
        Task("Nap Check", "enrichment",   5, "low",  start_time="14:00"),
        Task("Walk",      "walk",         30, "high", start_time="07:00"),
        Task("Meds",      "meds",          5, "high", start_time="08:00"),
    ]
    sorted_tasks = scheduler.sort_by_time(tasks)
    times = [t.start_time for t in sorted_tasks]
    assert times == sorted(times)


def test_sort_by_time_single_task():
    """A single task should be returned unchanged."""
    owner, dog, scheduler = make_scheduler()
    tasks = [Task("Walk", "walk", 30, "high", start_time="07:00")]
    assert scheduler.sort_by_time(tasks) == tasks


# ===========================================================================
# 4. filter_tasks() — by pet name and completion status
# ===========================================================================

def test_filter_by_pet_name_returns_only_that_pets_tasks():
    """filter_tasks(pet_name=...) should exclude tasks from other pets."""
    owner = make_owner()
    dog = Pet(name="Biscuit", species="Dog", age=3)
    cat = Pet(name="Mochi",   species="Cat", age=5)
    owner.add_pet(dog)
    owner.add_pet(cat)

    dog.add_task(Task("Walk",       "walk", 30, "high"))
    cat.add_task(Task("Medication", "meds",  5, "high"))

    scheduler = Scheduler(owner)
    all_tasks = owner.get_all_tasks()

    result = scheduler.filter_tasks(all_tasks, pet_name="Biscuit")
    assert len(result) == 1
    assert result[0].name == "Walk"


def test_filter_pending_excludes_completed_tasks():
    """filter_tasks(status='pending') should not include completed tasks."""
    owner, dog, scheduler = make_scheduler()
    t1 = Task("Walk",    "walk", 30, "high")
    t2 = Task("Feeding", "feed", 10, "high")
    t2.mark_complete()
    dog.add_task(t1)
    dog.add_task(t2)

    result = scheduler.filter_tasks(owner.get_all_tasks(), status="pending")
    names = [t.name for t in result]
    assert "Walk"    in names
    assert "Feeding" not in names


def test_filter_completed_returns_only_done_tasks():
    """filter_tasks(status='completed') should return only finished tasks."""
    owner, dog, scheduler = make_scheduler()
    t1 = Task("Walk",    "walk", 30, "high")
    t2 = Task("Feeding", "feed", 10, "high")
    t2.mark_complete()
    dog.add_task(t1)
    dog.add_task(t2)

    result = scheduler.filter_tasks(owner.get_all_tasks(), status="completed")
    assert len(result) == 1
    assert result[0].name == "Feeding"


def test_filter_no_criteria_returns_all():
    """filter_tasks() with no filters should return all tasks unchanged."""
    owner, dog, scheduler = make_scheduler()
    dog.add_task(Task("Walk",    "walk", 30, "high"))
    dog.add_task(Task("Feeding", "feed", 10, "high"))

    all_tasks = owner.get_all_tasks()
    result = scheduler.filter_tasks(all_tasks)
    assert len(result) == len(all_tasks)


# ===========================================================================
# 5. mark_task_complete() — recurring auto-renewal
# ===========================================================================

def test_daily_task_creates_next_occurrence_tomorrow():
    """Completing a daily task should auto-create a copy due tomorrow."""
    owner, dog, scheduler = make_scheduler()
    today = str(date.today())
    tomorrow = str(date.today() + timedelta(days=1))

    dog.add_task(Task("Walk", "walk", 30, "high", frequency="daily", due_date=today))
    next_task = scheduler.mark_task_complete("Walk")

    assert next_task is not None
    assert next_task.due_date == tomorrow
    assert next_task.is_completed is False
    assert next_task.name == "Walk"


def test_weekly_task_creates_next_occurrence_in_seven_days():
    """Completing a weekly task should auto-create a copy due 7 days later."""
    owner, dog, scheduler = make_scheduler()
    today = str(date.today())
    next_week = str(date.today() + timedelta(weeks=1))

    dog.add_task(Task("Bath", "grooming", 20, "low", frequency="weekly", due_date=today))
    next_task = scheduler.mark_task_complete("Bath")

    assert next_task is not None
    assert next_task.due_date == next_week


def test_completing_task_adds_it_to_pets_list():
    """After mark_task_complete(), the pet should have one more task."""
    owner, dog, scheduler = make_scheduler()
    dog.add_task(Task("Walk", "walk", 30, "high", frequency="daily"))

    before = len(dog.tasks)
    scheduler.mark_task_complete("Walk")
    assert len(dog.tasks) == before + 1


def test_mark_nonexistent_task_returns_none():
    """mark_task_complete() on a task that doesn't exist should return None silently."""
    owner, dog, scheduler = make_scheduler()
    result = scheduler.mark_task_complete("Ghost Task")
    assert result is None


# ===========================================================================
# 6. detect_conflicts() — same start_time warning
# ===========================================================================

def test_detect_conflict_when_two_tasks_same_time():
    """Two tasks at the same start_time should produce a conflict warning."""
    owner, dog, scheduler = make_scheduler()
    tasks = [
        Task("Walk", "walk", 30, "high", start_time="07:00"),
        Task("Meds", "meds",  5, "high", start_time="07:00"),
    ]
    conflicts = scheduler.detect_conflicts(tasks)
    assert len(conflicts) == 1
    assert "07:00" in conflicts[0]


def test_no_conflict_when_times_differ():
    """Tasks at different start_times should produce no warnings."""
    owner, dog, scheduler = make_scheduler()
    tasks = [
        Task("Walk", "walk", 30, "high", start_time="07:00"),
        Task("Meds", "meds",  5, "high", start_time="08:00"),
    ]
    assert scheduler.detect_conflicts(tasks) == []


def test_default_start_time_not_flagged_as_conflict():
    """Tasks with the default start_time '00:00' should not be flagged as conflicts."""
    owner, dog, scheduler = make_scheduler()
    tasks = [
        Task("Walk",    "walk", 30, "high"),  # start_time defaults to "00:00"
        Task("Feeding", "feed", 10, "high"),  # same default
    ]
    assert scheduler.detect_conflicts(tasks) == []

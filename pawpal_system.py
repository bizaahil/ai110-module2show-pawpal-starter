from dataclasses import dataclass, field, replace
from datetime import date, timedelta
from typing import Optional


@dataclass
class Task:
    name: str
    category: str            # e.g. "walk", "feed", "meds", "grooming"
    duration_minutes: int
    priority: str            # "high", "medium", or "low"
    frequency: str = "daily" # "daily" or "weekly"
    recur_day: Optional[int] = None  # 0=Mon..6=Sun; only used when frequency="weekly"
    time_slot: str = "anytime"       # "morning", "afternoon", "evening", or "anytime"
    start_time: str = "00:00"        # scheduled start time in "HH:MM" format
    due_date: str = field(default_factory=lambda: str(date.today()))
    is_completed: bool = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.is_completed = True

    def next_occurrence(self) -> "Task":
        """
        Return a new Task instance for the next occurrence of this recurring task.
        - daily  → due_date advances by 1 day  (today + timedelta(days=1))
        - weekly → due_date advances by 7 days (today + timedelta(weeks=1))
        """
        current = date.fromisoformat(self.due_date)
        if self.frequency == "weekly":
            next_date = current + timedelta(weeks=1)
        else:
            next_date = current + timedelta(days=1)
        return replace(self, due_date=str(next_date), is_completed=False)

    def edit(self, **kwargs):
        """Update one or more task attributes by keyword argument."""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: Optional[str] = None
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task_name: str):
        """Remove a task from this pet's task list by name."""
        self.tasks = [t for t in self.tasks if t.name != task_name]

    def get_tasks_by_priority(self) -> list[Task]:
        """Return this pet's tasks sorted from highest to lowest priority."""
        priority_order = {"high": 0, "medium": 1, "low": 2}
        return sorted(self.tasks, key=lambda t: priority_order.get(t.priority, 3))


class Owner:
    def __init__(self, name: str, available_minutes_per_day: int, preferences: Optional[str] = None):
        self.name = name
        self.available_minutes_per_day = available_minutes_per_day
        self.preferences = preferences
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet):
        """Add a pet to this owner's pet list."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str):
        """Remove a pet from this owner's pet list by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def get_available_time(self) -> int:
        """Return the owner's total available minutes per day."""
        return self.available_minutes_per_day

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across all pets."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks


class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def get_all_tasks(self) -> list[Task]:
        """Retrieve all tasks from all of the owner's pets."""
        return self.owner.get_all_tasks()

    def fits_in_day(self, tasks: list[Task]) -> bool:
        """Check if the total duration of tasks fits within the owner's available time."""
        total = sum(t.duration_minutes for t in tasks)
        return total <= self.owner.get_available_time()

    # --- Algorithmic Layer ---

    def filter_tasks(
        self,
        tasks: list[Task],
        pet_name: Optional[str] = None,
        status: Optional[str] = None,
    ) -> list[Task]:
        """
        Return a filtered subset of tasks based on optional criteria.

        Args:
            tasks:    The list of Task objects to filter.
            pet_name: If provided, only tasks belonging to the named pet are kept.
                      Uses object identity (id()) so renamed tasks are not false-matched.
            status:   "pending"   → keep only incomplete tasks (is_completed=False)
                      "completed" → keep only finished tasks  (is_completed=True)
                      None        → keep all tasks regardless of status

        Returns:
            A new list containing only the tasks that match all supplied filters.
        """
        result = tasks
        if pet_name is not None:
            pet_task_ids = {id(t) for pet in self.owner.pets if pet.name == pet_name for t in pet.tasks}
            result = [t for t in result if id(t) in pet_task_ids]
        if status == "pending":
            result = [t for t in result if not t.is_completed]
        elif status == "completed":
            result = [t for t in result if t.is_completed]
        return result

    def mark_task_complete(self, task_name: str) -> Optional[Task]:
        """
        Mark a task complete by name and auto-schedule its next occurrence.

        Searches all pets for the first incomplete task matching task_name.
        If found and the task is recurring (daily or weekly), calls
        next_occurrence() to create a copy with an advanced due_date and
        appends it to the same pet's task list.

        Args:
            task_name: The exact name of the task to mark complete.

        Returns:
            The newly created next-occurrence Task if the task is recurring,
            or None if the task is one-time or was not found.
        """
        for pet in self.owner.pets:
            for task in pet.tasks:
                if task.name == task_name and not task.is_completed:
                    task.mark_complete()
                    if task.frequency in ("daily", "weekly"):
                        next_task = task.next_occurrence()
                        pet.add_task(next_task)
                        return next_task
                    return None
        return None

    def sort_by_time_slot(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks by time slot: morning → afternoon → evening → anytime."""
        slot_order = {"morning": 0, "afternoon": 1, "evening": 2, "anytime": 3}
        return sorted(tasks, key=lambda t: slot_order.get(t.time_slot, 3))

    def sort_by_time(self, tasks: list[Task]) -> list[Task]:
        """
        Sort tasks chronologically by their start_time field.

        Uses a lambda key on the 'HH:MM' string. Zero-padded 24-hour format
        means lexicographic (alphabetical) order is identical to chronological
        order, so no parsing is needed.

        Args:
            tasks: The list of Task objects to sort.

        Returns:
            A new list sorted earliest start_time first.
        """
        return sorted(tasks, key=lambda t: t.start_time)

    def is_task_due_today(self, task: Task) -> bool:
        """
        Return True if a task should run today.
        - daily tasks always run
        - weekly tasks only run on their recur_day (0=Mon..6=Sun)
        """
        if task.frequency == "daily":
            return True
        if task.frequency == "weekly":
            from datetime import date
            return task.recur_day is None or date.today().weekday() == task.recur_day
        return True

    def detect_conflicts(self, tasks: list[Task]) -> list[str]:
        """
        Detect scheduling conflicts among a list of tasks.

        A conflict occurs when two or more tasks share the exact same start_time
        (HH:MM), meaning the owner would need to be in two places at once.
        Tasks with the default start_time of "00:00" are excluded to avoid
        flagging tasks that haven't been explicitly scheduled yet.

        Args:
            tasks: The list of Task objects to check.

        Returns:
            A list of human-readable warning strings, one per conflicting time
            slot. Returns an empty list if no conflicts are found.
        """
        from collections import defaultdict
        time_groups: dict[str, list[Task]] = defaultdict(list)
        for task in tasks:
            if task.start_time != "00:00":  # only flag explicitly scheduled tasks
                time_groups[task.start_time].append(task)

        warnings = []
        for start_time, group in time_groups.items():
            if len(group) > 1:
                names = " and ".join(f"'{t.name}'" for t in group)
                warnings.append(
                    f"WARNING: {names} are both scheduled at {start_time}. "
                    f"Consider rescheduling one."
                )
        return warnings

    def generate_plan(self) -> "DailyPlan":
        """
        Build a daily plan by:
        1. Collecting all tasks across all pets
        2. Filtering to tasks due today (handles recurring logic)
        3. Sorting by priority, then by time slot within same priority
        4. Adding tasks until time runs out
        5. Detecting conflicts in the final schedule
        """
        from datetime import date

        all_tasks = self.get_all_tasks()

        # Step 2: recurring filter
        due_today = [t for t in all_tasks if self.is_task_due_today(t)]

        # Step 3: sort by priority first, then time slot
        priority_order = {"high": 0, "medium": 1, "low": 2}
        slot_order = {"morning": 0, "afternoon": 1, "evening": 2, "anytime": 3}
        sorted_tasks = sorted(
            due_today,
            key=lambda t: (priority_order.get(t.priority, 3), slot_order.get(t.time_slot, 3))
        )

        # Step 4: greedy fill within time budget
        scheduled = []
        total_duration = 0
        for task in sorted_tasks:
            if total_duration + task.duration_minutes <= self.owner.get_available_time():
                scheduled.append(task)
                total_duration += task.duration_minutes

        # Step 5: sort final schedule by time slot for display
        scheduled = self.sort_by_time_slot(scheduled)

        conflicts = self.detect_conflicts(scheduled)
        explanation = self.explain_plan(scheduled)

        return DailyPlan(
            date=str(date.today()),
            scheduled_tasks=scheduled,
            explanation=explanation,
            conflicts=conflicts,
        )

    def explain_plan(self, scheduled_tasks: list[Task]) -> str:
        """Generate a plain-language explanation of why tasks were chosen."""
        if not scheduled_tasks:
            return "No tasks could be scheduled within the available time."
        total = sum(t.duration_minutes for t in scheduled_tasks)
        names = ", ".join(t.name for t in scheduled_tasks)
        return (
            f"Scheduled {len(scheduled_tasks)} task(s) totaling {total} minutes "
            f"(of {self.owner.get_available_time()} available): {names}. "
            f"Tasks were prioritized by urgency (high → medium → low), "
            f"then ordered by time of day."
        )


class DailyPlan:
    def __init__(self, date: str, scheduled_tasks: list[Task], explanation: str, conflicts: list[str] = None):
        self.date = date
        self.scheduled_tasks = scheduled_tasks
        self.explanation = explanation
        self.conflicts = conflicts or []

    @property
    def total_duration(self) -> int:
        """Computed from scheduled tasks to avoid redundancy."""
        return sum(t.duration_minutes for t in self.scheduled_tasks)

    def display(self):
        """Print the full daily plan with tasks and reasoning to the terminal."""
        print(f"Daily Plan for {self.date}")
        print(f"Total time: {self.total_duration} minutes")
        print("-" * 30)
        for task in self.scheduled_tasks:
            status = "[x]" if task.is_completed else "[ ]"
            slot = f" @{task.time_slot}" if task.time_slot != "anytime" else ""
            print(f"{status} {task.name} ({task.category}){slot} — {task.duration_minutes} min [{task.priority}]")
        print(f"\nReasoning: {self.explanation}")
        if self.conflicts:
            print("\nConflicts detected:")
            for c in self.conflicts:
                print(f"  ⚠ {c}")

    def get_summary(self) -> str:
        """Return a one-line summary of the plan including date, task count, and total time."""
        return (
            f"{self.date}: {len(self.scheduled_tasks)} tasks, "
            f"{self.total_duration} min total"
        )

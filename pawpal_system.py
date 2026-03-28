from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Task:
    name: str
    category: str            # e.g. "walk", "feed", "meds", "grooming"
    duration_minutes: int
    priority: str            # "high", "medium", or "low"
    frequency: str = "daily" # e.g. "daily", "weekly"
    is_completed: bool = False

    def mark_complete(self):
        """Mark this task as completed."""
        self.is_completed = True

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

    def generate_plan(self) -> "DailyPlan":
        """
        Build a daily plan by:
        1. Collecting all tasks across all pets
        2. Sorting by priority
        3. Adding tasks until time runs out
        """
        all_tasks = self.get_all_tasks()
        priority_order = {"high": 0, "medium": 1, "low": 2}
        sorted_tasks = sorted(all_tasks, key=lambda t: priority_order.get(t.priority, 3))

        scheduled = []
        total_duration = 0
        for task in sorted_tasks:
            if total_duration + task.duration_minutes <= self.owner.get_available_time():
                scheduled.append(task)
                total_duration += task.duration_minutes

        explanation = self.explain_plan(scheduled)
        from datetime import date
        return DailyPlan(
            date=str(date.today()),
            scheduled_tasks=scheduled,
            explanation=explanation
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
            f"Tasks were prioritized by urgency (high → medium → low)."
        )


class DailyPlan:
    def __init__(self, date: str, scheduled_tasks: list[Task], explanation: str):
        self.date = date
        self.scheduled_tasks = scheduled_tasks
        self.explanation = explanation

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
            print(f"{status} {task.name} ({task.category}) — {task.duration_minutes} min [{task.priority}]")
        print(f"\nReasoning: {self.explanation}")

    def get_summary(self) -> str:
        """Return a one-line summary of the plan including date, task count, and total time."""
        return (
            f"{self.date}: {len(self.scheduled_tasks)} tasks, "
            f"{self.total_duration} min total"
        )

from dataclasses import dataclass
from typing import Optional


@dataclass
class Pet:
    name: str
    species: str
    age: int
    special_needs: Optional[str] = None

    def update_info(self, **kwargs):
        pass


@dataclass
class Task:
    name: str
    category: str        # e.g. "walk", "feed", "meds", "grooming"
    duration_minutes: int
    priority: str        # "high", "medium", or "low"
    is_completed: bool = False

    def mark_complete(self):
        pass

    def edit(self, **kwargs):
        pass


class Owner:
    def __init__(self, name: str, available_minutes_per_day: int, preferences: Optional[str] = None):
        self.name = name
        self.available_minutes_per_day = available_minutes_per_day
        self.preferences = preferences

    def update_info(self, **kwargs):
        pass

    def get_available_time(self) -> int:
        pass


class Scheduler:
    def __init__(self, owner: Owner, pet: Pet, tasks: list[Task]):
        self.owner = owner
        self.pet = pet
        self.tasks = tasks

    def generate_plan(self):
        pass

    def fits_in_day(self, tasks: list[Task]) -> bool:
        pass

    def explain_plan(self, scheduled_tasks: list[Task]) -> str:
        pass


class DailyPlan:
    def __init__(self, date: str, scheduled_tasks: list[Task], total_duration: int, explanation: str):
        self.date = date
        self.scheduled_tasks = scheduled_tasks
        self.total_duration = total_duration
        self.explanation = explanation

    def display(self):
        pass

    def get_summary(self) -> str:
        pass

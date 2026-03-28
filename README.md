# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Features

- **Multi-pet support** — manage tasks for multiple pets under one owner profile
- **Priority scheduling** — high-priority tasks are always scheduled first within the daily time budget
- **Sorting by time** — tasks are displayed in chronological order using their `HH:MM` start time
- **Filtering** — view tasks by pet name or completion status (pending / completed)
- **Daily recurrence** — completing a daily task auto-creates the next occurrence for tomorrow
- **Weekly recurrence** — weekly tasks repeat on a chosen day; completing one schedules the next in 7 days
- **Conflict warnings** — the scheduler flags any two tasks sharing the same start time so the owner isn't double-booked
- **Plain-language reasoning** — every generated plan includes an explanation of why tasks were chosen

## Demo

<!-- Add a screenshot of your running Streamlit app here -->
<!-- <a href="/course_images/ai110/your_screenshot_name.png" target="_blank"><img src='/course_images/ai110/your_screenshot_name.png' width='600'/></a> -->
<img width="264" height="714" alt="image" src="https://github.com/user-attachments/assets/3f6a481a-06ef-444e-a496-a05cc188122b" />


## Smarter Scheduling

Phase 4 added an algorithmic layer to `pawpal_system.py` that makes the scheduler more intelligent:

- **Sort by time** — `Scheduler.sort_by_time()` orders any list of tasks chronologically using their `start_time` field (`"HH:MM"` format).
- **Filter by pet or status** — `Scheduler.filter_tasks()` narrows a task list by pet name, completion status (`"pending"` / `"completed"`), or both.
- **Recurring tasks** — Tasks have a `frequency` (`"daily"` or `"weekly"`) and a `due_date`. Calling `Scheduler.mark_task_complete()` marks the task done and automatically creates the next occurrence with an advanced due date using Python's `timedelta`.
- **Conflict detection** — `Scheduler.detect_conflicts()` scans the scheduled tasks and returns warning messages for any two tasks sharing the same `start_time`, preventing the owner from being double-booked.

## Testing PawPal+

Run the full test suite from the project root:

```bash
python -m pytest
```

The tests live in [tests/test_pawpal.py](tests/test_pawpal.py) and cover:

- **Task completion** — `mark_complete()` correctly flips `is_completed` to `True`
- **Pet task list** — adding a task increases the pet's task count
- **Sorting correctness** — `sort_by_time()` returns tasks in chronological `HH:MM` order
- **Recurrence logic** — completing a daily task auto-creates a new task due tomorrow
- **Conflict detection** — `detect_conflicts()` flags tasks sharing the same `start_time`, and stays silent when times differ

**Confidence level: ⭐⭐⭐⭐ (4/5)**
The core scheduling behaviors are well covered. The main gap is `generate_plan()` integration tests and edge cases around weekly recurrence and the time-budget cutoff.

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

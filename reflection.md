# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

The three core actions a user should be able to perform in PawPal+ are:

1. **Add/edit pet and owner info** — The user enters basic details about themselves and their pet, such as name, available time per day, and any preferences. This information provides the scheduler with the context it needs to personalize the daily plan.

2. **Add/edit care tasks** — The user creates and manages individual care tasks (e.g., walks, feeding, medication, grooming). Each task has at minimum a duration and a priority level, which the scheduler uses to decide what fits in the day and what matters most.

3. **Generate and view a daily plan** — The user triggers the scheduler to produce a prioritized daily schedule. The app displays the resulting plan clearly and explains the reasoning behind the order and selection of tasks.

The initial UML design included five classes:

- **Owner** — holds the user's name, daily available time, and preferences; responsible for providing scheduling constraints
- **Pet** — holds the pet's name, species, age, and any special needs; informs the scheduler of pet-specific context
- **Task** — holds a care task's name, category, duration, priority, and completion status; can be marked complete or edited
- **Scheduler** — the coordinator; takes an Owner, Pet, and list of Tasks and is responsible for generating and explaining a daily plan
- **DailyPlan** — the output of the Scheduler; holds the ordered task list, total duration, date, and a natural-language explanation

**b. Design changes**

After reviewing the skeleton with AI, two potential issues were identified:

1. **`generate_plan()` had no return type.** It was updated to explicitly return a `DailyPlan` object, making the relationship between `Scheduler` and `DailyPlan` clearer and easier to implement correctly.

2. **`total_duration` on `DailyPlan` is redundant.** It can always be computed by summing `duration_minutes` across `scheduled_tasks`. Storing it separately risks it going out of sync. This will be removed when logic is implemented — `get_summary()` will compute it on the fly instead.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

The scheduler considers three constraints:

1. **Time budget** — the owner's `available_minutes_per_day` acts as a hard cap. Tasks are added greedily until the budget is exhausted; any remaining tasks are dropped for that day regardless of their priority.
2. **Priority** — tasks are sorted `high → medium → low` before the greedy fill, so urgent tasks (medication, feeding) are always included before optional ones (grooming, enrichment).
3. **Recurrence / due date** — weekly tasks are only included on their designated day of the week; daily tasks are always included. This prevents a weekly bath from crowding out daily essentials.

The time constraint was treated as the hardest boundary because exceeding it would make the plan unrealistic. Priority was chosen as the primary sort key because a pet owner's first concern is not missing critical care, not optimizing the clock order of tasks.

**b. Tradeoffs**

The conflict detector only flags tasks that share an **exact `start_time` match** (e.g., two tasks both at `"08:00"`). It does not check whether task durations overlap — so a 30-minute task starting at `07:00` and a task starting at `07:15` would not trigger a warning, even though they genuinely collide in real life.

This is a reasonable tradeoff for this scenario because:
1. **Simplicity** — duration-based overlap detection requires comparing intervals (`start_time` to `start_time + duration`) rather than just string equality, which is significantly more complex to implement and read.
2. **Good enough for a pet care app** — most pet care tasks (walks, feeding, medication) are thought of as "morning" or "evening" commitments rather than precise clock-scheduled blocks. Exact-time conflicts are the most obvious and actionable to flag.
3. **Avoids false positives** — a 5-minute medication at 08:00 and a 30-minute walk starting at 08:00 are a real conflict, but a walk ending at 07:30 and medication at 07:45 are fine. Without precise clock handling, interval checks would produce noisy warnings.

A future improvement would be to store tasks as `(start_time, duration)` intervals and use proper overlap detection.

---

## 3. AI Collaboration

**a. How you used AI**

AI was used across every phase of the project:

- **Design brainstorming** — asked AI to review the initial UML and flag any structural issues before writing code. It caught the missing return type on `generate_plan()` and the redundant `total_duration` storage.
- **Implementation** — used AI to write the algorithmic methods (`sort_by_time`, `filter_tasks`, `detect_conflicts`, `next_occurrence`) after describing the desired behavior in plain English.
- **Refactoring** — asked AI how to simplify `filter_tasks`'s pet-lookup loop into a set comprehension; evaluated the tradeoff between conciseness and readability before accepting the change.
- **Test generation** — asked AI to draft tests for sorting, recurrence, and conflict detection, then read each test carefully to verify it was testing the right thing before keeping it.

The most effective prompts were specific and gave context: *"Here is the method, here is what it should do, here is the edge case I'm worried about — how would you implement or test this?"*

**b. Judgment and verification**

When AI suggested using `filter_tasks` with a nested comprehension, the initial version collapsed the pet-name lookup into a single dense line. The logic was correct, but the readability tradeoff was real — a four-line loop with a comment is easier for a new reader to follow than a two-level list comprehension. The simplified version was kept because it was short enough to remain readable, but the decision was made deliberately rather than just accepting the "more Pythonic" suggestion automatically.

Verification was done by running the existing tests after every refactor to confirm behavior didn't change, and by tracing through the logic manually for the edge cases (empty task list, task not found by name).

---

## 4. Testing and Verification

**a. What you tested**

Six behaviors were tested:

1. `mark_complete()` flips `is_completed` to `True`
2. Adding a task to a `Pet` increases its task count
3. `sort_by_time()` returns tasks in correct chronological order when given out-of-order input
4. Completing a daily task creates a new task with `due_date = today + 1 day`
5. Two tasks at the same `start_time` trigger a conflict warning
6. Tasks at different `start_time` values produce no warning

These were the most important because they cover the three new algorithmic features added in Phase 4 — sorting, recurrence, and conflict detection — which are the behaviors most likely to have subtle bugs (off-by-one dates, wrong string comparisons, false positives in conflict detection).

**b. Confidence**

Confidence: **4 out of 5**. The core behaviors are verified and the edge cases for each individual method are covered. The gap is end-to-end `generate_plan()` integration tests — for example, verifying that a weekly task is correctly excluded on the wrong day of the week, or that the plan handles an owner with zero available minutes. Those would be the next tests to add.

---

## 5. Reflection

**a. What went well**

The algorithmic layer came together cleanly. Each method (`sort_by_time`, `filter_tasks`, `detect_conflicts`, `mark_task_complete`) is small, focused, and independently testable. The decision to keep `next_occurrence()` on the `Task` class and `mark_task_complete()` on the `Scheduler` kept responsibilities clearly separated — Task knows how to copy itself forward in time, Scheduler knows where to put the copy.

**b. What you would improve**

The conflict detection is the weakest part of the system. Checking for exact `start_time` matches is fast and simple but misses real overlaps (a 30-minute walk at 07:00 and a task at 07:20 won't be flagged). A future iteration would represent each task as a time interval and use proper overlap detection. The UI would also benefit from a drag-to-reorder task list rather than a dropdown to pick which task to complete.

**c. Key takeaway**

The most important thing learned was that AI is a powerful collaborator for *implementation* but a weak one for *design decisions*. AI will generate correct code quickly, but it doesn't know which tradeoffs matter for your specific context. Every time AI suggested a "more Pythonic" version, the question wasn't "is this correct?" — it was "is this the right level of complexity for this project?" That judgment always had to come from the human. The lead architect role isn't about writing code — it's about deciding what the code should be.

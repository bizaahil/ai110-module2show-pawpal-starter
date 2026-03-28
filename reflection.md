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

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

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

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

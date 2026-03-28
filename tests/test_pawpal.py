from pawpal_system import Task, Pet


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

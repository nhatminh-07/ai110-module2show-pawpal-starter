from models import Owner, Pet, Task
from scheduler import Scheduler


def test_high_priority_tasks_are_scheduled_first():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")
    tasks = [
        Task(title="Brush coat", category="grooming", duration_minutes=20, priority="low"),
        Task(title="Morning walk", category="walk", duration_minutes=20, priority="high"),
    ]

    plan = Scheduler().build_plan(owner, pet, tasks)

    assert plan.scheduled_tasks[0].task.title == "Morning walk"


def test_tasks_that_do_not_fit_are_skipped():
    owner = Owner(name="Jordan", available_minutes=30)
    pet = Pet(name="Mochi", species="dog")
    tasks = [
        Task(title="Long trail walk", category="walk", duration_minutes=45, priority="high"),
        Task(title="Feed breakfast", category="feeding", duration_minutes=10, priority="medium"),
    ]

    plan = Scheduler().build_plan(owner, pet, tasks)

    assert len(plan.scheduled_tasks) == 1
    assert plan.scheduled_tasks[0].task.title == "Feed breakfast"


def test_required_tasks_receive_a_boost():
    owner = Owner(name="Jordan", available_minutes=20)
    pet = Pet(name="Mochi", species="dog")
    tasks = [
        Task(title="Playtime", category="enrichment", duration_minutes=20, priority="medium"),
        Task(
            title="Medication",
            category="meds",
            duration_minutes=20,
            priority="low",
            required=True,
        ),
    ]

    plan = Scheduler().build_plan(owner, pet, tasks)

    assert plan.scheduled_tasks[0].task.title == "Medication"


def test_owner_preferences_break_ties():
    owner = Owner(name="Jordan", available_minutes=20, preferences=["walk"])
    pet = Pet(name="Mochi", species="dog")
    tasks = [
        Task(title="Short walk", category="walk", duration_minutes=20, priority="medium"),
        Task(title="Puzzle toy", category="enrichment", duration_minutes=20, priority="medium"),
    ]

    plan = Scheduler().build_plan(owner, pet, tasks)

    assert plan.scheduled_tasks[0].task.title == "Short walk"


def test_empty_tasks_produce_empty_plan():
    owner = Owner(name="Jordan", available_minutes=60)
    pet = Pet(name="Mochi", species="dog")

    plan = Scheduler().build_plan(owner, pet, [])

    assert plan.scheduled_tasks == []
    assert "No tasks were scheduled" in Scheduler().explain_plan(plan)

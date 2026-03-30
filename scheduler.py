from models import DailyPlan, Owner, Pet, ScheduledTask, Task


class Scheduler:
    def __init__(self, default_start_hour: int = 9, default_start_minute: int = 0) -> None:
        self.default_start_minutes = default_start_hour * 60 + default_start_minute

    def score_task(self, task: Task, owner: Owner) -> int:
        score = {"low": 10, "medium": 20, "high": 30}.get(task.priority, 0)

        if task.required:
            score += 25

        if task.matches_preference(owner):
            score += 10

        preferred_time_bonus = {"morning": 3, "afternoon": 2, "evening": 1, "any": 0}
        score += preferred_time_bonus.get(task.preferred_time, 0)

        return score

    def rank_tasks(self, tasks: list[Task], owner: Owner) -> list[Task]:
        return sorted(
            tasks,
            key=lambda task: (self.score_task(task, owner), -task.duration_minutes, task.title),
            reverse=True,
        )

    def select_tasks(self, tasks: list[Task], owner: Owner) -> list[Task]:
        remaining = owner.available_minutes
        selected: list[Task] = []

        for task in self.rank_tasks(tasks, owner):
            if task.duration_minutes <= remaining:
                selected.append(task)
                remaining -= task.duration_minutes

        return selected

    def build_plan(self, owner: Owner, pet: Pet, tasks: list[Task]) -> DailyPlan:
        plan = DailyPlan(owner=owner, pet=pet)
        current_minutes = self.default_start_minutes

        for task in self.select_tasks(tasks, owner):
            end_minutes = current_minutes + task.duration_minutes
            scheduled_task = ScheduledTask(
                task=task,
                start_time=self._format_time(current_minutes),
                end_time=self._format_time(end_minutes),
                reason=self._build_reason(task, owner),
            )
            plan.add_task(scheduled_task)
            current_minutes = end_minutes

        return plan

    def explain_plan(self, plan: DailyPlan) -> str:
        if not plan.scheduled_tasks:
            return "No tasks were scheduled because nothing fit the available time."

        explanations = [
            f"{item.task.title} ({item.start_time}-{item.end_time}): {item.reason}"
            for item in plan.scheduled_tasks
        ]
        return "\n".join(explanations)

    def _build_reason(self, task: Task, owner: Owner) -> str:
        reasons = [f"{task.priority} priority"]
        if task.required:
            reasons.append("required for care")
        if task.matches_preference(owner):
            reasons.append(f"matches owner preference for {task.category}")
        if task.preferred_time != "any":
            reasons.append(f"preferred in the {task.preferred_time}")
        return "Chosen because it is " + ", ".join(reasons) + "."

    def _format_time(self, total_minutes: int) -> str:
        hour = total_minutes // 60
        minute = total_minutes % 60
        return f"{hour:02d}:{minute:02d}"

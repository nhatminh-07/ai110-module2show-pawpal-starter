from dataclasses import dataclass, field


@dataclass
class Owner:
    name: str
    available_minutes: int
    preferences: list[str] = field(default_factory=list)

    def prefers(self, category: str) -> bool:
        return category in self.preferences

    def can_fit(self, duration: int) -> bool:
        return duration <= self.available_minutes


@dataclass
class Pet:
    name: str
    species: str
    age: int = 0
    notes: str = ""

    def get_profile(self) -> str:
        details = f"{self.name} is a {self.species}"
        if self.age > 0:
            details += f", age {self.age}"
        if self.notes:
            details += f". Notes: {self.notes}"
        return details


@dataclass
class Task:
    title: str
    category: str
    duration_minutes: int
    priority: str
    preferred_time: str = "any"
    required: bool = False

    def is_high_priority(self) -> bool:
        return self.priority == "high"

    def matches_preference(self, owner: Owner) -> bool:
        return owner.prefers(self.category)


@dataclass
class ScheduledTask:
    task: Task
    start_time: str
    end_time: str
    reason: str

    def get_summary(self) -> str:
        return f"{self.start_time}-{self.end_time}: {self.task.title}"


@dataclass
class DailyPlan:
    owner: Owner
    pet: Pet
    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)

    @property
    def total_minutes(self) -> int:
        return sum(item.task.duration_minutes for item in self.scheduled_tasks)

    def add_task(self, item: ScheduledTask) -> None:
        self.scheduled_tasks.append(item)

    def get_remaining_time(self) -> int:
        return max(self.owner.available_minutes - self.total_minutes, 0)

    def get_plan_summary(self) -> str:
        if not self.scheduled_tasks:
            return "No tasks scheduled for today."
        return "\n".join(item.get_summary() for item in self.scheduled_tasks)

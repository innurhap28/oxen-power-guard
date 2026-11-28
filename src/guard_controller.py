"""OXEN Power Guard - 전원 절차 상태 및 타이머 제어 로직."""

from math import ceil

from power_sequence import POWER_OFF_STEPS, POWER_ON_STEPS


class GuardController:
    """UI와 독립된 순수 상태 머신."""

    def __init__(self):
        self.steps: list[dict] = []
        self.mode: str | None = None
        self.step_index: int = 0
        self.completed: bool = False
        self.timer_running: bool = False
        self.deadline: float | None = None

    def reset_to_home(self):
        self.steps = []
        self.mode = None
        self.step_index = 0
        self.completed = False
        self.stop_timer()

    def start_sequence(self, mode: str):
        self.mode = mode
        self.steps = POWER_ON_STEPS if mode == "on" else POWER_OFF_STEPS
        self.step_index = 0
        self.completed = False
        self.stop_timer()

    @property
    def total_steps(self) -> int:
        return len(self.steps)

    @property
    def current_step(self) -> dict | None:
        if 0 <= self.step_index < len(self.steps):
            return self.steps[self.step_index]
        return None

    @property
    def timer_duration(self) -> int | None:
        step = self.current_step
        return step.get("duration") if step is not None else None

    @property
    def progress_ratio(self) -> float:
        if not self.steps:
            return 0.0
        return (self.step_index + 1) / len(self.steps)

    @property
    def is_in_progress(self) -> bool:
        return self.mode is not None and not self.completed

    @property
    def can_safely_quit(self) -> bool:
        """전원 끄기 절차를 완전히 마쳤을 때만 프로그램/OS 종료 허용."""
        return self.mode == "off" and self.completed

    def start_timer(self, now_seconds: float) -> int | None:
        duration = self.timer_duration
        if duration is None or self.timer_running:
            return None
        self.timer_running = True
        self.deadline = now_seconds + duration
        return duration

    def stop_timer(self):
        self.timer_running = False
        self.deadline = None

    def check_timer(self, now_seconds: float) -> tuple[int, bool]:
        """남은 초(정수 올림)와 완료 여부(bool)를 반환."""
        if not self.timer_running or self.deadline is None:
            return 0, True

        remaining = max(0.0, self.deadline - now_seconds)
        seconds = ceil(remaining)

        if remaining <= 0:
            self.stop_timer()
            return 0, True

        return seconds, False

    def advance_step(self) -> bool:
        """다음 단계로 이동. 모든 단계가 끝나면 completed=True 설정 후 False 반환."""
        if self.timer_running:
            return True

        if self.step_index + 1 < len(self.steps):
            self.step_index += 1
            return True

        self.completed = True
        return False

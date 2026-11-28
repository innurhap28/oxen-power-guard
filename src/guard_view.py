"""OXEN Power Guard - Tkinter UI 렌더링 및 창 제어."""

import contextlib
import tkinter as tk
from tkinter import messagebox

from guard_controller import GuardController
from notifications import play_notification
from settings import POWER_OFF_WAIT_SECONDS, POWER_ON_WAIT_SECONDS
from ui_widgets import FlatButton, Theme


class GuardView:
    def __init__(self, root: tk.Tk, controller: GuardController):
        self.root = root
        self.ctrl = controller
        self.timer_after_id: str | None = None
        self.is_mini: bool = False
        self._alert_open: bool = False

        self.root.title("OXEN Power Guard")
        self.root.configure(bg=Theme.BG)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.root.after(100, self._grab_focus)

        self.wrapper = tk.Frame(
            self.root,
            bg=Theme.BG,
            highlightbackground=Theme.BORDER,
            highlightthickness=2,
        )
        self.wrapper.pack(fill="both", expand=True)

        self._build_shell()
        self.render_home()

        self.root.protocol("WM_DELETE_WINDOW", self._intercept_system_close)
        with contextlib.suppress(tk.TclError):
            self.root.createcommand("tk::mac::Quit", self._intercept_system_close)
        self.root.bind_all("<Control-Shift-Q>", self._force_quit)
        self.root.bind_all("<Control-Shift-q>", self._force_quit)

    def _grab_focus(self):
        """실행 직후 OS 포커스를 강제로 창으로 가져온다."""
        self.root.deiconify()
        self.root.lift()
        self.root.attributes("-topmost", True)
        self.root.focus_force()

    def _now_seconds(self) -> float:
        return self.root.tk.call("clock", "milliseconds") / 1000

    def _set_window_mode(self, mini: bool):
        self.is_mini = mini
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        if mini:
            x = screen_w - Theme.MINI_WIDTH - 24
            y = 24
            self.root.geometry(f"{Theme.MINI_WIDTH}x{Theme.MINI_HEIGHT}+{x}+{y}")
        else:
            x = (screen_w - Theme.MAIN_WIDTH) // 2
            y = (screen_h - Theme.MAIN_HEIGHT) // 2
            self.root.geometry(f"{Theme.MAIN_WIDTH}x{Theme.MAIN_HEIGHT}+{x}+{y}")

        self.root.lift()
        self.root.attributes("-topmost", True)

    def _build_shell(self):
        for widget in self.wrapper.winfo_children():
            widget.destroy()

        header = tk.Frame(self.wrapper, bg=Theme.BG)
        header.pack(fill="x", padx=30, pady=(24, 12))

        tk.Label(
            header,
            text="OXEN POWER GUARD",
            bg=Theme.BG,
            fg=Theme.TEXT,
            font=("Arial", 18, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="MAIN AMPLIFIER & X AIR SAFETY GUIDE",
            bg=Theme.BG,
            fg=Theme.MUTED,
            font=("Arial", 9),
        ).pack(anchor="w", pady=(3, 0))

        self.content = tk.Frame(self.wrapper, bg=Theme.BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=12)

        tk.Label(
            self.wrapper,
            text="실제 장비 상태는 직접 확인하고 조작해야 합니다.",
            bg=Theme.BG,
            fg=Theme.MUTED,
            font=("Arial", 9),
        ).pack(pady=(4, 18))

    def _clear_content(self):
        self._cancel_timer_loop()
        if not self.content.winfo_exists():
            self._build_shell()
        for widget in self.content.winfo_children():
            widget.destroy()

    def _button(self, parent, text, command, bg, fg="#ffffff", state=tk.NORMAL, **kwargs):
        return FlatButton(
            parent,
            text=text,
            command=command,
            bg=bg,
            fg=fg,
            state=state,
            **kwargs,
        )

    def render_home(self):
        self._set_window_mode(mini=False)
        self._clear_content()

        tk.Label(
            self.content,
            text="무엇을 할까요?",
            bg=Theme.BG,
            fg=Theme.TEXT,
            font=("Arial", 24, "bold"),
        ).pack(anchor="w", pady=(20, 8))

        tk.Label(
            self.content,
            text="실제 장비를 조작한 뒤 해당 단계의 완료 버튼을 눌러주세요.",
            bg=Theme.BG,
            fg=Theme.MUTED,
            font=("Arial", 11),
        ).pack(anchor="w", pady=(0, 26))

        self._button(
            self.content,
            "전원 켜기  ·  POWER ON",
            lambda: self._on_start("on"),
            Theme.GREEN,
        ).pack(fill="x", pady=7, ipady=7)

        self._button(
            self.content,
            "전원 끄기  ·  POWER OFF",
            lambda: self._on_start("off"),
            Theme.RED,
        ).pack(fill="x", pady=7, ipady=7)

        info = tk.Frame(self.content, bg=Theme.PANEL, padx=16, pady=14)
        info.pack(fill="x", pady=(26, 0))

        tk.Label(
            info,
            text="기억하세요",
            bg=Theme.PANEL,
            fg=Theme.AMBER,
            font=("Arial", 11, "bold"),
        ).pack(anchor="w")

        tk.Label(
            info,
            text=(
                f"전원 켜기: 믹서 ON → {POWER_ON_WAIT_SECONDS}초 → 두 앰프 ON → X AIR Edit 연결\n"
                f"전원 끄기: 두 앰프 OFF → {POWER_OFF_WAIT_SECONDS}초 → 믹서 OFF"
            ),
            bg=Theme.PANEL,
            fg=Theme.TEXT,
            justify="left",
            font=("Arial", 10),
            pady=7,
        ).pack(anchor="w")

    def render_mini_mode(self):
        """합주 중 X AIR Edit 화면을 가리지 않도록 우측 상단 미니 바로 축소."""
        self._cancel_timer_loop()
        self._set_window_mode(mini=True)

        for widget in self.wrapper.winfo_children():
            widget.destroy()

        bar = tk.Frame(self.wrapper, bg=Theme.PANEL)
        bar.pack(fill="both", expand=True)

        tk.Label(
            bar,
            text="● 합주 중",
            bg=Theme.PANEL,
            fg=Theme.GREEN,
            font=("Arial", 11, "bold"),
            padx=14,
        ).pack(side="left", fill="y")

        self._button(
            bar,
            "전원 끄기 →",
            lambda: self._on_start("off"),
            Theme.RED,
            font=("Arial", 10, "bold"),
            padx=14,
            pady=8,
        ).pack(side="right", padx=8, pady=7)

    def _on_start(self, mode: str):
        self.ctrl.start_sequence(mode)
        self.render_step()
        self._set_window_mode(mini=False)

    def render_step(self):
        self._clear_content()
        step = self.ctrl.current_step
        if step is None:
            return

        accent = Theme.GREEN if self.ctrl.mode == "on" else Theme.RED
        title = "전원 켜기" if self.ctrl.mode == "on" else "전원 끄기"

        top = tk.Frame(self.content, bg=Theme.BG)
        top.pack(fill="x")

        tk.Label(
            top,
            text=title,
            bg=Theme.BG,
            fg=accent,
            font=("Arial", 18, "bold"),
        ).pack(side="left")

        tk.Label(
            top,
            text=f"STEP {self.ctrl.step_index + 1} / {self.ctrl.total_steps}",
            bg=Theme.BG,
            fg=Theme.MUTED,
            font=("Arial", 10, "bold"),
        ).pack(side="right")

        progress_bg = tk.Frame(self.content, bg=Theme.PANEL_LIGHT, height=7)
        progress_bg.pack(fill="x", pady=(16, 24))
        progress = tk.Frame(progress_bg, bg=accent)
        progress.place(relwidth=self.ctrl.progress_ratio, relheight=1)

        panel = tk.Frame(self.content, bg=Theme.PANEL, padx=24, pady=24)
        panel.pack(fill="both", expand=True)

        tk.Label(
            panel,
            text=step["title"],
            bg=Theme.PANEL,
            fg=Theme.TEXT,
            font=("Arial", 20, "bold"),
            wraplength=560,
            justify="left",
        ).pack(anchor="w", pady=(4, 12))

        tk.Label(
            panel,
            text=step["description"],
            bg=Theme.PANEL,
            fg=Theme.MUTED,
            font=("Arial", 12),
            wraplength=560,
            justify="left",
        ).pack(anchor="w", pady=(0, 20))

        duration = self.ctrl.timer_duration
        if duration is not None:
            self.timer_label = tk.Label(
                panel,
                text=self._format_countdown(duration),
                bg=Theme.PANEL,
                fg=Theme.AMBER,
                font=("Arial", 48, "bold"),
            )
            self.timer_label.pack(pady=(2, 12))

            self.timer_status = tk.Label(
                panel,
                text="대기 시간이 끝날 때까지 기다려주세요.",
                bg=Theme.PANEL,
                fg=Theme.MUTED,
                font=("Arial", 10),
            )
            self.timer_status.pack(pady=(0, 16))

            self.action_button = self._button(
                panel,
                f"{duration}초 대기 시작",
                self._on_start_timer,
                Theme.BLUE,
            )
            self.action_button.pack(fill="x", pady=(8, 0))
        else:
            if step.get("warning"):
                tk.Label(
                    panel,
                    text=step["warning"],
                    bg=Theme.PANEL_LIGHT,
                    fg=Theme.AMBER,
                    font=("Arial", 10, "bold"),
                    wraplength=550,
                    justify="left",
                    padx=12,
                    pady=10,
                ).pack(fill="x", pady=(0, 18))

            self.action_button = self._button(
                panel,
                step.get("button", "완료했어요  →"),
                self._on_next_step,
                accent,
            )
            self.action_button.pack(fill="x", pady=(8, 0))

        bottom = tk.Frame(self.content, bg=Theme.BG)
        bottom.pack(fill="x", pady=(16, 0))

        self._button(
            bottom,
            "처음으로",
            self._on_confirm_home,
            Theme.PANEL_LIGHT,
            fg=Theme.TEXT,
        ).pack(side="left")

    @staticmethod
    def _format_countdown(seconds: int) -> str:
        minutes, seconds = divmod(seconds, 60)
        return f"{minutes:02d}:{seconds:02d}"

    def _on_start_timer(self):
        duration = self.ctrl.start_timer(self._now_seconds())
        if duration is None:
            return
        self.action_button.update_button(state=tk.DISABLED, text="대기 중...")
        self.timer_status.configure(text=f"{duration}초가 지나면 다음 단계로 진행할 수 있습니다.")
        self._tick_timer()

    def _tick_timer(self):
        seconds, finished = self.ctrl.check_timer(self._now_seconds())
        self.timer_label.configure(text=self._format_countdown(seconds))

        if finished:
            self.timer_after_id = None
            self.timer_label.configure(text="완료", fg=Theme.GREEN)
            self.timer_status.configure(text="대기 시간이 끝났습니다. 실제 장비 상태를 확인하세요.")
            play_notification()
            self.root.bell()
            self.action_button.update_button(
                state=tk.NORMAL,
                text="대기 완료 · 다음 단계로 →",
                command=self._on_next_step,
                bg=Theme.GREEN,
            )
            return

        self.timer_after_id = self.root.after(100, self._tick_timer)

    def _cancel_timer_loop(self):
        if self.timer_after_id is not None:
            with contextlib.suppress(tk.TclError):
                self.root.after_cancel(self.timer_after_id)
            self.timer_after_id = None

    def _on_next_step(self):
        has_next = self.ctrl.advance_step()
        if has_next:
            self.render_step()
        else:
            self.render_complete()

    def render_complete(self):
        self._clear_content()
        is_on = self.ctrl.mode == "on"
        title = "전원 켜기 완료" if is_on else "전원 끄기 완료"
        message = (
            "두 앰프와 X AIR Edit 사용 준비가 끝났습니다.\n아래 버튼을 누르면 우측 상단 미니 바 모드로 전환됩니다."
            if is_on
            else "두 앰프와 믹서의 전원 종료 절차가 끝났습니다.\n이제 컴퓨터를 종료하셔도 안전합니다."
        )

        tk.Label(
            self.content,
            text="✓",
            bg=Theme.BG,
            fg=Theme.GREEN,
            font=("Arial", 64, "bold"),
        ).pack(pady=(34, 8))

        tk.Label(
            self.content,
            text=title,
            bg=Theme.BG,
            fg=Theme.TEXT,
            font=("Arial", 23, "bold"),
        ).pack(pady=8)

        tk.Label(
            self.content,
            text=message,
            bg=Theme.BG,
            fg=Theme.MUTED,
            font=("Arial", 12),
            wraplength=520,
        ).pack(pady=(0, 28))

        if is_on:
            self._button(
                self.content,
                "합주 중이에요 (우측 상단으로 축소)",
                self.render_mini_mode,
                Theme.GREEN,
            ).pack(fill="x", pady=6)
        else:
            self._button(
                self.content,
                "처음 화면으로 돌아가기",
                self._on_confirm_home,
                Theme.PANEL_LIGHT,
                fg=Theme.TEXT,
            ).pack(fill="x", pady=6)

    def _on_confirm_home(self):
        if self.ctrl.is_in_progress:
            answer = messagebox.askyesno(
                "절차 진행 중",
                "현재 전원 절차가 완료되지 않았습니다.\n처음 화면으로 돌아가시겠습니까?",
                parent=self.root,
            )
            if not answer:
                return
        self.ctrl.reset_to_home()
        self.render_home()

    def _intercept_system_close(self):
        """전원 끄기 미완료 상태에서 종료 시도 시 경고만 1회 표시하고 현재 화면 유지."""
        if self.ctrl.can_safely_quit:
            self._cancel_timer_loop()
            self.root.destroy()
            return

        if self._alert_open:
            return

        self._alert_open = True
        try:
            message = (
                "아직 두 앰프/믹서 전원 종료 절차가 완료되지 않았습니다!\n"
                "합주를 마치려면 우측 상단의 '전원 끄기' 버튼을 눌러 절차를 진행해 주세요."
                if self.is_mini
                else "아직 두 앰프/믹서 전원 종료 절차가 완료되지 않았습니다!\n"
                "장비 손상 방지를 위해 '전원 끄기' 절차를 완료한 후 종료해 주세요."
            )
            messagebox.showwarning("전원 보호 경고", message, parent=self.root)
        finally:
            self._alert_open = False

        self.root.lift()
        self.root.attributes("-topmost", True)

    def _force_quit(self, _event=None):
        """관리자용 비상 종료 (Ctrl + Shift + Q)."""
        self._cancel_timer_loop()
        self.ctrl.stop_timer()
        self.root.destroy()

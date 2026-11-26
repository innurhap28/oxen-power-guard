"""Band Power Guard - 합주실 메인 앰프/믹서 전원 절차 안내 프로그램."""

import contextlib
import tkinter as tk
from tkinter import messagebox

from notifications import play_notification
from power_sequence import POWER_OFF_STEPS, POWER_ON_STEPS


class FlatButton(tk.Label):
    """macOS와 Windows에서 동일하게 배경색과 호버/비활성 상태가 렌더링되는 버튼."""

    def __init__(
        self,
        parent,
        text: str,
        command,
        bg: str,
        fg: str = "#ffffff",
        hover_bg: str | None = None,
        disabled_bg: str = "#273449",
        disabled_fg: str = "#7b8797",
        state: str = tk.NORMAL,
        font=("Arial", 12, "bold"),
        padx: int = 18,
        pady: int = 13,
        **kwargs,
    ):
        self._bg = bg
        self._fg = fg
        self._hover_bg = hover_bg or self._adjust_brightness(bg, 1.12)
        self._disabled_bg = disabled_bg
        self._disabled_fg = disabled_fg
        self._command = command
        self._state = state

        super().__init__(
            parent,
            text=text,
            font=font,
            padx=padx,
            pady=pady,
            **kwargs,
        )

        self.bind("<Button-1>", self._on_click)
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self._apply_state()

    @staticmethod
    def _adjust_brightness(hex_color: str, factor: float) -> str:
        hex_color = hex_color.lstrip("#")
        rgb = [int(hex_color[i : i + 2], 16) for i in (0, 2, 4)]
        adjusted = [min(255, int(c * factor)) for c in rgb]
        return f"#{adjusted[0]:02x}{adjusted[1]:02x}{adjusted[2]:02x}"

    def _apply_state(self):
        if self._state == tk.NORMAL:
            super().configure(bg=self._bg, fg=self._fg, cursor="hand2")
        else:
            super().configure(bg=self._disabled_bg, fg=self._disabled_fg, cursor="arrow")

    def _on_click(self, _event):
        if self._state == tk.NORMAL and callable(self._command):
            self._command()

    def _on_enter(self, _event):
        if self._state == tk.NORMAL:
            super().configure(bg=self._hover_bg)

    def _on_leave(self, _event):
        if self._state == tk.NORMAL:
            super().configure(bg=self._bg)

    def update_button(
        self,
        *,
        text: str | None = None,
        command=None,
        bg: str | None = None,
        state: str | None = None,
    ):
        if text is not None:
            super().configure(text=text)
        if command is not None:
            self._command = command
        if bg is not None:
            self._bg = bg
            self._hover_bg = self._adjust_brightness(bg, 1.12)
        if state is not None:
            self._state = state
        self._apply_state()


class BandPowerGuard:
    BG = "#111827"
    PANEL = "#1f2937"
    PANEL_LIGHT = "#273449"
    BORDER = "#374151"
    TEXT = "#f9fafb"
    MUTED = "#aeb9c8"
    GREEN = "#22c55e"
    RED = "#ef4444"
    BLUE = "#60a5fa"
    AMBER = "#fbbf24"

    MAIN_WIDTH = 680
    MAIN_HEIGHT = 640
    MINI_WIDTH = 270
    MINI_HEIGHT = 54

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("OXEN Power Guard")
        self.root.configure(bg=self.BG)

        # 항상 최상단 고정 + 상단 닫기/최소화 버튼 제거
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)

        self.steps = []
        self.mode = None
        self.step_index = 0
        self.timer_after_id = None
        self.deadline = None
        self.timer_running = False
        self.completed = False
        self.is_mini = False

        # 외곽 테두리 프레임 (타이틀바 제거 시 경계 구분용)
        self.wrapper = tk.Frame(
            self.root,
            bg=self.BG,
            highlightbackground=self.BORDER,
            highlightthickness=2,
        )
        self.wrapper.pack(fill="both", expand=True)

        self._build_shell()
        self.show_home()

        # OS 종료 신호 가로채기 및 관리자 비상 종료 단축키(Ctrl+Shift+Q)
        self.root.protocol("WM_DELETE_WINDOW", self._intercept_system_close)
        self.root.bind_all("<Control-Shift-Q>", self._force_quit)
        self.root.bind_all("<Control-Shift-q>", self._force_quit)

    def _set_window_mode(self, mini: bool):
        self.is_mini = mini
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()

        if mini:
            x = screen_w - self.MINI_WIDTH - 24
            y = 24
            self.root.geometry(f"{self.MINI_WIDTH}x{self.MINI_HEIGHT}+{x}+{y}")
        else:
            x = (screen_w - self.MAIN_WIDTH) // 2
            y = (screen_h - self.MAIN_HEIGHT) // 2
            self.root.geometry(f"{self.MAIN_WIDTH}x{self.MAIN_HEIGHT}+{x}+{y}")

        self.root.lift()
        self.root.attributes("-topmost", True)

    def _build_shell(self):
        for widget in self.wrapper.winfo_children():
            widget.destroy()

        header = tk.Frame(self.wrapper, bg=self.BG)
        header.pack(fill="x", padx=30, pady=(24, 12))

        tk.Label(
            header,
            text="BAND POWER GUARD",
            bg=self.BG,
            fg=self.TEXT,
            font=("Arial", 18, "bold"),
        ).pack(anchor="w")

        tk.Label(
            header,
            text="MAIN AMPLIFIER SAFETY GUIDE",
            bg=self.BG,
            fg=self.MUTED,
            font=("Arial", 9),
        ).pack(anchor="w", pady=(3, 0))

        self.content = tk.Frame(self.wrapper, bg=self.BG)
        self.content.pack(fill="both", expand=True, padx=30, pady=12)

        tk.Label(
            self.wrapper,
            text="실제 장비 상태는 직접 확인하고 조작해야 합니다.",
            bg=self.BG,
            fg=self.MUTED,
            font=("Arial", 9),
        ).pack(pady=(4, 18))

    def _clear_content(self):
        self._stop_timer()
        if self.is_mini:
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
            disabled_bg=self.PANEL_LIGHT,
            state=state,
            **kwargs,
        )

    def show_home(self):
        self._set_window_mode(mini=False)
        self._clear_content()
        self.mode = None
        self.completed = False

        tk.Label(
            self.content,
            text="무엇을 할까요?",
            bg=self.BG,
            fg=self.TEXT,
            font=("Arial", 24, "bold"),
        ).pack(anchor="w", pady=(22, 8))

        tk.Label(
            self.content,
            text="실제 장비를 조작한 뒤 해당 단계의 완료 버튼을 눌러주세요.",
            bg=self.BG,
            fg=self.MUTED,
            font=("Arial", 11),
        ).pack(anchor="w", pady=(0, 28))

        self._button(
            self.content,
            "전원 켜기  ·  POWER ON",
            lambda: self.start_sequence("on"),
            self.GREEN,
        ).pack(fill="x", pady=7, ipady=7)

        self._button(
            self.content,
            "전원 끄기  ·  POWER OFF",
            lambda: self.start_sequence("off"),
            self.RED,
        ).pack(fill="x", pady=7, ipady=7)

        info = tk.Frame(self.content, bg=self.PANEL, padx=16, pady=14)
        info.pack(fill="x", pady=(28, 0))

        tk.Label(
            info,
            text="기억하세요",
            bg=self.PANEL,
            fg=self.AMBER,
            font=("Arial", 11, "bold"),
        ).pack(anchor="w")

        tk.Label(
            info,
            text=(
                "전원 켜기: 믹서 ON → 30초 → 앰프 ON\n"
                "전원 끄기: 전체 Mute → 앰프 OFF → 30초 → 표시등 확인 → 믹서 OFF"
            ),
            bg=self.PANEL,
            fg=self.TEXT,
            justify="left",
            font=("Arial", 10),
            pady=7,
        ).pack(anchor="w")

    def show_mini_mode(self):
        """합주 중 화면을 가리지 않도록 우측 상단 미니 바로 축소."""
        self._stop_timer()
        self._set_window_mode(mini=True)

        for widget in self.wrapper.winfo_children():
            widget.destroy()

        bar = tk.Frame(self.wrapper, bg=self.PANEL)
        bar.pack(fill="both", expand=True)

        tk.Label(
            bar,
            text="● 합주 중",
            bg=self.PANEL,
            fg=self.GREEN,
            font=("Arial", 11, "bold"),
            padx=14,
        ).pack(side="left", fill="y")

        self._button(
            bar,
            "전원 끄기 →",
            lambda: self.start_sequence("off"),
            self.RED,
            font=("Arial", 10, "bold"),
            padx=14,
            pady=8,
        ).pack(side="right", padx=8, pady=7)

    def start_sequence(self, mode: str):
        self._set_window_mode(mini=False)
        self.mode = mode
        self.steps = POWER_ON_STEPS if mode == "on" else POWER_OFF_STEPS
        self.step_index = 0
        self.completed = False
        self.show_step()

    def show_step(self):
        self._clear_content()
        step = self.steps[self.step_index]
        total = len(self.steps)
        accent = self.GREEN if self.mode == "on" else self.RED
        title = "전원 켜기" if self.mode == "on" else "전원 끄기"

        top = tk.Frame(self.content, bg=self.BG)
        top.pack(fill="x")

        tk.Label(
            top,
            text=title,
            bg=self.BG,
            fg=accent,
            font=("Arial", 18, "bold"),
        ).pack(side="left")

        tk.Label(
            top,
            text=f"STEP {self.step_index + 1} / {total}",
            bg=self.BG,
            fg=self.MUTED,
            font=("Arial", 10, "bold"),
        ).pack(side="right")

        progress_bg = tk.Frame(self.content, bg=self.PANEL_LIGHT, height=7)
        progress_bg.pack(fill="x", pady=(16, 28))
        progress = tk.Frame(progress_bg, bg=accent)
        progress.place(relwidth=(self.step_index + 1) / total, relheight=1)

        panel = tk.Frame(self.content, bg=self.PANEL, padx=24, pady=24)
        panel.pack(fill="both", expand=True)

        tk.Label(
            panel,
            text=step["title"],
            bg=self.PANEL,
            fg=self.TEXT,
            font=("Arial", 21, "bold"),
            wraplength=560,
            justify="left",
        ).pack(anchor="w", pady=(4, 12))

        tk.Label(
            panel,
            text=step["description"],
            bg=self.PANEL,
            fg=self.MUTED,
            font=("Arial", 12),
            wraplength=560,
            justify="left",
        ).pack(anchor="w", pady=(0, 20))

        if step.get("timer"):
            duration = step.get("duration", 30)
            self.timer_label = tk.Label(
                panel,
                text=f"00:{duration:02d}",
                bg=self.PANEL,
                fg=self.AMBER,
                font=("Arial", 48, "bold"),
            )
            self.timer_label.pack(pady=(2, 12))

            self.timer_status = tk.Label(
                panel,
                text="대기 시간이 끝날 때까지 기다려주세요.",
                bg=self.PANEL,
                fg=self.MUTED,
                font=("Arial", 10),
            )
            self.timer_status.pack(pady=(0, 16))

            self.action_button = self._button(
                panel,
                f"{duration}초 대기 시작",
                lambda d=duration: self.start_timer(d),
                self.BLUE,
            )
            self.action_button.pack(fill="x", pady=(8, 0))
        else:
            if step.get("warning"):
                tk.Label(
                    panel,
                    text=step["warning"],
                    bg=self.PANEL_LIGHT,
                    fg=self.AMBER,
                    font=("Arial", 10, "bold"),
                    wraplength=550,
                    justify="left",
                    padx=12,
                    pady=10,
                ).pack(fill="x", pady=(0, 18))

            self.action_button = self._button(
                panel,
                step.get("button", "완료했어요  →"),
                self.next_step,
                accent,
            )
            self.action_button.pack(fill="x", pady=(8, 0))

        bottom = tk.Frame(self.content, bg=self.BG)
        bottom.pack(fill="x", pady=(16, 0))

        self._button(
            bottom,
            "처음으로",
            self.confirm_go_home,
            self.PANEL_LIGHT,
            fg=self.TEXT,
        ).pack(side="left")

        self._button(
            bottom,
            "합주 중 (최소화)",
            self.show_mini_mode,
            self.PANEL_LIGHT,
            fg=self.MUTED,
        ).pack(side="right")

    def start_timer(self, duration: int = 30):
        if self.timer_running:
            return

        self.timer_running = True
        self.deadline = self.root.tk.call("clock", "milliseconds") / 1000 + duration
        self.action_button.update_button(state=tk.DISABLED, text="대기 중...")
        self.timer_status.configure(text=f"{duration}초가 지나면 다음 단계로 진행할 수 있습니다.")
        self._tick_timer()

    def _tick_timer(self):
        if not self.timer_running or self.deadline is None:
            return

        now = self.root.tk.call("clock", "milliseconds") / 1000
        remaining = max(0, self.deadline - now)
        seconds = int(remaining + 0.999)

        self.timer_label.configure(text=f"00:{seconds:02d}")

        if remaining <= 0:
            self.timer_running = False
            self.deadline = None
            self.timer_label.configure(text="완료", fg=self.GREEN)
            self.timer_status.configure(text="대기 시간이 끝났습니다. 실제 장비 상태를 확인하세요.")
            play_notification()
            self.action_button.update_button(
                state=tk.NORMAL,
                text="대기 완료 · 다음 단계로 →",
                command=self.next_step,
                bg=self.GREEN,
            )
            return

        self.timer_after_id = self.root.after(100, self._tick_timer)

    def _stop_timer(self):
        if self.timer_after_id is not None:
            with contextlib.suppress(tk.TclError):
                self.root.after_cancel(self.timer_after_id)
            self.timer_after_id = None
        self.timer_running = False
        self.deadline = None

    def next_step(self):
        if self.timer_running:
            return

        if self.step_index + 1 < len(self.steps):
            self.step_index += 1
            self.show_step()
        else:
            self.show_complete()

    def show_complete(self):
        self._clear_content()
        self.completed = True
        is_on = self.mode == "on"
        title = "전원 켜기 완료" if is_on else "전원 끄기 완료"
        message = (
            "메인 앰프와 믹서의 사용 준비가 끝났습니다.\n아래 버튼을 누르면 우측 상단 미니 바 모드로 전환됩니다."
            if is_on
            else "메인 앰프와 믹서의 전원 종료 절차가 끝났습니다.\n이제 컴퓨터를 종료하셔도 안전합니다."
        )

        tk.Label(
            self.content,
            text="✓",
            bg=self.BG,
            fg=self.GREEN,
            font=("Arial", 64, "bold"),
        ).pack(pady=(36, 8))

        tk.Label(
            self.content,
            text=title,
            bg=self.BG,
            fg=self.TEXT,
            font=("Arial", 23, "bold"),
        ).pack(pady=8)

        tk.Label(
            self.content,
            text=message,
            bg=self.BG,
            fg=self.MUTED,
            font=("Arial", 12),
            wraplength=520,
        ).pack(pady=(0, 28))

        if is_on:
            self._button(
                self.content,
                "합주 중이에요 (우측 상단으로 축소)",
                self.show_mini_mode,
                self.GREEN,
            ).pack(fill="x", pady=6)
        else:
            self._button(
                self.content,
                "처음 화면으로 돌아가기",
                self.show_home,
                self.PANEL_LIGHT,
                fg=self.TEXT,
            ).pack(fill="x", pady=6)

    def confirm_go_home(self):
        if self.mode is not None and not self.completed:
            answer = messagebox.askyesno(
                "절차 진행 중",
                "현재 전원 절차가 완료되지 않았습니다.\n처음 화면으로 돌아가시겠습니까?",
                parent=self.root,
            )
            if not answer:
                return
        self.show_home()

    def _intercept_system_close(self):
        """사용자가 Alt+F4나 OS 종료로 창을 닫으려 할 때 차단하고 전원 끄기 화면 강제 노출."""
        if self.mode == "off" and self.completed:
            self._stop_timer()
            self.root.destroy()
            return

        self._set_window_mode(mini=False)
        messagebox.showwarning(
            "전원 보호 경고",
            "아직 메인 앰프/믹서 전원 종료 절차가 완료되지 않았습니다!\n"
            "장비 손상 방지를 위해 전원 끄기 절차를 먼저 진행해 주세요.",
            parent=self.root,
        )
        if self.mode != "off":
            self.start_sequence("off")

    def _force_quit(self, _event=None):
        """관리자용 비상 종료 (Ctrl + Shift + Q)."""
        self._stop_timer()
        self.root.destroy()

    def run(self):
        self.root.mainloop()


def main():
    root = tk.Tk()
    app = BandPowerGuard(root)
    app.run()


if __name__ == "__main__":
    main()
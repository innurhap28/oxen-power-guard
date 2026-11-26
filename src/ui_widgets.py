"""OXEN Power Guard - 공통 테마 상수 및 크로스플랫폼 커스텀 위젯."""

import tkinter as tk


class Theme:
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
    MAIN_HEIGHT = 650
    MINI_WIDTH = 270
    MINI_HEIGHT = 54


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
        disabled_bg: str = Theme.PANEL_LIGHT,
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

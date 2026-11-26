"""OXEN Power Guard - 실행 진입점."""

import contextlib
import signal
import sys
import tkinter as tk
from tkinter import messagebox

from guard_controller import GuardController
from guard_view import GuardView


def main() -> int:
    for sig in (signal.SIGINT, signal.SIGTERM, getattr(signal, "SIGBREAK", None)):
        if sig is not None:
            signal.signal(sig, lambda s, _: sys.exit(128 + s))

    try:
        root = tk.Tk()
        GuardView(root, GuardController())
        root.after(200, lambda: None)
        root.mainloop()
        return 0

    except KeyboardInterrupt:
        return 128 + signal.SIGINT

    except tk.TclError as e:
        print(f"[GUI 오류] Tkinter 초기화 또는 실행 실패: {e}", file=sys.stderr)
        return 1

    except OSError as e:
        print(f"[시스템 오류] OS 리소스 또는 권한 문제: {e}", file=sys.stderr)
        with contextlib.suppress(Exception):
            messagebox.showerror("OXEN Power Guard - 시스템 오류", str(e))
        return 1

    except Exception as e:
        print(f"[오류] 예기치 못한 예외 발생: {e}", file=sys.stderr)
        with contextlib.suppress(Exception):
            messagebox.showerror("OXEN Power Guard - 오류", str(e))
        return 1


if __name__ == "__main__":
    sys.exit(main())

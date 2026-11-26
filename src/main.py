"""OXEN Power Guard - 실행 진입점."""

import tkinter as tk

from guard_controller import GuardController
from guard_view import GuardView


def main():
    root = tk.Tk()
    controller = GuardController()
    GuardView(root, controller)
    root.mainloop()


if __name__ == "__main__":
    main()
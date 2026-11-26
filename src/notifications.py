"""알림음 재생. 운영체제 기본 기능만 사용한다."""

import sys


def play_notification():
    """Windows/macOS에서 사용 가능한 간단한 완료 알림음."""
    try:
        if sys.platform == "win32":
            import winsound
            winsound.MessageBeep(winsound.MB_ICONASTERISK)
        else:
            # Tkinter의 bell은 별도 오디오 패키지 없이 시스템 알림음을 낸다.
            # 호출 측에서 root.bell()을 사용할 수 없는 구조이므로 기본 터미널 벨을 사용한다.
            print("\a", end="", flush=True)
    except Exception:
        # 알림음이 재생되지 않아도 절차 진행에는 영향을 주지 않는다.
        pass

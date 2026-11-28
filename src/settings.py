"""실행 환경에서 읽는 전원 대기 시간 설정."""

import math
import os
import sys


def _wait_seconds(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default

    try:
        seconds = int(value)
        if seconds > 0 and math.isfinite(seconds):
            return seconds
    except (ValueError, OverflowError):
        pass

    print(f"[설정 경고] {name}에 양의 정수(초)가 필요합니다. 기본값 {default}초를 사용합니다.", file=sys.stderr)
    return default


POWER_ON_WAIT_SECONDS = _wait_seconds("OXEN_POWER_ON_WAIT_SECONDS", 30)
POWER_OFF_WAIT_SECONDS = _wait_seconds("OXEN_POWER_OFF_WAIT_SECONDS", 30)

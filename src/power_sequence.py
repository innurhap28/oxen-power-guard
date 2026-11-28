"""믹서와 앰프 전원 조작 순서."""

from settings import POWER_OFF_WAIT_SECONDS, POWER_ON_WAIT_SECONDS

POWER_ON_STEPS = [
    {
        "title": "믹서 전원을 켜주세요",
        "description": "믹서 오른쪽 벽 스위치를 ON으로 전환하세요.",
        "button": "믹서를 켰어요  →",
    },
    {
        "title": f"{POWER_ON_WAIT_SECONDS}초 기다려주세요",
        "description": f"믹서 전원을 켠 뒤 앰프를 켜기 전까지 {POWER_ON_WAIT_SECONDS}초 대기합니다.",
        "duration": POWER_ON_WAIT_SECONDS,
    },
    {
        "title": "두 앰프를 켜주세요",
        "description": f"{POWER_ON_WAIT_SECONDS}초 대기가 끝났습니다. Rockers와 SIGMA 전원을 모두 켜세요.",
        "button": "두 앰프를 켰어요  →",
    },
    {
        "title": "컴퓨터에서 X AIR Edit를 실행하세요",
        "description": "X AIR Edit 프로그램을 실행하고 믹서 연결 화면으로 이동하세요.",
        "button": "X AIR Edit를 실행했어요  →",
    },
    {
        "title": "믹서에 연결하세요",
        "description": "Connect를 클릭한 다음 MIXER to PC를 선택하세요. Not Connected가 표시되면 믹서 전원을 확인하고 Setup → Connection → Rescan을 선택하세요.",
        "button": "믹서에 연결했어요  →",
    },
]

POWER_OFF_STEPS = [
    {
        "title": "두 앰프를 꺼주세요",
        "description": "Rockers와 SIGMA 전원을 모두 끄세요.",
        "button": "두 앰프를 껐어요  →",
    },
    {
        "title": f"{POWER_OFF_WAIT_SECONDS}초 기다려주세요",
        "description": f"마지막 앰프를 끈 뒤 믹서 전원을 끄기 전까지 {POWER_OFF_WAIT_SECONDS}초 대기합니다.",
        "duration": POWER_OFF_WAIT_SECONDS,
    },
    {
        "title": "믹서 전원을 끄세요",
        "description": "믹서 오른쪽 벽 스위치를 OFF로 전환하세요.",
        "warning": "합주가 끝나면 다음 합주팀이 있더라도 장비를 꼭 끄고 나가세요.",
        "button": "믹서를 껐어요  →",
    },
]

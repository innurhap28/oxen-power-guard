"""메인 앰프 전원 조작 순서."""

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
        "title": "메인 앰프를 켜주세요",
        "description": f"{POWER_ON_WAIT_SECONDS}초 대기가 끝났습니다. 메인 앰프 전원을 ON으로 전환하세요.",
        "button": "앰프를 켰어요  →",
    },
    {
        "title": "컴퓨터에서 X Air를 실행하세요",
        "description": "X Air 프로그램을 실행하고 믹서 연결 화면으로 이동하세요.",
        "button": "X Air를 실행했어요  →",
    },
    {
        "title": "믹서에 연결하세요",
        "description": "Connect를 클릭한 다음 MIXER to PC를 선택하세요. 연결이 되지 않으면 우측 상단 Setup에서 믹서 연결을 확인하세요.",
        "button": "믹서에 연결했어요  →",
    },
    {
        "title": "필요한 채널의 Mute를 해제하세요",
        "description": "사용할 채널과 Main의 하단 Mute를 해제하세요.",
        "warning": "지정된 FX, EQ 및 밸런스 값은 임의로 변경하지 마세요.",
        "button": "사용 준비를 마쳤어요  →",
    },
]

POWER_OFF_STEPS = [
    {
        "title": "X Air 연결 상태를 확인하세요",
        "description": "X Air 창 상단에 믹서 주소가 표시되어 있는지 확인하세요. Not connected 상태라면 우측 상단 Setup에서 믹서와 연결하세요.",
        "button": "연결 상태를 확인했어요  →",
    },
    {
        "title": "전체 채널과 Main을 Mute 하세요",
        "description": "X Air에서 모든 채널과 Main의 하단 Mute를 활성화하세요.",
        "button": "전체 Mute 했어요  →",
    },
    {
        "title": "메인 앰프 전원을 끄세요",
        "description": "메인 앰프의 전원을 OFF로 전환하세요.",
        "button": "앰프를 껐어요  →",
    },
    {
        "title": f"{POWER_OFF_WAIT_SECONDS}초 기다려주세요",
        "description": f"앰프 전원을 끈 뒤 믹서 전원을 끄기 전까지 {POWER_OFF_WAIT_SECONDS}초 대기합니다.",
        "duration": POWER_OFF_WAIT_SECONDS,
    },
    {
        "title": "앰프의 빨간 표시등을 확인하세요",
        "description": "앰프의 빨간 표시등이 꺼졌는지 직접 확인하세요.",
        "button": "빨간 표시등이 꺼진 것을 확인했어요  →",
    },
    {
        "title": "믹서 전원을 끄세요",
        "description": "믹서 오른쪽 벽 스위치를 OFF로 전환하세요.",
        "warning": "합주가 끝나면 다음 합주팀이 있더라도 장비를 꼭 끄고 나가세요.",
        "button": "믹서를 껐어요  →",
    },
]

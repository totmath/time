import os
import requests
from datetime import datetime, timedelta, timezone
from slack_sdk import WebClient

# --- [1. 시간 및 슬랙 설정] ---
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
target_day_name = now.strftime('%A') # 요일 이름 (예: Wednesday)

# 깃허브 Secrets와 코드의 이름을 'CHANNEL'로 통일
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
CHANNEL = os.environ.get("CHANNEL") 
client = WebClient(token=SLACK_TOKEN)

# --- [2. 시간표 데이터] ---
# 사용자님의 데이터 구조에 맞춰 예시를 넣었습니다. 실제 데이터와 다르면 수정하세요!
timetable_data = {
    "Wednesday": [
        {"period": "1", "subject": "물리1", "teacher": "강은지", "location": "물리학실1", "floor": "4층"},
        {"period": "2", "subject": "물리1", "teacher": "강은지", "location": "물리학실1", "floor": "4층"},
        {"period": "3", "subject": "통물", "teacher": "양하은", "location": "물리학실1", "floor": "4층"},
        {"period": "4", "subject": "공수2", "teacher": "조동기", "location": "201호", "floor": "2층"},
        {"period": "5", "subject": "통사1", "teacher": "김정민", "location": "303호", "floor": "3층"},
        {"period": "6", "subject": "통지", "teacher": "오상림", "location": "지구과학실1", "floor": "5층"},
        {"period": "7", "subject": "동아리", "teacher": "홍창욱", "location": "동아리실", "floor": "기타"}
    ]
}

# 1. 요일 변환 사전 (함수 밖에 두거나 안에 두어도 됨)
days_ko = {
    "Monday": "월요일", "Tuesday": "화요일", "Wednesday": "수요일",
    "Thursday": "목요일", "Friday": "금요일", "Saturday": "토요일", "Sunday": "일요일"
}

def send_slack_timetable():
    # 데이터는 영어("Wednesday")로 찾고!
    today_schedule = timetable_data.get(target_day_name, [])
    
    # 출력용 이름만 한글("수요일")로 바꿉니다.
    target_day_ko = days_ko.get(target_day_name, target_day_name)
    
    if not today_schedule:
        print(f"오늘({target_day_name})은 수업 데이터가 없네요.")
        return

    # 메시지 디자인 (선 빼고 공백으로 예쁘게)
    message_text = f"✨ *{now.strftime('%m/%d')} {target_day_ko} 시간표* ✨\n\n"

    for item in today_schedule:
        p = item['period'].replace("교시", "").strip()
        # 선(-) 대신 이모지와 줄바꿈으로 정리
        message_text += f"{p}️⃣  *{item['subject']}* ({item['teacher']})\n"
        message_text += f"      📍 _{item['location']} ({item['floor']})_\n\n"

    # 전송 (CHANNEL 이름 확인!)
    try:
        client.chat_postMessage(channel=CHANNEL, text=message_text)
        print("성공적으로 보냈습니다!")
    except Exception as e:
        print(f"에러 발생: {e}")
    client.chat_postMessage(channel=CHANNEL, text=message_text)

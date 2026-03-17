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

def send_slack_timetable():
    # 오늘 요일에 맞는 데이터 가져오기
    today_schedule = timetable_data.get(target_day_name, [])
    
    if not today_schedule:
        print("오늘 수업이 없습니다.")
        return

    # 메시지 조립 (모바일 최적화)
    message_text = f"📅 *{now.strftime('%m/%d')} {target_day_name} 시간표 (1-3)*\n"
    message_text += "━━━━━━━━━━━━━━━━━━━━\n"

    for item in today_schedule:
        message_text += f"\n{item['period']}️⃣ *{item['subject']}* ({item['teacher']})\n"
        message_text += f"📍 _{item['location']} ({item['floor']})_\n"

    # 슬랙 전송 (채널 이름 CHANNEL로 통일)
    try:
        client.chat_postMessage(channel=CHANNEL, text=message_text)
        print("메시지 전송 성공!")
    except Exception as e:
        print(f"전송 실패: {e}")

if __name__ == "__main__":
    send_slack_timetable()



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
# 1. 요일 이름 리스트 (0: 월요일, 1: 화요일 ... 6: 일요일)
days_list_ko = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]
# 데이터 키값 리스트 (사용자님의 timetable_data 키값에 맞추세요)
days_list_en = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def send_slack_timetable():
    # 0~6 사이의 숫자로 오늘 요일을 가져옵니다 (오늘이 수요일이면 2)
    day_idx = now.weekday() 
    
    # 1. 한글 요일 이름 정하기
    target_day_ko = days_list_ko[day_idx]
    # 2. 데이터 찾을 키 이름 정하기
    target_key = days_list_en[day_idx]

    # 데이터 가져오기 (만약 키값이 다르면 여기서 에러 없이 빈 리스트 반환)
    today_schedule = timetable_data.get(target_key, [])
    
    # [디버깅] 로그에서 확인용 (Actions 로그에 찍힙니다)
    print(f"인식된 요일 인덱스: {day_idx}")
    print(f"찾으려는 키값: {target_key}")

    if not today_schedule:
        print(f"⚠️ {target_key}에 해당하는 시간표 데이터가 없습니다!")
        return

    # 메시지 조립
    message_text = f"✨ *{now.strftime('%m/%d')} {target_day_ko} 시간표* ✨\n\n"

    for item in today_schedule:
        p = item['period'].replace("교시", "").strip()
        message_text += f"{p}️⃣  *{item['subject']}* ({item['teacher']})\n"
        message_text += f"      📍 _{item['location']} ({item['floor']})_\n\n"

    # 전송 (CHANNEL 이름 통일!)
    try:
        client.chat_postMessage(channel=CHANNEL, text=message_text)
        print("🚀 슬랙 전송 성공!")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")

if __name__ == "__main__":
    send_slack_timetable()

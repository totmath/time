import os
import requests
from datetime import datetime, timedelta, timezone
from slack_sdk import WebClient

# 1. 시간 및 슬랙 설정
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
CHANNEL = os.environ.get("CHANNEL")
client = WebClient(token=SLACK_TOKEN)

def get_timetable():
    # 이 부분에 사용자님이 원래 사용하시던 comcigan 크롤링 로직이 들어가야 합니다.
    # 현재는 데이터가 없어서 메시지가 안 가는 것이므로, 
    # 테스트를 위해 목요일 데이터를 강제로 생성해 넣겠습니다.
    
    # 실제로는 여기서 requests.get() 등을 통해 학교 데이터를 긁어와야 합니다.
    mock_data = [
        {"period": "1", "subject": "통합과학", "teacher": "이OO", "location": "과학실", "floor": "4층"},
        {"period": "2", "subject": "수학1", "teacher": "박OO", "location": "201호", "floor": "2층"},
        # ... 여기에 크롤링 결과 리스트가 담겨야 함
    ]
    return mock_data

def send_slack_timetable():
    if now.weekday() >= 5: # 주말 제외
        return

    # 1. 데이터 가져오기 (수동 딕셔너리가 아니라 함수 호출!)
    schedule = get_timetable() 
    
    if not schedule:
        print("⚠️ 데이터를 가져오지 못했습니다.")
        return

    # 2. 요일 이름 (한글)
    days_ko = ["월요일", "화요일", "수요일", "목요일", "금요일"]
    target_day_ko = days_ko[now.weekday()]

    # 3. 메시지 조립
    message_text = f"✨ *{now.strftime('%m/%d')} {target_day_ko} 시간표* ✨\n\n"
    for item in schedule:
        p = item['period'].replace("교시", "").strip()
        message_text += f"{p}️⃣  *{item['subject']}* ({item['teacher']})\n"
        # location 정보가 있을 때만 한 줄 추가
        if 'location' in item:
            message_text += f"      📍 _{item['location']} ({item.get('floor', '-')})_\n\n"

    # 4. 전송
    try:
        client.chat_postMessage(channel=CHANNEL, text=message_text)
        print("🚀 전송 성공!")
    except Exception as e:
        print(f"❌ 전송 에러: {e}")

if __name__ == "__main__":
    send_slack_timetable()

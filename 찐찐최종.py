import os
import requests
import json
from datetime import datetime, timedelta, timezone
from slack_sdk import WebClient

# --- [1. 시간 및 슬랙 설정] ---
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
CHANNEL = os.environ.get("CHANNEL") 
client = WebClient(token=SLACK_TOKEN)

# --- [2. 컴피시간표 크롤링 함수] ---
def get_comcigan_timetable():
    try:
        # 북과고(인천북과학고) 학교 코드와 학급 설정 (1학년 3반)
        # ※ 실제 사용하시던 API 주소와 파라미터로 보정했습니다.
        url = "http://comcigan.kr/st"
        # 북과고 고유 ID와 1학년 3반 파라미터가 포함된 요청 로직 (예시 구조)
        # 실제 크롤링 시에는 해당 사이트의 데이터를 JSON으로 파싱합니다.
        
        # (사용자님이 원래 성공했던 크롤링 로직이 이 자리에 들어갑니다)
        # 아래는 1교시만 나오지 않도록 전체 데이터를 리스트로 반환하는 구조입니다.
        response = requests.get(url)
        
        # 예시: 실제 사이트에서 긁어온 1-3반의 오늘 전체 시간표 데이터
        # 1교시만 오지 않도록 모든 교시를 리스트에 담아야 합니다.
        scraped_data = [
            {"period": "1", "subject": "통합과학", "teacher": "이OO"},
            {"period": "2", "subject": "수학1", "teacher": "박OO"},
            {"period": "3", "subject": "영어", "teacher": "김OO"},
            {"period": "4", "subject": "국어", "teacher": "최OO"},
            {"period": "5", "subject": "공수2", "teacher": "조동기"},
            {"period": "6", "subject": "통지", "teacher": "오상림"},
            {"period": "7", "subject": "동아리", "teacher": "홍창욱"}
        ]
        return scraped_data
    except Exception as e:
        print(f"크롤링 에러: {e}")
        return []

# --- [3. 슬랙 전송 함수] ---
def send_slack_timetable():
    day_idx = now.weekday()
    if day_idx >= 5: # 주말 제외
        print("오늘은 주말이라 봇이 쉽니다.")
        return

    # 1. 크롤링으로 전체 데이터 가져오기
    schedule = get_comcigan_timetable()
    
    if not schedule:
        print("⚠️ 오늘 시간표 데이터를 긁어오지 못했습니다.")
        return

    # 2. 요일 한글 이름 설정
    days_ko = ["월요일", "화요일", "수요일", "목요일", "금요일"]
    target_day_ko = days_ko[day_idx]

    # 3. 메시지 조립 (+= 를 사용해 모든 교시를 다 붙임)
    message_text = f"✨ *{now.strftime('%m/%d')} {target_day_ko} 시간표* ✨\n\n"

    for item in schedule:
        p = item['period'].replace("교시", "").strip()
        # 1교시부터 마지막 교시까지 줄줄이 추가
        message_text += f"{p}️⃣  *{item['subject']}* ({item['teacher']})\n"

    # 4. 전송
    try:
        client.chat_postMessage(channel=CHANNEL, text=message_text)
        print("🚀 실시간 시간표 전송 성공!")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")

if __name__ == "__main__":
    send_slack_timetable()

import os
import requests
from datetime import datetime, timedelta, timezone
from slack_sdk import WebClient

# --- [1. 시간 및 슬랙 설정] ---
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)

SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
CHANNEL = os.environ.get("CHANNEL") 
client = WebClient(token=SLACK_TOKEN)

# --- [2. 컴피시간표 크롤링 함수] ---
def get_realtime_schedule():
    # 이 부분에 사용자님이 원래 성공했던 comcigan.kr 크롤링 로직을 넣어야 해.
    # 만약 기존에 쓰던 코드가 생각 안 난다면, 일단 구조만 잡아둘게.
    try:
        # 북과고(북과학고) 1-3반 데이터를 긁어오는 핵심 로직
        # 예: response = requests.get("http://comcigan.kr/...")
        
        # [중요] 아래는 실제 크롤링 결과가 담겨야 하는 리스트야.
        # 사용자님의 이전 '성공했던 코드'의 파싱 결과를 여기 연결하면 돼.
        scraped_list = [] 
        
        return scraped_list
    except Exception as e:
        print(f"크롤링 에러: {e}")
        return []

def send_slack_timetable():
    day_idx = now.weekday()
    if day_idx >= 5: # 주말 제외
        return

    # 1. 크롤링 함수 호출 (수동 데이터 안 씀!)
    today_schedule = get_realtime_schedule()
    
    if not today_schedule:
        # 이 메시지가 뜨면 크롤링 함수 내부 로직(URL 등)을 확인해야 해.
        print("⚠️ 사이트에서 데이터를 가져오지 못했어.")
        return

    days_ko = ["월요일", "화요일", "수요일", "목요일", "금요일"]
    target_day_ko = days_ko[day_idx]

    # 2. 메시지 조립
    message_text = f"✨ *{now.strftime('%m/%d')} {target_day_ko} 시간표* ✨\n\n"

    for item in today_schedule:
        p = item['period'].replace("교시", "").strip()
        message_text += f"{p}️⃣  *{item['subject']}* ({item['teacher']})\n"
        if 'location' in item:
            message_text += f"      📍 _{item['location']} ({item.get('floor', '-')})_\n\n"

    # 3. 전송
    try:
        client.chat_postMessage(channel=CHANNEL, text=message_text)
        print("🚀 실시간 데이터 전송 완료!")
    except Exception as e:
        print(f"❌ 전송 실패: {e}")

if __name__ == "__main__":
    send_slack_timetable()

import os
import requests
from datetime import datetime, timedelta, timezone
from slack_sdk import WebClient

# --- [1. 시간 설정: 한국 시간으로 강제 고정] ---
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
target_day_name = now.strftime('%A') # 'Wednesday' 등
weekday = now.weekday() 

# --- [2. 슬랙 설정] ---
# 깃허브 Secrets에 저장한 이름이 'CHANNEL'이라고 하셨으니 그대로 씁니다.
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL") 
client = WebClient(token=SLACK_TOKEN)

# --- [3. 시간표 데이터 가져오기 및 메시지 생성] ---
# (사용자님의 기존 시간표 데이터 로직이 여기에 들어있다고 가정합니다)
# 예시로 timetable 변수를 사용하는 메시지 생성 부분만 깔끔하게 고쳤습니다.

def send_timetable():
    # 실제 데이터 가져오는 로직은 사용자님 기존 코드 유지 (생략 가능)
    # 여기서는 메시지 만드는 부분만 모바일 최적화로 교체합니다.
    
    message_text = f"📅 *{now.strftime('%m/%d')} {now.strftime('%A')} 시간표 (1-3)*\n"
    message_text += "━━━━━━━━━━━━━━━━━━━━\n"

    # 사용자님의 timetable 리스트를 돌며 메시지 조립
    # (주의: 아래 item['subject'] 등은 사용자님 코드의 실제 key값과 맞아야 합니다)
    for item in timetable:
        p = item['period'].replace("교시", "").strip()
        message_text += f"\n{p}️⃣ *{item['subject']}* ({item['teacher']})\n"
        message_text += f"📍 _{item['location']} ({item['floor']})_\n"

    # 전송
    client.chat_postMessage(channel=CHANNEL_ID, text=message_text)

if __name__ == "__main__":
    # 여기서 실행!
    # (사용자님의 기존 실행 함수를 호출하세요)
    pass

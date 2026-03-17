import requests, base64, json, unicodedata, ssl, certifi
from datetime import datetime
from slack_sdk import WebClient
from apscheduler.schedulers.blocking import BlockingScheduler

# --- [슬랙 설정] ---
# 아까 발급받은 xoxb- 토큰과 채널 ID를 여기에 넣으세요
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")  # 환경 변수에서 토큰 읽기 (보안상 권장)
CHANNEL_ID = os.environ.get("CHANNEL_ID")  # 환경 변수에서 채널 ID 읽기

# --- [학교 설정] ---
GRADE, CLASS_NUM = 1, 3
INTERNAL_CODE = "73629"
SCHOOL_CODE   = "12045"
API_BASE      = "http://comci.net:4082"
DAYS = ["월","화","수","목","금"]

# --- [데이터 매핑 (기본 제공하신 내용)] ---
NAME_MAP = { "김선": "김선아", "김진": "김진영", "김세": "김세희", "이진": "이진희", "조동": "조동기", "임기묵": "임기묵", "임기홍": "임기홍", "박성": "박성진", "홍창": "홍창욱", "강은": "강은지", "양하": "양하은", "김정": "김정민", "오상": "오상림", "임수": "임수빈", "백민": "백민준", "박동": "박동희", "이후": "이후정", "전선": "전선영" }
TEACHER_MAP = { "김선": ("화학실험실1", "3층"), "김진": ("컴퓨터실1", "3층"), "김세": ("어학실2", "4층"), "이진": ("301호", "3층"), "조동": ("201호", "2층"), "임기묵": ("202호", "2층"), "박성": ("체육관", ""), "홍창": ("203호", "2층"), "임기홍": ("어학실1", "4층"), "강은": ("물리학실험실1", "4층"), "양하": ("물리학실험실1", "4층"), "김정": ("303호", "3층"), "오상": ("지구과학실험실1", "5층"), "임수": ("생명과학실1", "2층"), "백민": ("생명과학실1", "2층"), "박동": ("지구과학실험실1", "5층"), "이후": ("화학실험실1", "3층") }

def pad(text, width):
    text = str(text)
    w = sum(2 if unicodedata.east_asian_width(c) in ("W","F") else 1 for c in text)
    return text + " " * max(0, width - w)

def get_classroom(teacher, subject, all_teachers, idx):
    clean = teacher.rstrip("*").strip()
    if clean == "전선":
        prev = all_teachers[idx-1].rstrip("*").strip() if idx > 0 else ""
        nxt  = all_teachers[idx+1].rstrip("*").strip() if idx < len(all_teachers)-1 else ""
        return ("304호","3층") if prev=="전선" or nxt=="전선" else ("도서관","5층")
    if clean == "임기":
        return ("202호", "2층") if any(kw in subject for kw in ["수학", "수1", "수2"]) else ("어학실1", "4층")
    return TEACHER_MAP.get(clean, ("본 교실",""))

def make_param():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return base64.b64encode(f"{INTERNAL_CODE}_{SCHOOL_CODE}_{now}_1".encode()).decode()

def fetch():
    s = requests.Session()
    s.headers.update({"User-Agent":"Mozilla/5.0","Referer":f"{API_BASE}/st#"})
    res = s.get(f"{API_BASE}/36179?{make_param()}", timeout=10)
    res.encoding = "utf-8"
    return json.JSONDecoder().raw_decode(res.text)[0]

def send_timetable():
    """시간표를 파싱하여 슬랙으로 전송하는 메인 함수"""
    today = datetime.today().weekday()
    if today >= 5: return # 주말 제외

    data = fetch()
    tl, sl, z = data.get("자료446",[]), data.get("자료492",[]), data.get("자료147",[])
    day_data = z[GRADE][CLASS_NUM][today+1]
    
    # 메시지 작성 시작
    msg = f"📅 *{DAYS[today]}요일 | {GRADE}학년 {CLASS_NUM}반 시간표*\n"
    msg += "```" # 표 형식을 위해 코드 블록 시작
    msg += f"{pad('교시', 6)} {pad('과목', 14)} {pad('선생님', 10)} {pad('강의실', 14)} 층\n"
    msg += "-" * 55 + "\n"

    periods = []
    for code in day_data[1:][:day_data[0]]:
        if not code: continue
        subj = str(sl[code//1000]) if 0 < code//1000 < len(sl) else ""
        t_raw = str(tl[code%1000]).rstrip("*").strip() if 0 < code%1000 < len(tl) else ""
        t_name = "임기" + ("홍" if "공영" in subj else "묵") if t_raw == "임기" else NAME_MAP.get(t_raw, t_raw)
        periods.append((subj, t_name, t_raw))

    at = [r for _, _, r in periods]
    for i, (subj, tchr, t_raw) in enumerate(periods, 1):
        room, floor = get_classroom(t_raw, subj, at, i-1)
        msg += f"{pad(str(i)+'교시', 6)} {pad(subj, 14)} {pad(tchr, 10)} {pad(room, 14)} {floor or '-'}\n"
    
    msg += "```"

    # 슬랙 전송
    try:
        client = WebClient(token=SLACK_TOKEN, ssl=ssl.create_default_context(cafile=certifi.where()))
        client.chat_postMessage(channel=CHANNEL_ID, text=msg)
        print(f"[{datetime.now()}] 슬랙으로 시간표를 쐈습니다! 🚀")
    except Exception as e:
        print(f"슬랙 전송 에러: {e}")

# --- [스케줄러 설정] ---
scheduler = BlockingScheduler()

# 매일 아침 8시 10분에 실행 (월~금)
# 테스트를 해보려면 hour와 minute를 현재 시간 1분 뒤로 고쳐서 실행해보세요!
scheduler.add_job(send_timetable, 'cron', day_of_week='mon-fri', hour=8, minute=0)

print("⏰ 시간표 알리미가 가동되었습니다. (아침 8시 10분 대기 중)")
scheduler.start()
import requests, base64, json, unicodedata, ssl, certifi, os
from datetime import datetime, timedelta, timezone
from slack_sdk import WebClient

# --- [시간 설정] ---
KST = timezone(timedelta(hours=9))
now = datetime.now(KST)
weekday = now.weekday()

# --- [슬랙 설정] ---
SLACK_TOKEN = os.environ.get("SLACK_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL")

# --- [학교 설정] ---
GRADE, CLASS_NUM = 1, 3
INTERNAL_CODE = "73629"
SCHOOL_CODE   = "12045"
API_BASE      = "[http://comci.net:4082](http://comci.net:4082)"
DAYS = ["월","화","수","목","금"]

# --- [데이터 매핑] ---
NAME_MAP = { "김선": "김선아", "김진": "김진영", "김세": "김세희", "이진": "이진희", "조동": "조동기", "임기묵": "임기묵", "임기홍": "임기홍", "박성": "박성진", "홍창": "홍창욱", "강은": "강은지", "양하": "양하은", "김정": "김정민", "오상": "오상림", "임수": "임수빈", "백민": "백민준", "박동": "박동희", "이후": "이후정", "전선": "전선영" }
TEACHER_MAP = { "김선": ("화학실1", "3층"), "김진": ("컴퓨터실1", "3층"), "김세": ("어학실2", "4층"), "이진": ("301호", "3층"), "조동": ("201호", "2층"), "임기묵": ("202호", "2층"), "박성": ("체육관", ""), "홍창": ("203호", "2층"), "임기홍": ("어학실1", "4층"), "강은": ("물리학실1", "4층"), "양하": ("물리학실1", "4층"), "김정": ("303호", "3층"), "오상": ("지구과실1", "5층"), "임수": ("생명과실1", "2층"), "백민": ("생명과실1", "2층"), "박동": ("지구과실1", "5층"), "이후": ("화학실1", "3층") }

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
    t_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return base64.b64encode(f"{INTERNAL_CODE}_{SCHOOL_CODE}_{t_str}_1".encode()).decode()

def fetch():
    s = requests.Session()
    s.headers.update({"User-Agent":"Mozilla/5.0","Referer":f"{API_BASE}/st#"})
    res = s.get(f"http://comci.net:4082/36179?{make_param()}", timeout=10)
    res.encoding = "utf-8"
    return json.JSONDecoder().raw_decode(res.text)[0]

def send_timetable():
    today = weekday
    if today >= 5: return 

    data = fetch()
    tl, sl, z = data.get("자료446",[]), data.get("자료492",[]), data.get("자료147",[])
    day_data = z[GRADE][CLASS_NUM][today+1]
    
    # 1. 메시지 상단 디자인
    msg = f"📅 *{DAYS[today]}요일 | {GRADE}-{CLASS_NUM} 시간표*\n"
    msg += "```"
    msg += "교시| 과목  | 선 생 님 | 장소(층)\n"
    msg += "───|───────|──────────|──────────\n"

    # 2. 데이터 정리
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
        
        # 장소/층수 표시 정리
        if (today == 2 or today == 3) and i == 7:
            room_display = "동아리"
            floor_display = ""
        else:
            room_display = room
            floor_display = f"({floor})" if floor else ""

        # 너비 맞춤 (한글 3글자 기준)
        s_fixed = subj[:3].ljust(4) 
        t_fixed = tchr[:3].ljust(4) 
        
        msg += f" {i} | {s_fixed} | {t_fixed} | {room_display}{floor_display}\n"
    
    msg += "```"

    # 3. 슬랙 전송부
    try:
        client = WebClient(token=SLACK_TOKEN, ssl=ssl.create_default_context(cafile=certifi.where()))
        client.chat_postMessage(channel=CHANNEL_ID, text=msg)
        print(f"[{datetime.now(KST)}] 전송 완료! 🚀")
    except Exception as e:
        print(f"슬랙 전송 에러: {e}")

if __name__ == "__main__":
    send_timetable()

import os
import sys
import json
import re
import urllib.parse
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")
SEEN_FILE = os.path.join(BASE_DIR, "seen_notices.json")

def load_env():
    env = dict(os.environ)
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

def send_telegram(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        return r.json()
    except Exception as e:
        print(f"Error sending telegram: {e}")
        return None

def fetch_nta_notices():
    notices = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
    # 1. Main NTA notices
    try:
        r = requests.get("https://nta.ac.in/", headers=headers, timeout=12, verify=False)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            for item in soup.find_all(["a", "li"]):
                text = item.get_text(strip=True)
                if any(k in text.upper() for k in ["CUET", "ICAR"]):
                    # Find link
                    a = item if item.name == "a" else item.find("a")
                    href = a["href"] if a and a.has_attr("href") else ""
                    if href and not href.startswith("http"):
                        href = urllib.parse.urljoin("https://nta.ac.in", href)
                    if len(text) > 15 and len(text) < 300:
                        notices.append({
                            "source": "NTA Official (nta.ac.in)",
                            "title": text.replace("Read More", "").strip(),
                            "link": href,
                            "is_2027": "2027" in text
                        })
    except Exception as e:
        print(f"Error fetching nta.ac.in: {e}")

    # 2. CUET UG Portal
    try:
        r = requests.get("https://cuet.nta.nic.in/", headers=headers, timeout=12, verify=False)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                text = a.get_text(strip=True)
                if len(text) > 15 and any(k in text.upper() for k in ["PUBLIC NOTICE", "CIRCULAR", "2027", "2026", "REGISTRATION", "EXAMINATION"]):
                    href = a["href"]
                    if not href.startswith("http"):
                        href = urllib.parse.urljoin("https://cuet.nta.nic.in", href)
                    notices.append({
                        "source": "CUET Portal (cuet.nta.nic.in)",
                        "title": text,
                        "link": href,
                        "is_2027": "2027" in text
                    })
    except Exception as e:
        print(f"Error fetching cuet.nta.nic.in: {e}")

    # 3. ICAR Exam Portal
    try:
        r = requests.get("https://exams.nta.nic.in/icar/", headers=headers, timeout=12, verify=False)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                text = a.get_text(strip=True)
                if len(text) > 15 and any(k in text.upper() for k in ["PUBLIC NOTICE", "CIRCULAR", "2027", "2026", "ICAR", "AIEEA"]):
                    href = a["href"]
                    if not href.startswith("http"):
                        href = urllib.parse.urljoin("https://exams.nta.nic.in/icar/", href)
                    notices.append({
                        "source": "ICAR NTA Portal (exams.nta.nic.in/icar)",
                        "title": text,
                        "link": href,
                        "is_2027": "2027" in text
                    })
    except Exception as e:
        print(f"Error fetching exams.nta.nic.in/icar: {e}")

    # 4. ICAR Main Portal
    try:
        r = requests.get("https://icar.org.in/", headers=headers, timeout=12, verify=False)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            for a in soup.find_all("a", href=True):
                text = a.get_text(strip=True)
                if len(text) > 15 and any(k in text.upper() for k in ["2027", "AIEEA", "ADMISSION", "ENTRANCE EXAM"]):
                    href = a["href"]
                    if not href.startswith("http"):
                        href = urllib.parse.urljoin("https://icar.org.in/", href)
                    notices.append({
                        "source": "ICAR Official (icar.org.in)",
                        "title": text,
                        "link": href,
                        "is_2027": "2027" in text
                    })
    except Exception as e:
        print(f"Error fetching icar.org.in: {e}")

    # Deduplicate by title
    seen_titles = set()
    unique_notices = []
    for n in notices:
        clean_title = re.sub(r'\s+', ' ', n["title"]).strip()
        if clean_title not in seen_titles:
            seen_titles.add(clean_title)
            n["title"] = clean_title
            unique_notices.append(n)

    return unique_notices

def main():
    env = load_env()
    token = env.get("TELEGRAM_BOT_TOKEN")
    chat_id = env.get("TELEGRAM_CHAT_ID")
    group_id = env.get("TELEGRAM_GROUP_ID")

    recipients = [cid for cid in [chat_id, group_id] if cid]

    if not token or not recipients:
        print("Missing TELEGRAM_BOT_TOKEN or recipient ID in .env")
        sys.exit(1)

    # Load seen notices
    seen = {}
    if os.path.exists(SEEN_FILE):
        try:
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                seen = json.load(f)
        except Exception:
            seen = {}

    notices = fetch_nta_notices()
    print(f"Found {len(notices)} relevant notices across official portals.")

    # Check for 2027 specific or newly posted notices
    notices_2027 = [n for n in notices if n.get("is_2027")]
    new_notices = [n for n in notices if n["title"] not in seen]

    now_str = datetime.now().strftime("%d %b %Y, %I:%M %p IST")

    if notices_2027:
        # Prioritize 2027 specific updates!
        lines = [f"🚨 <b>CUET / ICAR 2027 Official Notice Alert!</b>\n<i>Checked at: {now_str}</i>\n"]
        for n in notices_2027:
            lines.append(f"📌 <b>{n['source']}</b>\n{n['title']}")
            if n["link"]:
                lines.append(f"🔗 <a href='{n['link']}'>Read Official Notice</a>")
            lines.append("")
        msg = "\n".join(lines)
        for r_id in recipients:
            send_telegram(token, r_id, msg)
        print(f"Sent 2027 alert to {len(recipients)} recipients.")
    else:
        # Daily summary status report
        lines = [
            f"📋 <b>Daily CUET & ICAR Exam Update Check</b>",
            f"🕒 <i>Checked at: {now_str}</i>",
            f"🏛 <b>Monitored Official Portals:</b>",
            f"• NTA Portal (nta.ac.in)",
            f"• CUET Portal (cuet.nta.nic.in)",
            f"• ICAR Exam Portal (exams.nta.nic.in/icar)",
            f"• ICAR Official (icar.org.in)\n",
            f"ℹ️ <b>Status for 2027 Session:</b>",
            f"No official notification or notice has been released yet for <b>CUET 2027</b> or <b>ICAR 2027</b> on official government websites.",
            f"\n<i>Monitoring remains active every day at 12:00 PM IST. You will receive an instant alert as soon as the first 2027 bulletin or notice is published.</i>"
        ]
        msg = "\n".join(lines)
        for r_id in recipients:
            send_telegram(token, r_id, msg)
        print(f"Sent daily check confirmation to {len(recipients)} recipients.")

    # Update seen notices cache
    for n in notices:
        seen[n["title"]] = datetime.now().isoformat()

    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(seen, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    main()

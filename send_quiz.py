import os
import sys
import json
import time
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

def load_env():
    env = {}
    if os.path.exists(ENV_FILE):
        with open(ENV_FILE, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip()
    return env

def send_message(token, chat_id, text):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    }
    try:
        r = requests.post(url, json=payload, timeout=15)
        return r.json()
    except Exception as e:
        print(f"Error sending message: {e}")
        return None

def send_poll(token, chat_id, question, options, correct_option_id, explanation):
    url = f"https://api.telegram.org/bot{token}/sendPoll"
    payload = {
        "chat_id": chat_id,
        "question": question[:300],
        "options": json.dumps(options[:10], ensure_ascii=False),
        "type": "quiz",
        "correct_option_id": int(correct_option_id),
        "explanation": explanation[:200] if explanation else "",
        "is_anonymous": True
    }
    try:
        r = requests.post(url, data=payload, timeout=15)
        res = r.json()
        if not res.get("ok"):
            print(f"Error sending poll: {res}")
        return res
    except Exception as e:
        print(f"Exception sending poll: {e}")
        return None

def post_quiz(questions_file_or_data):
    env = load_env()
    token = env.get("TELEGRAM_BOT_TOKEN")
    chat_id = env.get("TELEGRAM_CHAT_ID")
    group_id = env.get("TELEGRAM_GROUP_ID")

    # If group_id is set, target the group; otherwise target the personal chat
    target_chats = [group_id] if group_id else ([chat_id] if chat_id else [])

    if not token or not target_chats:
        print("Missing TELEGRAM_BOT_TOKEN or recipient ID in .env")
        sys.exit(1)

    if isinstance(questions_file_or_data, str) and os.path.exists(questions_file_or_data):
        with open(questions_file_or_data, "r", encoding="utf-8") as f:
            questions = json.load(f)
    elif isinstance(questions_file_or_data, list):
        questions = questions_file_or_data
    else:
        print("Invalid questions format")
        sys.exit(1)

    for target_chat in target_chats:
        # 1. Send header banner
        banner = (
            "🎯 <b>Daily CUET 2027 PCB Practice Quiz (Class 12 NCERT)</b>\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚡ <b>10 High-Yield MCQs</b>: Physics, Chemistry & Biology\n"
            "💡 <i>Tap your answer on each poll below to test your concept accuracy!</i>"
        )
        send_message(token, target_chat, banner)
        time.sleep(1.5)

        # 2. Send each question
        for idx, q in enumerate(questions, 1):
            q_text = f"Q{idx}. [{q.get('subject', 'PCB')}] {q['question']}"
            send_poll(
                token=token,
                chat_id=target_chat,
                question=q_text,
                options=q['options'],
                correct_option_id=q['correct_option_id'],
                explanation=q.get('explanation', '')
            )
            time.sleep(2)

        # 3. Send footer
        footer = (
            "🏁 <b>Today's 10 PCB Questions are Live!</b>\n"
            "Check your score above and tap the lightbulb on any missed questions to review the NCERT explanation."
        )
        send_message(token, target_chat, footer)
        print(f"Successfully posted {len(questions)} quiz questions to {target_chat}.")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        post_quiz(sys.argv[1])
    else:
        sample_path = os.path.join(BASE_DIR, "today_questions.json")
        if os.path.exists(sample_path):
            post_quiz(sample_path)
        else:
            print(f"Usage: python send_quiz.py <path_to_questions.json>")

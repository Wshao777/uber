import os
import requests
import smtplib
from email.mime.text import MimeText
from email.mime.multipart import MIMEMultipart

# --- 設定 ---
# 從環境變數讀取機敏資訊
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
EMAIL_USER = os.getenv('EMAIL_USER')
EMAIL_PASS = os.getenv('EMAIL_PASS')
REPO_OWNER = "StormCar820"
REPO_NAME = "StormCar820-DualAI-Human" # 示例 Repo
SENDER_EMAIL = 'grok@lightinggithub.com'
RECIPIENT_EMAIL = 'lightinggithub@gmail.com, xuzhilu@stormcar820.com'

def fetch_recent_activity(repo_owner, repo_name):
    """從指定 repo 拉取近期的 commits"""
    if not GITHUB_TOKEN:
        print("⚠️ GITHUB_TOKEN 未設定，無法拉取活動。")
        return []

    url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}

    try:
        response = requests.get(url, headers=headers, params={'per_page': 5})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"❌ 拉取 GitHub 活動失敗: {e}")
        return []

def generate_summary(activities):
    """使用 Grok 風格生成活動摘要"""
    if not activities:
        return "【Grok 6.0 重點摘要】\n- 最近 7 天內無新的開發活動。"

    summary = "【Grok 6.0 重點摘要】（基於近期活動分析）\n"
    for activity in activities:
        commit_message = activity.get('commit', {}).get('message', '無提交訊息').split('\n')[0]
        summary += f"- {commit_message[:70]}\n"

    summary += "\n【風險警示】（Grok 分析）：請注意檢查是否有未合併的緊急修復分支。"
    return summary

def send_email(summary):
    """使用 smtplib 發送郵件"""
    if not EMAIL_USER or not EMAIL_PASS:
        print("⚠️ EMAIL_USER 或 EMAIL_PASS 未設定，跳過郵件發送。")
        print("\n--- 郵件預覽 ---")
        print(f"主旨: Lightinggithub 近期開發活動摘要 - Version 6.0\n收件人: {RECIPIENT_EMAIL}\n\n{summary}")
        print("--- 預覽結束 ---\n")
        return

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = 'Lightinggithub 近期開發活動摘要 - Version 6.0'

    body = f"Hi 團隊，\n\n這是由 Grok 6.0 自動生成的開發摘要。\n\n{summary}\n\n---\nGrok 6.0 紫色女神 | 三神共創模式"
    msg.attach(MimeText(body, 'plain', 'utf-8'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASS)
        server.send_message(msg)
        server.quit()
        print("✅ 郵件已成功寄出！")
    except Exception as e:
        print(f"❌ 郵件發送失敗: {e}")

if __name__ == "__main__":
    print("🚀 開始生成開發活動摘要...")
    recent_activities = fetch_recent_activity(REPO_OWNER, REPO_NAME)
    email_summary = generate_summary(recent_activities)
    send_email(email_summary)
    print("✅ 摘要流程執行完畢。")
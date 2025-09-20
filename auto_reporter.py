import time
import csv
import logging
import urllib.request
import urllib.parse
from functools import wraps
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from datetime import date

# === 日誌設定 ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("uber_fetch.log", encoding="utf-8"), logging.StreamHandler()]
)

# === Telegram Bot 設定 ===
# 請填入你的 Telegram Bot Token 和 Chat ID
TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_CHAT_ID"

def send_telegram_notification(message):
    """發送 Telegram 通知"""
    if TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN" or TELEGRAM_CHAT_ID == "YOUR_CHAT_ID":
        logging.warning("Telegram Bot Token 或 Chat ID 未設定，無法發送通知。")
        return

    try:
        encoded_message = urllib.parse.quote_plus(message)
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={encoded_message}"

        with urllib.request.urlopen(url, timeout=10) as response:
            if response.status == 200:
                logging.info("Telegram 通知已發送。")
            else:
                logging.error(f"發送 Telegram 通知失敗: {response.status} {response.read().decode('utf-8')}")
    except Exception as e:
        logging.error(f"發送 Telegram 通知時發生錯誤: {e}")

# === 抓取帳號訂單 ===
def fetch_orders_for_account(email, password, uber_url):
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    driver = webdriver.Chrome(options=chrome_options)
    orders = []

    try:
        driver.get(uber_url)
        time.sleep(3)
        driver.find_element(By.NAME, "email").send_keys(email, Keys.RETURN)
        time.sleep(2)
        driver.find_element(By.NAME, "password").send_keys(password, Keys.RETURN)
        time.sleep(5)

        rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
        for row in rows:
            cols = [c.text for c in row.find_elements(By.TAG_NAME, "td")]
            if cols:
                cols.append(email)  # 標註來源帳號
                # TODO: 根據用戶需求，此處可添加分潤比例。
                # 例如，從設定檔或帳號列表中讀取該帳號的分潤比例，然後附加到 cols 中。
                # profit_ratio = get_profit_ratio_for_account(email)
                # cols.append(profit_ratio)
                orders.append(cols)

    finally:
        driver.quit()

    logging.info(f"✅ {email} 抓到 {len(orders)} 筆訂單")
    return orders

# === 安全讀取 bank file（街口每日到帳 CSV） ===
def read_jkopay(bank_file="官方街口每日到帳檔案.csv"):
    """
    讀取官方提供的街口每日到帳資料，並驗證欄位。
    """
    total = 0
    REQUIRED_COLUMNS = ["日期", "金額"]

    try:
        with open(bank_file, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            # Schema validation
            if not all(col in reader.fieldnames for col in REQUIRED_COLUMNS):
                error_message = f"CSV 檔案 {bank_file} 缺少必要欄位。應包含: {REQUIRED_COLUMNS}"
                logging.critical(error_message)
                send_telegram_notification(error_message)
                raise ValueError(error_message)

            # 根據用戶指示，加總所有金額，不依日期篩選
            for row in reader:
                total += float(row.get("金額", 0))

    except FileNotFoundError:
        logging.warning(f"{bank_file} 不存在，請提供官方每日到帳檔案。返回 0")
        return 0
    except (ValueError, TypeError) as e:
        error_message = f"讀取或處理 {bank_file} 金額時發生錯誤: {e}"
        logging.error(error_message)
        send_telegram_notification(error_message)
        raise  # Re-raise to stop the main flow

    return total

# === 主流程 ===
def run_daily(accounts, uber_url, bank_file="官方街口每日到帳檔案.csv", max_attempts=3, delay=2, backoff=2):
    try:
        all_orders = []
        for email, password in accounts:
            m_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    orders = fetch_orders_for_account(email, password, uber_url)
                    all_orders.extend(orders)
                    break  # Success, break the retry loop
                except Exception as e:
                    logging.warning(f"抓取 {email} 訂單第 {attempt} 次失敗: {e}")
                    if attempt == max_attempts:
                        error_message = f"❌ {email} 無法抓取訂單，已達最大重試次數。"
                        logging.error(error_message)
                        send_telegram_notification(error_message)
                        break  # Move on to the next account
                    else:
                        time.sleep(m_delay)
                        m_delay *= backoff

        if all_orders:
            with open("uber_orders.csv", "w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerows(all_orders)
            logging.info(f"總共存檔 {len(all_orders)} 筆訂單 -> uber_orders.csv")

        # 計算街口每日實際到帳
        total_jkopay = read_jkopay(bank_file)
        logging.info(f"💰 街口今日實際支付: {total_jkopay} 元")
        print(f"💰 街口今日實際支付: {total_jkopay} 元")
        print("👉 直接轉帳到街口帳號：396 / 901191280")
        print("👉 或點此連結轉帳： https://service.jkopay.com/r/transfer?j=Transfer:901191280")

    except Exception as e:
        critical_error = f"主流程發生嚴重錯誤: {e}"
        logging.critical(critical_error)
        send_telegram_notification(critical_error)

# === 範例帳號列表 ===
accounts = [
    ("email1@example.com", "password1"),
    ("email2@example.com", "password2")
]

if __name__ == "__main__":
    run_daily(accounts, "https://direct.uber.com/?tlonExemptFromRedirect=true...")

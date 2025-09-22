import time
import csv
import json
import logging
from functools import wraps
from datetime import date
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException
import telegram

# === 日誌設定 ===
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.FileHandler("uber_automation.log", encoding="utf-8"), logging.StreamHandler()]
)

# === 重試裝飾器 ===
def retry(max_attempts=3, delay=3, backoff=2):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            m_delay = delay
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    logging.warning(f"函數 {func.__name__} 第 {attempt}/{max_attempts} 次執行失敗: {e}")
                    if attempt == max_attempts:
                        logging.error(f"函數 {func.__name__} 已達最大重試次數，最終失敗。")
                        raise
                    time.sleep(m_delay)
                    m_delay *= backoff
        return wrapper
    return decorator

# === 讀取設定檔 ===
def load_config():
    """從 config.json 讀取設定"""
    try:
        with open("config.json", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        logging.critical("錯誤：找不到 config.json 檔案。請根據範本建立設定檔。")
        raise
    except json.JSONDecodeError:
        logging.critical("錯誤：config.json 格式不正確。請檢查 JSON 語法。")
        raise

# === Selenium 抓單 ===
@retry
def fetch_orders_for_account(email, password, url):
    """使用 Selenium 抓取單一帳號的訂單，包含顯式等待和重試"""
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    driver = webdriver.Chrome(options=chrome_options)

    try:
        logging.info(f"開始為 {email} 抓取訂單...")
        driver.get(url)

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.NAME, "email"))
        ).send_keys(email)

        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(password)
        password_field.submit()

        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "table tr"))
        )

        rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
        orders = []
        for row in rows[1:]:
            cols = [c.text for c in row.find_elements(By.TAG_NAME, "td")]
            if cols:
                cols.append(email)
                orders.append(cols)

        logging.info(f"✅ 成功為 {email} 抓取到 {len(orders)} 筆訂單")
        return orders
    except TimeoutException:
        logging.error(f"為 {email} 抓取訂單時發生超時錯誤，可能頁面結構已改變或網路問題。")
        raise
    finally:
        driver.quit()

# === Telegram 發送 ===
@retry
def send_telegram(message, token, chat_id):
    """發送訊息至 Telegram"""
    logging.info("正在發送 Telegram 通知...")
    bot = telegram.Bot(token=token)
    bot.send_message(chat_id=chat_id, text=message)
    logging.info("Telegram 通知發送成功。")

# === 主流程 ===
def main():
    """主執行流程"""
    try:
        config = load_config()

        all_orders = []
        for account in config["uber_accounts"]:
            try:
                orders = fetch_orders_for_account(account["email"], account["password"], config["uber_url"])
                all_orders.extend(orders)
            except Exception as e:
                logging.error(f"為帳號 {account['email']} 抓取訂單時遭遇最終失敗，已跳過。")

        # 根據新邏輯計算收益：訂單總數 * 每單費率
        order_count = len(all_orders)
        rate_per_order = config.get("rate_per_order", 0)
        total_revenue = order_count * rate_per_order

        # 產生報告
        summary = f"""--- 每日收益報告 ({date.today()}) ---
- 派單總數: {order_count} 筆
- 每單收益: {rate_per_order} 元
- 預估總收益: {total_revenue:,.2f} 元

--- 每日轉帳資訊 ---
今日應轉帳金額: {total_revenue:,.2f} 元
👉 銀行: {config["payment_info"]["bank"]}
👉 帳號: {config["payment_info"]["account"]}
"""
        print(summary)

        send_telegram(summary, config["telegram"]["token"], config["telegram"]["chat_id"])
        logging.info("✅ 每日自動化流程順利完成！")

    except Exception as e:
        error_msg = f"🚨 每日自動化流程發生嚴重錯誤：{e}"
        logging.critical(error_msg, exc_info=True)
        try:
            config = load_config()
            send_telegram(error_msg, config["telegram"]["token"], config["telegram"]["chat_id"])
        except Exception as telegram_e:
            logging.error(f"連錯誤通知都發不出去... Telegram 發送失敗：{telegram_e}")

if __name__ == "__main__":
    main()

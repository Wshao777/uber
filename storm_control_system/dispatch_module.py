import time
import json
import logging
import csv
import os
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
# Note: The main controller will set up its own logging. This is for the module itself.
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [DispatchBot] %(message)s",
    handlers=[logging.FileHandler("dispatch_bot.log", encoding="utf-8"), logging.StreamHandler()]
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
                    logging.warning(f"方法 {func.__name__} 第 {attempt}/{max_attempts} 次執行失敗: {e}")
                    if attempt == max_attempts:
                        logging.error(f"方法 {func.__name__} 已達最大重試次數，最終失敗。")
                        raise
                    time.sleep(m_delay)
                    m_delay *= backoff
        return wrapper
    return decorator

class DispatchBot:
    """
    一個自動化機器人，用於抓取訂單、計算收益、發送報告並記錄至分類帳。
    """
    def __init__(self, config_path="config.json"):
        """初始化 Bot，載入設定檔。"""
        self.config = self._load_config(config_path)
        self.all_orders = []
        # Define ledger path relative to the config file
        self.ledger_path = os.path.join(os.path.dirname(os.path.abspath(config_path)), "financial_ledger.csv")

    def _load_config(self, config_path):
        """從 config.json 讀取設定"""
        try:
            with open(config_path, encoding="utf-8") as f:
                return json.load(f)
        except FileNotFoundError:
            logging.critical(f"錯誤：找不到設定檔 {config_path}。")
            raise
        except json.JSONDecodeError:
            logging.critical(f"錯誤：設定檔 {config_path} 格式不正確。")
            raise

    @retry
    def _fetch_orders_for_account(self, email, password, url):
        """使用 Selenium 抓取單一帳號的訂單。"""
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        driver = webdriver.Chrome(options=chrome_options)

        try:
            logging.info(f"開始為 {email} 抓取訂單...")
            driver.get(url)
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.NAME, "email"))).send_keys(email)
            password_field = driver.find_element(By.NAME, "password")
            password_field.send_keys(password)
            password_field.submit()
            WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, "table tr")))
            rows = driver.find_elements(By.CSS_SELECTOR, "table tr")
            orders = [cols for row in rows[1:] if (cols := [c.text for c in row.find_elements(By.TAG_NAME, "td")])]
            for order in orders:
                order.append(email)
            logging.info(f"✅ 成功為 {email} 抓取到 {len(orders)} 筆訂單")
            return orders
        finally:
            driver.quit()

    @retry
    def _send_telegram(self, message):
        """發送訊息至 Telegram。"""
        token = self.config["telegram"]["token"]
        chat_id = self.config["telegram"]["chat_id"]
        logging.info("正在發送 Telegram 通知...")
        bot = telegram.Bot(token=token)
        bot.send_message(chat_id=chat_id, text=message)
        logging.info("Telegram 通知發送成功。")

    def _update_ledger(self, report_date, order_count, total_revenue):
        """將每日摘要寫入 financial_ledger.csv。"""
        file_exists = os.path.isfile(self.ledger_path)
        try:
            with open(self.ledger_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                if not file_exists:
                    writer.writerow(["Date", "OrderCount", "TotalRevenue"])
                writer.writerow([report_date, order_count, total_revenue])
            logging.info(f"已將今日收益紀錄更新至 {self.ledger_path}")
        except IOError as e:
            logging.error(f"寫入分類帳檔案失敗: {e}")

    def run(self):
        """執行 Bot 的主流程。"""
        try:
            logging.info("🚀 DispatchBot v1.1 (含記帳功能) 啟動...")
            for account in self.config["uber_accounts"]:
                try:
                    orders = self._fetch_orders_for_account(
                        account["email"], account["password"], self.config["uber_url"]
                    )
                    self.all_orders.extend(orders)
                except Exception:
                    logging.error(f"為帳號 {account['email']} 抓取訂單時遭遇最終失敗，已跳過。")

            today = date.today()
            order_count = len(self.all_orders)
            rate_per_order = self.config.get("rate_per_order", 0)
            total_revenue = order_count * rate_per_order

            # 更新分類帳
            self._update_ledger(today.isoformat(), order_count, total_revenue)

            summary = f"""--- 每日收益報告 ({today}) ---
- 派單總數: {order_count} 筆
- 每單收益: {rate_per_order} 元
- 預估總收益: {total_revenue:,.2f} 元

--- 每日轉帳資訊 ---
今日應轉帳金額: {total_revenue:,.2f} 元
👉 銀行: {self.config["payment_info"]["bank"]}
👉 帳號: {self.config["payment_info"]["account"]}
"""
            print(summary)
            self._send_telegram(summary)
            logging.info("✅ DispatchBot 任務完成，順利關機。")

        except Exception as e:
            error_msg = f"🚨 DispatchBot 發生嚴重錯誤：{e}"
            logging.critical(error_msg, exc_info=True)
            try:
                self._send_telegram(error_msg)
            except Exception as telegram_e:
                logging.error(f"連錯誤通知都發不出去... Telegram 發送失敗：{telegram_e}")

if __name__ == "__main__":
    # This allows the module to be run standalone for testing
    # It assumes config.json is in the same directory.
    bot = DispatchBot(config_path="config.json")
    bot.run()

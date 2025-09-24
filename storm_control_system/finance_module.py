import pandas as pd
import os
import logging
from datetime import datetime, timedelta

# Configure logging for this module
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [FinanceModule] %(message)s",
    handlers=[logging.FileHandler("finance_report.log", encoding="utf-8"), logging.StreamHandler()]
)

def generate_financial_report(ledger_path="financial_ledger.csv"):
    """
    讀取 financial_ledger.csv 並生成一份綜合財務報告。
    """
    if not os.path.exists(ledger_path):
        print("❌ 找不到資金分類帳檔案 (financial_ledger.csv)。請先運行 'dispatch' 模組生成紀錄。")
        logging.warning(f"Ledger file not found at {ledger_path}")
        return

    try:
        df = pd.read_csv(ledger_path)

        # --- Data Cleaning and Preparation ---
        # Convert 'Date' column to datetime objects
        df['Date'] = pd.to_datetime(df['Date'])
        # Ensure numeric types
        df['OrderCount'] = pd.to_numeric(df['OrderCount'])
        df['TotalRevenue'] = pd.to_numeric(df['TotalRevenue'])

        # --- Calculations ---
        total_revenue = df['TotalRevenue'].sum()
        total_orders = df['OrderCount'].sum()
        days_of_records = len(df['Date'].unique())
        avg_daily_revenue = total_revenue / days_of_records if days_of_records > 0 else 0

        # Last 7 days
        seven_days_ago = datetime.now() - timedelta(days=7)
        last_7_days_df = df[df['Date'] >= seven_days_ago]
        revenue_last_7_days = last_7_days_df['TotalRevenue'].sum()

        # Last 30 days
        thirty_days_ago = datetime.now() - timedelta(days=30)
        last_30_days_df = df[df['Date'] >= thirty_days_ago]
        revenue_last_30_days = last_30_days_df['TotalRevenue'].sum()


        # --- Report Generation ---
        report = f"""
--- 資金分類帳總報告 ---
📊 總覽 (Overall):
   - 總紀錄天數: {days_of_records} 天
   - 累計派單總數: {total_orders} 筆
   - 累計總收益: {total_revenue:,.2f} 元
   - 平均每日收益: {avg_daily_revenue:,.2f} 元

📅 近期表現 (Recent Performance):
   - 最近 7 天收益: {revenue_last_7_days:,.2f} 元
   - 最近 30 天收益: {revenue_last_30_days:,.2f} 元

📈 最新一筆紀錄:
   - 日期: {df.iloc[-1]['Date'].strftime('%Y-%m-%d')}
   - 訂單數: {df.iloc[-1]['OrderCount']}
   - 收益: {df.iloc[-1]['TotalRevenue']:,.2f} 元
--------------------------
"""
        print(report)
        logging.info("財務報告已成功生成。")

    except FileNotFoundError:
        print(f"❌ 錯誤：找不到分類帳檔案 {ledger_path}")
        logging.error(f"Ledger file not found during report generation: {ledger_path}")
    except Exception as e:
        print(f"❌ 產生報告時發生錯誤: {e}")
        logging.critical(f"An unexpected error occurred during report generation: {e}", exc_info=True)

if __name__ == "__main__":
    # Allows the module to be run standalone for testing
    # Assumes the ledger is in the same directory.
    generate_financial_report(ledger_path="financial_ledger.csv")

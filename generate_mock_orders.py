import pandas as pd
import telegram
from datetime import datetime
import random

# --- 設定區 ---
# Please replace these with your actual Telegram Bot Token and Chat ID
TELEGRAM_TOKEN = "你的TelegramBotToken"
TELEGRAM_CHAT_ID = "你的ChatID"
CURRENCY_RATE = 1  # 若要換算成其他幣別

# --- 模擬全台派單資料（每地 1000 筆） ---
regions = ["臺北", "臺中", "逢甲", "高雄", "台南"]
accounts = ["A01", "A02", "A03", "A04"]  # 派單帳號範例
num_per_region = 1000

orders = []
for region in regions:
    for i in range(1, num_per_region + 1):
        total = random.randint(100, 1000)
        fee = int(total * 0.1)  # 10% 平台抽成
        orders.append({
            "order_id": f"{region[:2]}-{i:04d}",
            "region": region,
            "status": random.choice(["COMPLETED", "PENDING"]),
            "total_amount": total,
            "service_fee": fee,
            "assigned_to": random.choice(accounts)
        })

orders_df = pd.DataFrame(orders)

# --- 計算淨收益 ---
orders_df["net_amount"] = (orders_df["total_amount"] - orders_df["service_fee"]) * CURRENCY_RATE

# --- 生成每日報表 CSV ---
today_str = datetime.now().strftime("%Y%m%d")
report_filename = f"orders_report_{today_str}.csv"
orders_df.to_csv(report_filename, index=False, encoding="utf-8")

# --- 統計資訊 ---
total_net = orders_df["net_amount"].sum()
total_orders = len(orders_df)
by_account = orders_df.groupby("assigned_to")["net_amount"].sum().to_dict()
by_region = orders_df.groupby("region")["net_amount"].sum().to_dict()
max_order = orders_df["net_amount"].max()
min_order = orders_df["net_amount"].min()

# --- Telegram 通知 ---
message = f"""
📊 今日到帳總額：{total_net} 元
訂單數量：{total_orders} 筆
分帳統計：{by_account}
各地區收益：{by_region}
最高單：{max_order} 元, 最低單：{min_order} 元
報表已生成：{report_filename}
"""

try:
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    print("✅ Telegram notification sent successfully.")
except Exception as e:
    print(f"Could not send Telegram notification. Please check your TOKEN and CHAT_ID. Error: {e}")


print(f"✅ 已完成今日收益計算，共 {total_orders} 筆訂單，總額 {total_net} 元")
print(f"✅ Report saved to {report_filename}")

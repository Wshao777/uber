import pandas as pd
import telegram
from datetime import datetime
import random
import json
import os
import argparse

def main(args):
    """
    Generates a set of mock orders and assigns them to 'Goddesses' based
    on their level, with higher-level goddesses having a higher chance of
    being assigned a task. It then generates a report and sends a Telegram
    notification.
    Includes a --dry-run mode to prevent sending actual notifications.
    """
    # --- Configuration ---
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "你的TelegramBotToken")
    TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "你的ChatID")
    CURRENCY_RATE = 1
    JSON_FILE = 'goddess_truecodes.json'

    # --- Load Goddess Data ---
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            goddesses = json.load(f)['goddesses']

        goddess_g_ids = [g['g_id'] for g in goddesses]
        goddess_levels = [g['level'] for g in goddesses]
        print(f"✅ Successfully loaded {len(goddesses)} goddesses from '{JSON_FILE}'.")
    except FileNotFoundError:
        print(f"🔥 Error: Core data file '{JSON_FILE}' not found. Cannot assign tasks.")
        return
    except (KeyError, json.JSONDecodeError) as e:
        print(f"🔥 Error: Could not parse '{JSON_FILE}'. Invalid format. Details: {e}")
        return

    # --- Generate Mock Order Data ---
    regions = ["臺北", "臺中", "逢甲", "高雄", "台南"]
    num_per_region = 1000
    orders = []

    print(f"⚙️  Generating {len(regions) * num_per_region} mock orders...")
    for region in regions:
        for i in range(1, num_per_region + 1):
            total = random.randint(100, 1000)
            fee = int(total * 0.1)
            assigned_goddess_gid = random.choices(goddess_g_ids, weights=goddess_levels, k=1)[0]
            orders.append({
                "order_id": f"{region[:2]}-{i:04d}",
                "region": region,
                "status": random.choice(["COMPLETED", "PENDING"]),
                "total_amount": total,
                "service_fee": fee,
                "assigned_to": assigned_goddess_gid
            })
    orders_df = pd.DataFrame(orders)
    print("✅ Mock order generation complete.")

    # --- Calculate Net Income & Generate Report ---
    orders_df["net_amount"] = (orders_df["total_amount"] - orders_df["service_fee"]) * CURRENCY_RATE
    today_str = datetime.now().strftime("%Y%m%d")
    report_filename = f"orders_report_{today_str}.csv"
    orders_df.to_csv(report_filename, index=False, encoding='utf-8-sig')
    print(f"✅ Daily report saved to '{report_filename}'.")

    # --- Calculate Statistics ---
    total_net = orders_df["net_amount"].sum()
    total_orders = len(orders_df)
    by_account = orders_df.groupby("assigned_to")["net_amount"].sum().to_dict()
    by_region = orders_df.groupby("region")["net_amount"].sum().to_dict()
    max_order = orders_df["net_amount"].max()
    min_order = orders_df["net_amount"].min()

    # --- Prepare Telegram Notification ---
    message = f"""
📊 **Daily Income Report**
---
**Total Net Income:** {total_net:,.2f}
**Total Orders:** {total_orders:,}
**Income by Goddess:**
"""
    for gid, amount in by_account.items():
        message += f"- {gid}: {amount:,.2f}\n"
    message += f"\n**Income by Region:**\n"
    for region, amount in by_region.items():
        message += f"- {region}: {amount:,.2f}\n"
    message += f"""
---
**Highest Order:** {max_order:,.2f}
**Lowest Order:** {min_order:,.2f}
---
*Report generated: {report_filename}*
"""

    # --- Send Notification or Print for Dry Run ---
    if args.dry_run:
        print("\n--- DRY RUN MODE ---")
        print("Telegram notification would be:")
        print(message)
        print("--- END DRY RUN ---")
    elif TELEGRAM_TOKEN != "你的TelegramBotToken" and TELEGRAM_CHAT_ID != "你的ChatID":
        try:
            bot = telegram.Bot(token=TELEGRAM_TOKEN)
            bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message, parse_mode='Markdown')
            print("✅ Telegram notification sent successfully.")
        except Exception as e:
            print(f"🔥 Could not send Telegram notification. Please check your TOKEN and CHAT_ID. Error: {e}")
    else:
        print("⚠️ Telegram notification skipped. Please set TELEGRAM_TOKEN and TELEGRAM_CHAT_ID.")

    print(f"\n✅ All tasks complete. Total orders: {total_orders}, Total net income: {total_net:,.2f}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Generate mock order data and send a report.")
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Run the script without sending a Telegram notification. Prints the message to the console instead."
    )
    args = parser.parse_args()
    main(args)

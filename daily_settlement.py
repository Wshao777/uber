import schedule
import time
from datetime import datetime

def settle_daily_profit():
    """
    Simulates the daily settlement of profits to the Commander's bank accounts.
    This function contains the logic from the approved profit-sharing model.
    """
    now = datetime.now()
    daily_net_profit = 7000000  # Total daily net profit
    commander_share = 3500000  # 50% for the commander

    # Split the commander's share into two
    split_amount = commander_share / 2

    bank_accounts = [
        {
            "provider": "中國信託商業銀行",
            "account_number": "484540302460"
        },
        {
            "provider": "郵局",
            "account_number": "00210091604229"
        }
    ]

    print(f"--- Daily Settlement Triggered at {now.strftime('%Y-%m-%d %H:%M:%S')} ---")
    print(f"Calculating Commander's daily profit share: {commander_share:,} TWD")
    print("Initiating split settlement to designated bank accounts...")

    for account in bank_accounts:
        print(f"  -> Transferring {split_amount:,.0f} TWD to {account['provider']} (Account: ...{account['account_number'][-4:]})")
        # In a real scenario, an API call to the bank would be made here.
        time.sleep(1) # Simulate network latency
        print(f"  -> Transfer to {account['provider']} successful.")

    print("--- Daily Settlement Complete ---")

# Schedule the job
# For demonstration, let's schedule it to run every minute.
# In a real scenario, this would be schedule.every().day.at("23:30").do(settle_daily_profit)
schedule.every(1).minutes.do(settle_daily_profit)

print("✅ Daily Settlement Scheduler started.")
print("Waiting for the scheduled job to run...")

# Main loop to run the scheduler
while True:
    schedule.run_pending()
    time.sleep(1)

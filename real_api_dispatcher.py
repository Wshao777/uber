import requests
import os
import random
import time
import json

# --- Placeholder Functions for Integration ---
def update_revenue_sheet(platform, order, result, ai_name):
    """Placeholder function to update Google Sheets/M365 Excel."""
    print(f"  -> [Placeholder] Updating revenue sheet for {platform} order {order['id']} assigned to {ai_name}.")
    pass

def send_telegram_notification(platform, order, result, ai_name):
    """Placeholder function to send a Telegram notification."""
    status = "Success" if result else "Failed"
    print(f"  -> [Placeholder] Sending Telegram notification: {platform} order {order['id']} for {ai_name} - {status}")
    pass

# --- API Dispatch Functions ---
def dispatch_uber(order):
    """Dispatches an order using the Uber API."""
    UBER_ACCESS_TOKEN = os.getenv("UBER_ACCESS_TOKEN")
    if not UBER_ACCESS_TOKEN:
        print("❌ Uber Access Token not found in environment variables.")
        return None

    url = "https://api.uber.com/v1.2/requests"
    headers = {
        "Authorization": f"Bearer {UBER_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "start_latitude": order["pickup_lat"],
        "start_longitude": order["pickup_lng"],
        "end_latitude": order["dropoff_lat"],
        "end_longitude": order["dropoff_lng"],
        "product_id": order.get("product_id")
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        print(f"✅ Uber order {order['id']} dispatched successfully.")
        return resp.json()
    except requests.RequestException as e:
        print(f"❌ Uber order {order['id']} dispatch failed: {e}")
        return None

def dispatch_foodpanda(order):
    """Dispatches an order using the Foodpanda Partner API."""
    FOODPANDA_ACCESS_TOKEN = os.getenv("FOODPANDA_ACCESS_TOKEN")
    FOODPANDA_PARTNER_ID = os.getenv("FOODPANDA_PARTNER_ID")

    if not FOODPANDA_ACCESS_TOKEN or not FOODPANDA_PARTNER_ID:
        print("❌ Foodpanda credentials not found in environment variables.")
        return None

    url = f"https://partner-api.foodpanda.com/v2/orders?partner_id={FOODPANDA_PARTNER_ID}"
    headers = {
        "Authorization": f"Bearer {FOODPANDA_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "order_id": order["id"],
        "items": [{"name": order["item"], "quantity": 1, "price": order["amount"]}],
        "pickup_address": order["pickup"],
        "dropoff_address": order["dropoff"]
    }

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=10)
        resp.raise_for_status()
        print(f"✅ Foodpanda order {order['id']} dispatched successfully.")
        return resp.json()
    except requests.RequestException as e:
        print(f"❌ Foodpanda order {order['id']} dispatch failed: {e}")
        return None

def dispatch_order(order, platform, ai_name):
    """Routes the dispatch request to the correct platform API."""
    print(f"\n📦 Attempting to dispatch order {order['id']} to {platform} for {ai_name}...")

    result = None
    if platform.lower() == "uber":
        result = dispatch_uber(order)
    elif platform.lower() == "foodpanda":
        result = dispatch_foodpanda(order)
    else:
        print(f"❌ Unknown platform: {platform}")

    update_revenue_sheet(platform, order, result, ai_name)
    send_telegram_notification(platform, order, result, ai_name)

    return result

# --- Main Execution ---
def generate_order(order_id):
    """Generates a random sample order."""
    amount = random.randint(50, 500)
    return {
        "id": f"ORDER-{order_id}",
        "item": "Test Item",
        "amount": amount,
        "pickup": "Some Pickup Address, Taichung",
        "dropoff": "Some Dropoff Address, Taichung",
        "pickup_lat": 24.1477,
        "pickup_lng": 120.6736,
        "dropoff_lat": 24.1558,
        "dropoff_lng": 120.6822,
        "product_id": os.getenv("UBER_PRODUCT_ID")
    }

def main():
    """Main function to run the dispatch simulation."""
    print("⚡️ Starting Real API Dispatch Simulation...")

    # --- Load Goddess Data for AI Assistant Logic ---
    JSON_FILE = 'goddess_truecodes.json'
    try:
        with open(JSON_FILE, 'r', encoding='utf-8') as f:
            goddesses = json.load(f)['goddesses']

        goddess_g_ids = [g['g_id'] for g in goddesses]
        goddess_levels = [g['level'] for g in goddesses]
        print(f"✅ Successfully loaded {len(goddesses)} goddesses for dispatch assignment.")
    except (FileNotFoundError, KeyError, json.JSONDecodeError) as e:
        print(f"🔥 Error loading goddess data from '{JSON_FILE}': {e}. Exiting.")
        return

    try:
        order_target = int(input("Enter the target number of orders to dispatch: "))
    except ValueError:
        print("Invalid number. Exiting.")
        return

    order_id_counter = 1000
    completed_orders = 0
    platforms = ["Uber", "Foodpanda"]

    while completed_orders < order_target:
        order = generate_order(order_id_counter)
        selected_platform = random.choice(platforms)

        # Select a Goddess based on weighted probability of their level
        selected_ai = random.choices(goddess_g_ids, weights=goddess_levels, k=1)[0]

        result = dispatch_order(order, selected_platform, selected_ai)

        if result:
            completed_orders += 1
            print(f"✅ Dispatch successful. {completed_orders}/{order_target} orders completed.")
        else:
            print(f"❌ Dispatch failed. Will retry with a new order.")

        order_id_counter += 1

        sleep_time = random.uniform(1, 5)
        print(f"--- Waiting for {sleep_time:.2f} seconds before next dispatch ---")
        time.sleep(sleep_time)

    print("\n🎯 All target orders have been processed. Dispatch simulation finished!")

if __name__ == "__main__":
    main()
# -*- coding: utf-8 -*-
"""
外送三距離派單 + 時薪計算骨架 (含即時模擬功能)
Delivery Dispatch for 3 Distances + Hourly Wage Calculation Skeleton (with Live Simulation)
"""
import random
import time
import os

# === Settings ===
DISTANCES = {
    "近距離": {"price_range": (40, 46), "drop_rate": 0.10, "efficiency_min_per_order": (4, 6)},
    "中距離": {"price_range": (50, 80), "drop_rate": 0.15, "efficiency_min_per_order": (7, 15)},
    "遠距離": {"price_range": (122, 141), "drop_rate": 0.20, "efficiency_min_per_order": (15, 30)}
}
ALLOCATION_RATIO = {"近距離": 0.47, "中距離": 0.33, "遠距離": 0.20}

def quick_estimate(total_orders):
    """Calculates a quick, high-level estimate of earnings."""
    print("\n--- Quick Estimate Mode ---")

    allocated_orders = {k: int(total_orders * v) for k, v in ALLOCATION_RATIO.items()}

    for k, v in DISTANCES.items():
        v["avg_price"] = sum(v["price_range"]) / 2

    total_hours = 8
    total_earnings = sum(allocated_orders[k] * DISTANCES[k]["avg_price"] * (1 - DISTANCES[k]["drop_rate"])
                         for k in DISTANCES)
    average_hourly = total_earnings / total_hours

    print("\n=== 今日派單分配 (Today's Dispatch Allocation) ===")
    for k, v in allocated_orders.items():
        print(f"{k}: {v} 單, 平均單價 (Avg Price) {DISTANCES[k]['avg_price']} 元, 棄單率 (Drop Rate) {DISTANCES[k]['drop_rate']*100}%")

    print(f"\n今日總收益 (Total Earnings): {total_earnings:.2f} 元")
    print(f"平均時薪 (Avg Hourly Wage): {average_hourly:.2f} 元/小時")

def live_simulation(total_orders):
    """Simulates a workday order by order with live updates."""
    print("\n--- Live Simulation Mode ---")

    # Create a pool of all orders for the day
    order_pool = []
    for dist, ratio in ALLOCATION_RATIO.items():
        num_orders = int(total_orders * ratio)
        order_pool.extend([dist] * num_orders)
    random.shuffle(order_pool)

    total_earnings = 0
    total_minutes_worked = 0
    orders_completed = 0
    orders_dropped = 0

    for i, order_type in enumerate(order_pool):
        # Simulate if the order is dropped
        if random.random() < DISTANCES[order_type]["drop_rate"]:
            orders_dropped += 1
            print(f"Order #{i+1} ({order_type}): ⚠️ Dropped!")
            continue

        # Process the order
        orders_completed += 1
        price = random.randint(*DISTANCES[order_type]["price_range"])
        time_taken = random.randint(*DISTANCES[order_type]["efficiency_min_per_order"])

        total_earnings += price
        total_minutes_worked += time_taken

        # Calculate current stats
        current_hours_worked = total_minutes_worked / 60
        current_hourly_wage = total_earnings / current_hours_worked if current_hours_worked > 0 else 0

        # Live update
        print(f"Order #{i+1} ({order_type}): ✅ Completed! | Price: {price}元 | Time: {time_taken}min")
        print(f"  -> Stats: {orders_completed} orders done | Total Mins: {total_minutes_worked} | Wage: {current_hourly_wage:.2f} 元/hr")

        time.sleep(0.1) # Pause for dramatic effect

    print("\n=== Simulation Complete ===")
    final_hours = total_minutes_worked / 60
    print(f"總計工時 (Total Hours): {final_hours:.2f} 小時")
    print(f"總計收益 (Total Earnings): {total_earnings:.2f} 元")
    print(f"完成單數 (Orders Completed): {orders_completed}")
    print(f"棄單數 (Orders Dropped): {orders_dropped}")
    final_hourly = total_earnings / final_hours if final_hours > 0 else 0
    print(f"最終時薪 (Final Hourly Wage): {final_hourly:.2f} 元/小時")

def main():
    """Main function to run the calculator."""
    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=== 外送員時薪計算機 (Delivery Driver Wage Calculator) ===")
        print("1. 快速預估 (Quick Estimate)")
        print("2. 即時模擬 (Live Simulation)")
        print("3. 離開 (Exit)")

        choice = input("請選擇模式 (Choose a mode): ")

        if choice == '3':
            break

        if choice in ['1', '2']:
            try:
                total_orders = int(input("輸入今日總訂單量 (Enter total orders for today): "))
                if choice == '1':
                    quick_estimate(total_orders)
                elif choice == '2':
                    live_simulation(total_orders)
            except ValueError:
                print("無效輸入，請輸入數字 (Invalid input, please enter a number).")
            input("\n按 Enter 鍵繼續 (Press Enter to continue)...")
        else:
            print("無效選擇 (Invalid choice).")
            time.sleep(1)

if __name__ == "__main__":
    main()

import pandas as pd
from datetime import datetime, timedelta

# --- Configuration & Market Data ---
# Based on user's prompt
MARKET_DATA = {
    "fengjia": {
        "name": "逢甲夜市 (Fengjia Night Market)",
        "annual_revenue_twd": 7.14e9,
        "cagr": 0.234  # 23.4%
    },
    "danshui_agei": {
        "name": "淡水阿給 (Danshui A-gei)",
        "annual_revenue_twd": 1e8,
        "cagr": 0.08  # 8%
    }
}

SIMULATION_PARAMS = {
    "duration_days": 90,
    "user_share": 0.90,  # 90%
    "daily_settlement_target_twd": 250000,
    "daily_distribution": {
        "fengjia": 0.4,  # 100k / 250k
        "japan": 0.2,    # 50k / 250k
        "china": 0.2,    # 50k / 250k
        "taiwan": 0.2    # 50k / 250k
    }
}

def project_future_revenue(market, years=1):
    """Projects future annual revenue based on CAGR."""
    return market["annual_revenue_twd"] * ((1 + market["cagr"]) ** years)

def run_simulation():
    """Runs the 90-day revenue simulation."""
    print("--- Running 90-Day Revenue Simulation for 'Fengjia Danshui A-gei Alliance' ---")

    total_projected_revenue = 0
    all_daily_data = []

    start_date = datetime.now()

    for day in range(SIMULATION_PARAMS["duration_days"]):
        current_date = start_date + timedelta(days=day)
        daily_revenue = SIMULATION_PARAMS["daily_settlement_target_twd"]
        total_projected_revenue += daily_revenue

        daily_data = {
            "date": current_date.strftime("%Y-%m-%d"),
            "daily_total_revenue_twd": daily_revenue,
            "fengjia_revenue": daily_revenue * SIMULATION_PARAMS["daily_distribution"]["fengjia"],
            "japan_revenue": daily_revenue * SIMULATION_PARAMS["daily_distribution"]["japan"],
            "china_revenue": daily_revenue * SIMULATION_PARAMS["daily_distribution"]["china"],
            "taiwan_revenue": daily_revenue * SIMULATION_PARAMS["daily_distribution"]["taiwan"],
        }
        all_daily_data.append(daily_data)

    user_share = total_projected_revenue * SIMULATION_PARAMS["user_share"]
    company_share = total_projected_revenue * (1 - SIMULATION_PARAMS["user_share"])

    # --- Generate Report ---
    print("\n--- Simulation Summary ---")
    print(f"Simulation Duration: {SIMULATION_PARAMS['duration_days']} days")
    print(f"Total Projected Revenue: {total_projected_revenue:,.2f} TWD")
    print(f"  -> Commander's Share (90%): {user_share:,.2f} TWD")
    print(f"  -> System Share (10%): {company_share:,.2f} TWD")

    # Compare with user's target
    user_target = 9.18e8 # 918 million TWD
    print(f"\nComparison with 3-Month Target:")
    print(f"  -> Target: {user_target:,.2f} TWD")
    print(f"  -> Simulation Result: {user_share:,.2f} TWD")
    if user_share < user_target:
        print(f"  -> NOTE: The daily target of {SIMULATION_PARAMS['daily_settlement_target_twd']:,} TWD is not sufficient to meet the 3-month goal of {user_target/1e8:.2f}億 TWD.")
        print(f"     To reach the goal, the daily target needs to be approximately {user_target / SIMULATION_PARAMS['duration_days'] / SIMULATION_PARAMS['user_share']:,.2f} TWD.")

    # --- Save to CSV ---
    df = pd.DataFrame(all_daily_data)
    report_filename = f"revenue_simulation_report_{start_date.strftime('%Y%m%d')}.csv"
    df.to_csv(report_filename, index=False, encoding='utf-8-sig')
    print(f"\n✅ Detailed simulation report saved to '{report_filename}'")


if __name__ == "__main__":
    run_simulation()
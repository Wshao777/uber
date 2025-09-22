import json
import hashlib
import hmac
import uuid
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

print(f"--- 偵錯資訊 ---")
print(f"腳本當前工作目錄: {os.getcwd()}")
print(f"--- 偵錯資訊結束 ---")

# 雙平台抽成數據（基於 v6.7）
data = {
    "platform": "UberEats_Foodpanda",
    "date": "2025-09-21",
    "settlement_time": "22:00",
    "accounts": [
        {
            "provider": "中國信託商業銀行",
            "institution_code": "822",
            "account_number": "484540302460",
            "settlement_amount": 3500000.0
        },
        {
            "provider": "郵局",
            "institution_code": "700",
            "account_number": "00210091604229",
            "settlement_amount": 3500000.0
        }
    ],
    "orders": [
        {
            "order_id": 1,
            "platform": "Foodpanda",
            "driver_id": "wshao777",
            "type": "near",
            "distance": 1.2,
            "price": 40.0,
            "commission": 10.0,
            "timestamp": "2025-09-21T08:00:00",
            "hotspot_start": {"name": "逢甲夜市", "lat": 24.1786, "lng": 120.6460},
            "hotspot_end": {"name": "逢甲夜市", "lat": 24.1786, "lng": 120.6460}
        },
        {
            "order_id": 2,
            "platform": "UberEats",
            "driver_id": "wshao777",
            "type": "medium",
            "distance": 3.5,
            "price": 50.0,
            "commission": 10.0,
            "timestamp": "2025-09-21T08:15:00",
            "hotspot_start": {"name": "信義區", "lat": 25.0330, "lng": 121.5654},
            "hotspot_end": {"name": "松菸", "lat": 25.0436, "lng": 121.5608}
        }
    ],
    "regions": [
        {
            "name": "台北",
            "daily_orders": 400000,
            "total_commission": 4000000.0,
            "net_profit": 2800000.0,
            "hotspots": [
                {"name": "信義區", "lat": 25.0330, "lng": 121.5654, "order_rate": 20},
                {"name": "松菸", "lat": 25.0436, "lng": 121.5608, "order_rate": 15}
            ]
        },
        {
            "name": "台中",
            "daily_orders": 150000,
            "total_commission": 1500000.0,
            "net_profit": 1050000.0,
            "hotspots": [
                {"name": "逢甲夜市", "lat": 24.1786, "lng": 120.6460, "order_rate": 15},
                {"name": "西區勤美", "lat": 24.1500, "lng": 120.6630, "order_rate": 6}
            ]
        },
        {
            "name": "高雄",
            "daily_orders": 200000,
            "total_commission": 2000000.0,
            "net_profit": 1400000.0,
            "hotspots": [
                {"name": "三民區", "lat": 22.6394, "lng": 120.3023, "order_rate": 10},
                {"name": "六合夜市", "lat": 22.6314, "lng": 120.3018, "order_rate": 8}
            ]
        },
        {
            "name": "其他",
            "daily_orders": 250000,
            "total_commission": 2500000.0,
            "net_profit": 1750000.0,
            "hotspots": []
        }
    ],
    "total": {
        "daily_orders": 1000000,
        "total_commission": 10000000.0,
        "net_profit": 7000000.0
    },
    "marketing": {
        "tiktok": {
            "tiktok_reach": 1250000,
            "ad_clicks": 98765,
            "conversion_rate": 0.12,
            "drivers_recruited": 7500,
            "regions": [
                {"name": "台灣", "budget": 6000.0, "reach": 750000, "ad_clicks": 60000, "drivers_recruited": 4500},
                {"name": "CA_NY", "budget": 4000.0, "reach": 500000, "ad_clicks": 38765, "drivers_recruited": 3000}
            ]
        }
    }
}

# HMAC-SHA256 簽章
def generate_hmac_sha256(data, key="G8-MASTER"):
    raw = json.dumps({k: v for k, v in data.items() if k != "verification"}, sort_keys=True).encode()
    return hmac.new(key.encode(), raw, hashlib.sha256).hexdigest()

# 生成驗證碼與簽章
verification_code = str(uuid.uuid4())
hmac_checksum = generate_hmac_sha256(data)
data["verification"] = {
    "checksum": hmac_checksum,
    "verification_code": verification_code,
    "algorithm": "HMAC-SHA256",
    "legal_evidence": True
}

# 驗證 HMAC
def verify_hmac_sha256(data, checksum, key="G8-MASTER"):
    raw = json.dumps({k: v for k, v in data.items() if k != "verification"}, sort_keys=True).encode()
    return hmac.new(key.encode(), raw, hashlib.sha256).hexdigest() == checksum

# 緊湊編碼
compact_json = json.dumps(data, ensure_ascii=False, separators=(',', ':'))
print("---COMPACT JSON START---")
print(compact_json)
print("---COMPACT JSON END---")
print("✅ 緊湊 JSON（v7.0，含 HMAC 簽章）已生成至標準輸出。")

# 美化輸出
pretty_json = json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True)
print("---PRETTY JSON START---")
print(pretty_json)
print("---PRETTY JSON END---")
print("✅ 美化 JSON（v7.0，含 HMAC 簽章）已生成至標準輸出。")

# # 導入 Google Sheets
# print("ℹ️ 偵測到無 Google Sheets 憑證，將跳過上傳步驟。")
# # scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
# # creds = ServiceAccountCredentials.from_json_keyfile_name('your-credentials.json', scope)
# # client = gspread.authorize(creds)
# # sheet = client.open("DoublePlatform_Commission_2025").add_worksheet("Commission_v7", rows=200, cols=20)

# # # 將 JSON 轉為表格
# # rows = [["Order_ID", "Platform", "Driver_ID", "Type", "Distance", "Price", "Commission", "Timestamp", "Start", "End"]]
# # for order in data["orders"]:
# #     rows.append([
# #         order["order_id"],
# #         order["platform"],
# #         order["driver_id"],
# #         order["type"],
# #         order["distance"],
# #         order["price"],
# #         order["commission"],
# #         order["timestamp"],
# #         order["hotspot_start"]["name"],
# #         order["hotspot_end"]["name"]
# #     ])
# # rows.append(["", "", "", "", "", "", "", "", "", ""])
# # rows.append(["Region", "Daily_Orders", "Total_Commission", "Net_Profit"])
# # for region in data["regions"]:
# #     rows.append([
# #         region["name"],
# #         region["daily_orders"],
# #         region["total_commission"],
# #         region["net_profit"]
# #     ])
# # rows.append(["總計", data["total"]["daily_orders"], data["total"]["total_commission"], data["total"]["net_profit"]])
# # rows.append(["", "", "", "", "", "", "", "", "", ""])
# # rows.append(["TikTok", "Reach", "Ad_Clicks", "Conversion_Rate", "Drivers_Recruited"])
# # rows.append([
# #     "TikTok",
# #     data["marketing"]["tiktok"]["tiktok_reach"],
# #     data["marketing"]["tiktok"]["ad_clicks"],
# #     data["marketing"]["tiktok"]["conversion_rate"],
# #     data["marketing"]["tiktok"]["drivers_recruited"]
# # ])
# # rows.append(["", "", "", "", "", "", "", "", "", ""])
# # rows.append(["Region", "Budget", "Reach", "Ad_Clicks", "Drivers_Recruited"])
# # for region in data["marketing"]["tiktok"]["regions"]:
# #     rows.append([
# #         region["name"],
# #         region["budget"],
# #         region["reach"],
# #         region["ad_clicks"],
# #         region["drivers_recruited"]
# #     ])
# # rows.append(["", "", "", "", "", "", "", "", "", ""])
# # rows.append(["Verification", "Checksum", data["verification"]["checksum"], "Algorithm", data["verification"]["algorithm"], "Legal_Evidence", data["verification"]["legal_evidence"]])

# # sheet.clear()
# # for row in rows:
# #     sheet.append_row(row)
# # print("✅ JSON 數據（v7.0，含 TikTok 與 HMAC）已上傳至 Google Sheets：Commission_v7")

# 驗證 HMAC
if verify_hmac_sha256(data, data["verification"]["checksum"]):
    print("✅ HMAC-SHA256 驗證通過：數據未被篡改")
else:
    print("⚠️ HMAC-SHA256 驗證失敗：數據可能被篡改")

# 模擬分割結算
def simulate_settlement(accounts_list):
    print("--- 模擬結算開始 ---")
    for account in accounts_list:
        print(f"✅ 轉帳成功：{account['settlement_amount']} 元至 {account['provider']} (帳號: ...{account['account_number'][-4:]})")
    print("--- 模擬結算結束 ---")
    return True

simulate_settlement(data["accounts"])

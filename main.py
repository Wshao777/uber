import pandas as pd
import requests
import os
from datetime import datetime
from geopy.distance import geodesic  # pip install geopy

UBER_API_KEY = os.getenv('UBER_API_KEY')
LINE_TOKEN = os.getenv('LINE_TOKEN')
LINE_GROUP_ID = os.getenv('LINE_GROUP_ID')  # @004kfkmv群

def fetch_orders(region='台中'):
    url = f'https://api.uber.com/v1/estimates?region={region}'
    headers = {'Authorization': f'Bearer {UBER_API_KEY}'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # If the response contains an HTTP error status code, raise an exception.
        orders = response.json().get('estimates', []) # Safely get estimates, default to empty list.
    except requests.exceptions.RequestException as e:
        print(f"API request failed: {e}")
        orders = [] # In case of network error, return empty list.
    except ValueError: # Catches JSON decoding errors
        print("Failed to decode JSON response from API.")
        orders = []
    return [o for o in pd.DataFrame(orders).to_dict('records') if check_5km(o['coords'], ('24.16', '120.69'))]

def check_5km(start, end):
    return geodesic(start, end).km <= 5

def calculate_metrics(orders):
    orders_count = len(orders)
    revenue = sum(o['fee'] for o in orders) * 0.1
    return {'日期':datetime.now().strftime('%Y-%m-%d'), '單量':orders_count, '收益':revenue, '累計':revenue*30}

def send_line_report(metrics):
    url = 'https://api.line.me/v2/bot/message/push'
    payload = {'to':LINE_GROUP_ID, 'messages':[{'type':'text', 'text':f"ThunderEmpire Metrics: 單量{metrics['單量']}, 收益{metrics['收益']}元, 累計{metrics['累計']}元！"}]}
    headers = {'Authorization':f'Bearer {LINE_TOKEN}', 'Content-Type':'application/json'}
    requests.post(url, json=payload, timeout=5)

if __name__ == '__main__':
    orders = fetch_orders()
    metrics = calculate_metrics(orders)
    print(metrics)
    send_line_report(metrics)
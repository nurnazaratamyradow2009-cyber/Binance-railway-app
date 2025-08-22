import os
import requests
import time
import hmac
import hashlib

# Set your actual API keys here for testing (remove before deploying)
API_KEY = "0o1KXgoF64koKnVXjR3kL6VJW74a2geYU0o09T4N7wGIdlUWJ8TSG2VONbXBImu3"  # Replace with your actual key
API_SECRET = "XW1Sh3SxFK6nLf70mdmVRUODGIfPSVwxFC766JwXei9wwyJLxXayMAff94Q9KzOW"  # Replace with your actual secret
BASE_URL = "https://api.binance.com"

def get_server_time():
    try:
        response = requests.get(f"{BASE_URL}/api/v3/time")
        response.raise_for_status()
        return response.json()["serverTime"]
    except requests.exceptions.RequestException as e:
        print(f"Error getting server time: {e}")
        return None
    except KeyError:
        print("Error: 'serverTime' not found in response")
        return None

def sign(params):
    query_string = "&".join([f"{k}={v}" for k, v in params.items()])
    return hmac.new(API_SECRET.encode(), query_string.encode(), hashlib.sha256).hexdigest()

def get_account_info():
    timestamp = get_server_time()
    if timestamp is None:
        return {"error": "Could not get server time"}
   
    params = {"timestamp": timestamp, "recvWindow": 10000}
    params["signature"] = sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}
   
    try:
        response = requests.get(f"{BASE_URL}/api/v3/account", params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting account info: {e}")
        return {"error": str(e)}

def get_deposit_address(coin, network=None):
    timestamp = get_server_time()
    if timestamp is None:
        return {"error": "Could not get server time"}
   
    params = {"coin": coin, "timestamp": timestamp, "recvWindow": 10000}
    if network:
        params["network"] = network
    params["signature"] = sign(params)
    headers = {"X-MBX-APIKEY": API_KEY}
   
    try:
        response = requests.get(f"{BASE_URL}/sapi/v1/capital/deposit/address", params=params, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting deposit address for {coin}: {e}")
        return {"error": str(e)}

def get_prices():
    try:
        response = requests.get(f"{BASE_URL}/api/v3/ticker/price")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error getting prices: {e}")
        return []

# Test the connection step by step
print("Testing connection to Binance API...")

# 1. Test server time
print("1. Testing server time...")
server_time = get_server_time()
if server_time:
    print(f"✓ Server time: {server_time}")
else:
    print("✗ Failed to get server time")
    exit()

# 2. Test signature generation
print("2. Testing signature generation...")
test_params = {"timestamp": server_time, "recvWindow": 10000}
signature = sign(test_params)
print(f"✓ Signature: {signature[:15]}...")

# 3. Test account info
print("3. Testing account info...")
account = get_account_info()
if "error" in account:
    print(f"✗ Error: {account['error']}")
    print("Please check your API keys and permissions")
    exit()
else:
    print("✓ Account info retrieved successfully")
    print(f"Account type: {account.get('accountType', 'N/A')}")
    print(f"Can trade: {account.get('canTrade', 'N/A')}")
    print(f"Can withdraw: {account.get('canWithdraw', 'N/A')}")
    print(f"Can deposit: {account.get('canDeposit', 'N/A')}")

# 4. Display ALL balances (even zero balances)
print("\n=== ALL BALANCES (including zeros) ===")
all_balances = account.get('balances', [])
print(f"Total assets tracked: {len(all_balances)}")

# Show first 10 assets as sample
for i, b in enumerate(all_balances[:10]):
    asset = b['asset']
    free = float(b['free'])
    locked = float(b['locked'])
    total = free + locked
    print(f"{asset}: Free={free}, Locked={locked}, Total={total}")

if len(all_balances) > 10:
    print(f"... and {len(all_balances) - 10} more assets")

# 5. Test deposit addresses for a few common assets
print("\n=== DEPOSIT ADDRESS TEST (for common assets) ===")
test_assets = ['BTC', 'ETH', 'USDT', 'BNB']  # Test with common assets

for asset in test_assets:
    try:
        addr = get_deposit_address(asset)
        if "error" in addr:
            print(f"{asset}: Error - {addr['error']}")
        elif "code" in addr:
            print(f"{asset}: API Error - {addr.get('msg', 'Unknown error')} (code: {addr.get('code')})")
        else:
            print(f"{asset}: {addr.get('address', 'No address')}")
    except Exception as e:
        print(f"{asset}: Exception {e}")

# 6. Test prices for common assets
print("\n=== PRICES FOR COMMON ASSETS ===")
prices = get_prices()
if prices:
    price_dict = {p['symbol']: p['price'] for p in prices}
   
    # Show prices for common trading pairs
    common_pairs = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'SOLUSDT']
    for pair in common_pairs:
        if pair in price_dict:
            print(f"{pair}: {price_dict[pair]}")
        else:
            print(f"{pair}: N/A")
else:
    print("Failed to get prices")

# 7. Verify API permissions
print("\n=== API PERMISSIONS CHECK ===")
print("Your API connection is working! But you might need to:")
print("1. Check if your Binance account has any assets")
print("2. Verify your API key has these permissions enabled:")
print("   - Enable Reading")
print("   - Enable Spot & Margin Trading (if needed)")
print("   - Allow access to deposit addresses")
print("3. If testing with a new account, you may need to deposit some crypto first")

print("\n✓ Test completed successfully! Your API connection is working")
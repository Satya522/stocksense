"""Quick script to check and fix API keys for StockSense."""
import requests
import json

s = requests.Session()

# Login with password
login = s.post("http://localhost:8080/api/method/login", data={"usr": "Administrator", "pwd": "admin"})
print(f"Login: {login.status_code}")

# Check current API key on Administrator
r = s.get("http://localhost:8080/api/resource/User/Administrator",
          params={"fields": json.dumps(["name", "api_key"])})
data = r.json().get("data", {})
print(f"Current API key on Administrator: {data.get('api_key', 'NONE')}")

# Try to generate new keys via bench command through API
# If the above key is empty, we'll use session-based auth instead
# First, let's just test session-based API access works
r2 = s.get("http://localhost:8080/api/resource/Item",
           params={"limit_page_length": 0, "fields": json.dumps(["name"])})
items = r2.json().get("data", [])
print(f"Items via session auth: {len(items)}")

# Test if old API key works
r3 = requests.get("http://localhost:8080/api/resource/Item",
                   headers={"Authorization": "token cde40747b0d9d8e:db7da3efad1b416"},
                   params={"limit_page_length": 0, "fields": json.dumps(["name"])})
print(f"Items via API key auth: {r3.status_code}")

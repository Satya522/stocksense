"""
StockSense — Connection Test Script
=====================================
Tests two connections to your ERPNext instance:
  1. REST API via requests (using API key/secret)
  2. Direct MariaDB database via SQLAlchemy + PyMySQL

Usage:
  cd python
  python src/test_connection.py

Prerequisites:
  - Copy .env.example to .env and fill in your credentials
  - Install dependencies: pip install -r requirements.txt
"""

import os
import sys
from pathlib import Path

# Load .env from the python/ directory (parent of src/)
from dotenv import load_dotenv

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


def test_erpnext_api():
    """
    Test 1: Connect to ERPNext REST API and fetch Item count.
    Uses the requests library with API key/secret authentication.
    """
    print("=" * 60)
    print("TEST 1: ERPNext REST API Connection")
    print("=" * 60)

    import requests

    url = os.getenv("ERPNEXT_URL", "").rstrip("/")
    api_key = os.getenv("ERPNEXT_API_KEY", "")
    api_secret = os.getenv("ERPNEXT_API_SECRET", "")

    if not url or api_key == "your_key_here" or not api_key:
        print("❌ ERPNEXT_URL / ERPNEXT_API_KEY not configured.")
        print("   → Edit your .env file with real credentials.")
        print("   → See README.md for how to generate API keys in ERPNext.")
        return False

    try:
        # Fetch list of Items (limit to 0 — we just want the total count)
        endpoint = f"{url}/api/resource/Item"
        headers = {
            "Authorization": f"token {api_key}:{api_secret}"
        }
        params = {
            "limit_page_length": 0,  # 0 = return all (just counting)
            "fields": '["name"]',
        }

        print(f"   Connecting to: {endpoint}")
        response = requests.get(endpoint, headers=headers, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        items = data.get("data", [])
        print(f"   ✅ SUCCESS — Found {len(items)} Items in ERPNext.")
        return True

    except requests.exceptions.ConnectionError:
        print(f"   ❌ Connection failed — cannot reach {url}")
        print("   → Is your ERPNext Docker container running?")
        print("   → Try: docker ps | findstr erpnext")
        return False
    except requests.exceptions.HTTPError as e:
        print(f"   ❌ HTTP Error: {e}")
        if e.response is not None and e.response.status_code == 403:
            print("   → Check your API key and secret in .env")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False


def test_database_connection():
    """
    Test 2: Connect directly to MariaDB and query tabItem.
    Uses SQLAlchemy with the PyMySQL driver.
    """
    print()
    print("=" * 60)
    print("TEST 2: MariaDB Direct Database Connection")
    print("=" * 60)

    from sqlalchemy import create_engine, text

    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_user = os.getenv("DB_USER", "")
    db_password = os.getenv("DB_PASSWORD", "")
    db_name = os.getenv("DB_NAME", "")

    if not db_user or db_password == "your_password" or not db_name or db_name == "your_erpnext_site_db":
        print("❌ Database credentials not configured.")
        print("   → Edit your .env file with real DB credentials.")
        print("   → Run SHOW DATABASES; in MariaDB to find your ERPNext DB name.")
        return False

    connection_string = (
        f"mysql+pymysql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )

    try:
        print(f"   Connecting to: {db_host}:{db_port}/{db_name}")
        engine = create_engine(connection_string, connect_args={"connect_timeout": 10})

        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) AS item_count FROM `tabItem`"))
            row = result.fetchone()
            count = row[0] if row else 0
            print(f"   ✅ SUCCESS — tabItem has {count} rows.")
            return True

    except Exception as e:
        error_msg = str(e)
        print(f"   ❌ Database connection failed: {e}")

        if "Access denied" in error_msg:
            print("   → Check DB_USER and DB_PASSWORD in .env")
        elif "Can't connect" in error_msg or "Connection refused" in error_msg:
            print("   → Is MariaDB running and port 3306 exposed?")
            print("   → Try: docker ps | findstr mariadb")
        elif "Unknown database" in error_msg:
            print("   → Check DB_NAME in .env")
            print("   → Run SHOW DATABASES; to find the correct name")
        else:
            print("   → Verify all DB_* values in your .env file")
        return False


def main():
    print()
    print("📦 StockSense — Connection Test")
    print("=" * 60)
    print()

    api_ok = test_erpnext_api()
    db_ok = test_database_connection()

    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"   ERPNext API:  {'✅ Connected' if api_ok else '❌ Failed'}")
    print(f"   MariaDB:      {'✅ Connected' if db_ok else '❌ Failed'}")
    print()

    if api_ok and db_ok:
        print("🎉 All connections working! You're ready to build dashboards.")
    elif not api_ok and not db_ok:
        print("⚠️  Both connections failed. Have you filled in your .env file?")
        print("   → cp .env.example .env   (then edit with real values)")
    else:
        print("⚠️  One connection failed — check the error messages above.")

    print()


if __name__ == "__main__":
    main()

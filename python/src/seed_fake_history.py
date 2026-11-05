import os
import pymysql
import random
from datetime import datetime, timedelta
from dotenv import load_dotenv
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

def seed_fake_history():
    conn = pymysql.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME")
    )
    
    with conn.cursor() as cursor:
        # Get top 20 items
        cursor.execute("SELECT item_code, warehouse, actual_qty FROM `tabBin` WHERE actual_qty > 0 LIMIT 20")
        items = cursor.fetchall()
        
        insert_sql = """
            INSERT INTO `tabStock Ledger Entry` 
            (name, item_code, warehouse, posting_date, posting_time, voucher_type, voucher_no, actual_qty, qty_after_transaction, stock_value, creation, modified, company)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NOW(), NOW(), 'StockSense')
        """
        
        count = 0
        for item in items:
            item_code, warehouse, base_qty = item[0], item[1], float(item[2])
            
            for d in range(30, 0, -1):
                if random.random() < 0.2: continue # skip some days
                
                date_str = (datetime.now() - timedelta(days=d)).strftime('%Y-%m-%d')
                outflow = -random.randint(1, 10)
                name = f"ML-SIM-{item_code}-{d}-{random.randint(1000,9999)}"
                
                try:
                    cursor.execute(insert_sql, (
                        name, item_code, warehouse, date_str, '10:00:00',
                        'Stock Entry', name, outflow, base_qty, 1000.0
                    ))
                    count += 1
                except Exception as e:
                    print(f"Error inserting for {item_code}: {e}")
                    
        conn.commit()
        print(f"Successfully inserted {count} historical ledger entries for ML training.")
    
    conn.close()

if __name__ == "__main__":
    seed_fake_history()

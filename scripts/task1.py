import pandas as pd
import sqlite3
import requests
import ipaddress

# API Key for ipwhois.io (Replace with your key)
API_KEY = "YOUR_API_KEY"

# File paths
ORDERS_CSV = r"C:\Users\jyothi\Downloads\task\orders_file.csv"
IPS_CSV =   r"C:\Users\jyothi\Downloads\task\ip_addresses.csv"
DB_FILE = "orders_db.sqlite"
EXPORT_CSV = "updated_orders.csv"

# Connect to SQLite
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

# Create Orders Table with correct columns based on the CSV structure
cursor.execute('''CREATE TABLE IF NOT EXISTS orders (
    order_number TEXT PRIMARY KEY,
    date TEXT,
    city TEXT,
    state TEXT,
    Zip TEXT,
    "$ sale" TEXT  -- Using "$ sale" as the column name in the database to match the CSV
)''')

# Create IP Lookup Table
cursor.execute('''CREATE TABLE IF NOT EXISTS ip_data (
    ip_address TEXT PRIMARY KEY,
    city TEXT,
    state TEXT,
    zip_code TEXT
)''')

conn.commit()

def load_orders_data(file_path):
    """Load orders CSV into the database, ignoring duplicates."""
    df = pd.read_csv(file_path, dtype=str)
    
    for _, row in df.iterrows():
        cursor.execute('''INSERT OR IGNORE INTO orders 
                          (order_number, date, city, state, Zip, "$ sale") 
                          VALUES (?, ?, ?, ?, ?, ?)''', 
                       (row["order_number"], row["date"], row.get("city", ""),
                        row.get("state", ""), row.get("Zip", ""), row.get("$ sale", "")))
    
    conn.commit()
    print("✅ Orders data loaded successfully!")

def load_ip_data(file_path):
    """Load IP addresses into the database, ignoring duplicates."""
    df = pd.read_csv(file_path, dtype=str)

    print(f"📝 Loaded {len(df)} IP addresses from the file")

    for _, row in df.iterrows():
        ip = row.get("ip_address", "")
        
        # Check for NaN or empty string and log it
        if pd.isna(ip) or not ip.strip():
            print(f"❌ Invalid IP found in the file: {ip}")
            continue
        
        ip = ip.strip()  # Ensure the IP is cleaned up before use
        print(f"✅ Valid IP found: {ip}")
        
        cursor.execute('''INSERT OR IGNORE INTO ip_data (ip_address) VALUES (?)''', (ip,))
    
    conn.commit()
    print("✅ IP data loaded successfully!")

def is_valid_ip(ip):
    """Validate IP address format."""
    if not isinstance(ip, str) or pd.isna(ip):  # Check if IP is a string and not NaN
        return None  # or return empty string to skip

    try:
        ip = ip.strip()  # Only strip if it's a string
        if ip == "":
            return None
        ipaddress.ip_address(ip)  # Validate IP
        return ip
    except ValueError:
        return None

def fetch_ip_data(ip):
    """Fetch location data from ipwhois.io API."""
    url = f"https://ipwhois.app/json/{ip}?apikey={API_KEY}"

    try:
        response = requests.get(url)
        response.raise_for_status()  # Will raise an HTTPError if the response code is not 200
        data = response.json()
        return data.get("city", ""), data.get("region", ""), data.get("postal", "")
    except requests.exceptions.RequestException as e:
        print(f"⚠ Error fetching data for IP: {ip}. Error: {e}")
        return "", "", ""
    except requests.exceptions.ConnectionError as e:
        print(f"⚠ Connection error while fetching data for IP: {ip}. Retrying...")
        time.sleep(5)  # Wait for 5 seconds before retrying
        return fetch_ip_data(ip)  # Retry the request

def update_ip_data():
    """Fetch and store location data for IPs in the database."""
    cursor.execute("SELECT ip_address FROM ip_data WHERE city IS NULL OR city = ''")
    ip_rows = cursor.fetchall()
    
    for row in ip_rows:
        ip = row[0]
        valid_ip = is_valid_ip(ip)
        
        if valid_ip:
            city, state, zip_code = fetch_ip_data(valid_ip)
            cursor.execute("UPDATE ip_data SET city=?, state=?, zip_code=? WHERE ip_address=?", 
                           (city, state, zip_code, valid_ip))
            conn.commit()
            print(f"✅ Updated {valid_ip}: {city}, {state}, {zip_code}")
        else:
            print(f"❌ Invalid IP format: {ip}")

def update_orders():
    """Update orders with location data from IPs."""
    cursor.execute('''SELECT o.order_number, i.city, i.state, i.zip_code, o.Zip
                      FROM orders o
                      JOIN ip_data i ON o.Zip = "" AND i.ip_address IS NOT NULL''')
    
    for order_number, city, state, zip_code, existing_zip in cursor.fetchall():
        if zip_code and not existing_zip:
            cursor.execute('''UPDATE orders SET city=?, state=?, Zip=? WHERE order_number=?''',
                           (city, state, zip_code, order_number))
    
    conn.commit()
    print("✅ Orders updated with IP location data!")

def export_orders():
    """Export updated orders to CSV."""
    df = pd.read_sql_query("SELECT order_number, city, state, Zip FROM orders", conn)
    df.to_csv(EXPORT_CSV, index=False)
    print(f"✅ Exported updated orders to {EXPORT_CSV}!")

# Run all functions
load_orders_data(ORDERS_CSV)
load_ip_data(IPS_CSV)
update_ip_data()
update_orders()
export_orders()

# Close DB connection
conn.close()
print("🎉 Process Completed Successfully!")

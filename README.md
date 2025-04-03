Project Overview
This project processes e-commerce order data by enriching missing address details using IP addresses. It also generates a quarterly sales report by state and city. The solution efficiently fetches location data, updates the database, and prevents redundant API calls.

Features
✅ Loads order data from a CSV file into an SQLite database
✅ Fetches missing city, state, and ZIP code from IP addresses using APIs
✅ Prevents duplicate API requests by caching previously processed IPs
✅ Generates a quarterly sales report in Excel format
✅ Optimized for large datasets (100,000+ records)


Setup & Installation

1. Install Dependencies
pip install pandas requests sqlite3 openpyxl

2. Prepare the Database

3. Run the Address Enrichment
This will Load the orders and IP addresses from CSV files
Fetch missing city, state, and ZIP details
Update the orders database


Project Structure
order-processing/
│-- orders_file.csv        # Raw order data
│-- ip_addresses.csv       # List of customer IPs
│-- script.py              # Main Python script
│-- database.sql           # SQL scripts for creating tables
│-- updated_orders.csv     # Processed orders with enriched addresses
│-- README.md              # Instructions and documentation

Customization
Modify ORDERS_CSV and IPS_CSV paths in script.py if using different file locations.
Adjust API settings (e.g., API keys) in the script for geolocation services.

Future Improvements
Support for more geolocation APIs

Optimization for real-time order processing

Cloud database integration

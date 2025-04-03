Project Overview
This project processes e-commerce order data by enriching missing address details using IP addresses. It also generates a quarterly sales report by state and city. The solution efficiently fetches location data, updates the database, and prevents redundant API calls.

Features
✅ Loads order data from a CSV file into an SQLite database
✅ Fetches missing city, state, and ZIP code from IP addresses using APIs
✅ Prevents duplicate API requests by caching previously processed IPs
✅ Generates a quarterly sales report in Excel format
✅ Optimized for large datasets (100,000+ records)

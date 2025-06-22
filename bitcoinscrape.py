import requests
import pymysql
import re
from datetime import datetime

# Database credentials
DB_HOST = '66.179.95.61'
DB_USER = 'root'  # Replace with your MySQL username
DB_PASSWORD = 'PtwaY7Z6'  # Replace with your MySQL password
DB_NAME = 'cryptodata'  # Replace with your MySQL database name

# CoinDesk URL
COINDESK_URL = 'https://www.coindesk.com/price/bitcoin'

def fetch_bitcoin_price():
    """Fetches the current Bitcoin price from CoinDesk."""
    try:
        response = requests.get(COINDESK_URL)
        response.raise_for_status()  # Raise an exception for bad status codes

        print(response.text)
        # Look for the price using a regular expression
        # The price is often found within a <span class="typography typography-headline3...">$...,...</span> tag
        # <div class="text-5xl lg:text-7xl font-mono inline-block relative tabular-nums __web-inspector-hide-shortcut__"><span class="">$94,117.93</span><div class="absolute right-0 translate-x-full top-1/2 -translate-y-1/2 flex justify-end items-center gap-0"><svg class="w-[25px] h-[25px]" fill="none" height="24" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path d="M15.79 11.71L13.2 14.3C12.81 14.69 12.18 14.69 11.79 14.3L9.19995 11.71C8.56995 11.08 9.00995 10 9.89995 10H15.09C15.98 10 16.42 11.08 15.79 11.71Z" fill="#F05C5C"></path></svg><span class="-ml-1 font-medium text-base lg:text-lg">0.17%</span></div></div>
        price_match = re.search(r'<meta name="description" (?:\$)([\d,.]+?)"/>', response.text)
        if price_match:
            price_str = price_match.group(1).replace(',', '')  # Remove commas
            return float(price_str)
        else:
            print("Could not find Bitcoin price on the page.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from CoinDesk: {e}")
        return None

def store_price_in_db(price):
    """Stores the Bitcoin price and timestamp in a MySQL database."""
    if price is not None:
        try:
            connection = pymysql.connect(host=DB_HOST,
                                         user=DB_USER,
                                         password=DB_PASSWORD,
                                         database=DB_NAME)
            cursor = connection.cursor()

            # Create table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS bitcoin_prices (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    price DECIMAL(10, 4) NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            connection.commit()

            # Insert the current price
            sql = "INSERT INTO bitcoin_prices (price) VALUES (%s)"
            cursor.execute(sql, (price,))
            connection.commit()
            print(f"Bitcoin price ({price:.2f}) stored in the database at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        except pymysql.Error as e:
            print(f"Error connecting to or interacting with the database: {e}")
        finally:
            if connection:
                cursor.close()
                connection.close()

if __name__ == "__main__":
    bitcoin_price = fetch_bitcoin_price()
    if bitcoin_price:
        store_price_in_db(bitcoin_price)

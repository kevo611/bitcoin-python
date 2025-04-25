
import mysql.connector
import time
import datetime
import requests
from bs4 import BeautifulSoup
import locale # Needed for a later example, but good practice to import at top

# Error: 2003: Can't connect to MySQL server on 'db5017731874.hosting-data.io:3306' (Errno 11001: getaddrinfo failed)

# Database connection details
DB_HOST = "db5017731874.hosting-data.io"  # Replace with your MySQL host
DB_USER = "dbu271559"  # Replace with your MySQL username
DB_PASSWORD = "420BUD420"  # Replace with your MySQL password
DB_NAME = "cryptodata"  # Replace with your MySQL database name
TABLE_NAME = "timestamp"
_price = 0.0
i = 44
def store_timestamp_in_mysql():
    global i
    """Connects to MySQL, creates a table if it doesn't exist,
    and stores the current system date and time."""
    try:
        # Establish a connection to the MySQL server
        mydb = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        # Create a cursor object to execute SQL queries
        mycursor = mydb.cursor()

        # Create the table if it doesn't exist
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id INT AUTO_INCREMENT PRIMARY KEY,
            coin VARCHAR(20),
            price float,
            timestamp DATETIME
        )
        """
        mycursor.execute(create_table_query)
        mydb.commit()

        # Get the current system date and time
        now = datetime.datetime.now()
        # SQL query to insert the timestamp
        insert_query = f"INSERT INTO {TABLE_NAME} (id, coin, price, timestamp) VALUES (%s, %s, %s, %s)"
        values = (i, 'bitcoin', get_float_from_string(get_bitcoin_price()), now.strftime('%Y-%m-%d %H:%M:%S'),)
        i = i + 1

        # Execute the insert query
        mycursor.execute(insert_query, values)
        mydb.commit()

        print(f"Current timestamp '{now.strftime('%Y-%m-%d %H:%M:%S')}' stored in table '{TABLE_NAME}'.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and the database connection
        if 'mydb' in locals() and mydb.is_connected():
            mycursor.close()
            mydb.close()
            print("MySQL connection closed.")

def print_current_time_with_milliseconds():
    now = datetime.datetime.now()
    print("Current system time:", now.strftime("%Y-%m-%d %H:%M:%S.%f"))

def ten_minute_timer():
    print_current_time_with_milliseconds()
    bitcoin_price = get_bitcoin_price()
    print(f"The current Bitcoin price is: {bitcoin_price}")
    for minute in range(1, 1440):
        print(f"Minute {minute} started...")
        time.sleep(60)  # Wait for 1 minute
        print(f"Minute {minute} finished.")
        print_current_time_with_milliseconds()
        bitcoin_price = get_bitcoin_price()
        print(f"The current Bitcoin price is: {bitcoin_price}")
        store_timestamp_in_mysql()
    print("Timer finished! 1440 minutes have passed.")

def get_bitcoin_price():
    """Fetches the current Bitcoin price from a specific website."""
    url = 'https://www.coindesk.com/price/bitcoin'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes

        soup = BeautifulSoup(response.content, 'html.parser')
        price_element = soup.find('div', class_='text-charcoal-600 font-mono')

        if price_element:
            price_text = price_element.text.strip()
            return price_text
        else:
            return "Could not find Bitcoin price on the page."

    except requests.exceptions.RequestException as e:
        return f"Error fetching the page: {e}"
    except Exception as e:
        return f"An error occurred: {e}"

def get_float_from_string(str):
    currency_string = str

    # 1. Remove the currency symbol ('$')
    # 2. Remove the thousands separator (',')
    # Chain the replace() calls for conciseness
    cleaned_string = currency_string.replace('$', '').replace(',', '')

    # 3. Convert the cleaned string to a float
    try:
        numerical_value = float(cleaned_string)
        print(numerical_value)       # Output: 93770.79
        print(type(numerical_value)) # Output: <class 'float'>
    except ValueError:
        print(f"Error: Could not convert '{cleaned_string}' to a float.")
    return numerical_value

if __name__ == "__main__":
    print("1440 min timer starting now:")
    ten_minute_timer()
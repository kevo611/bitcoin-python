import requests
import pymysql.cursors
import datetime

# --- Configuration ---

# CoinDesk API endpoint for current price
COINDESK_API_URL = "https://api.coindesk.com/v1/bpi/currentprice.json"

# MySQL Database Configuration
db_config = {
    'host': '66.179.95.61',  # Your database host (e.g., 'localhost', '127.0.0.1')
    'user': 'root', # Your MySQL username
    'password': 'PtwaY7Z6', # Your MySQL password
    'database': 'cryptodata', # The database name you created
    'charset': 'utf8mb4',
    'cursorclass': pymysql.cursors.DictCursor # Use dictionary cursor for easier access
}

# Table name to store Bitcoin prices
DB_TABLE_NAME = "bitcoin_prices"

# --- Functions ---

def get_bitcoin_price():
    """Retrieves the current Bitcoin price from the CoinDesk API (USD)."""
    print(f"Attempting to fetch data from {COINDESK_API_URL}")
    try:
        response = requests.get(COINDESK_API_URL)
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()

        # Extract USD price. CoinDesk API returns 'rate_float' which is a float.
        # You can change 'USD' to 'GBP' or 'EUR' if needed, provided by the API.
        price = data['bpi']['USD']['rate_float']
        timestamp = data['time']['updatedISO'] # Get the ISO formatted timestamp from the API

        print(f"Successfully fetched price: {price} USD at {timestamp}")
        return price, timestamp

    except requests.exceptions.RequestException as e:
        print(f"Error fetching Bitcoin price: {e}")
        return None, None
    except KeyError as e:
        print(f"Error parsing API response (missing key): {e}")
        return None, None
    except Exception as e:
        print(f"An unexpected error occurred during API fetch: {e}")
        return None, None

def create_price_table(connection):
    """Creates the bitcoin_prices table if it doesn't exist."""
    try:
        with connection.cursor() as cursor:
            sql = f"""
            CREATE TABLE IF NOT EXISTS `{DB_TABLE_NAME}` (
                `id` INT AUTO_INCREMENT PRIMARY KEY,
                `price` DECIMAL(10, 4) NOT NULL,
                `api_timestamp` DATETIME,
                `record_timestamp` TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET={db_config['charset']};
            """
            cursor.execute(sql)
        connection.commit()
        print(f"Ensured table '{DB_TABLE_NAME}' exists.")
    except pymysql.Error as e:
        print(f"Error creating table {DB_TABLE_NAME}: {e}")
        # Optionally rollback if creation fails, though CREATE IF NOT EXISTS is usually safe
        connection.rollback()


def insert_bitcoin_price(connection, price, api_timestamp_str):
    """Inserts the Bitcoin price and timestamp into the database."""
    try:
        # Convert the ISO timestamp string from API to a datetime object
        # Example format: "2023-10-27T10:30:00+00:00"
        # We might need to handle timezone or just store as is if MySQL supports it,
        # or strip timezone info if only DATETIME is used.
        # A simpler approach for DATETIME is to format it or just use the string if MySQL handles it.
        # Let's try converting to datetime object which pymysql handles well.
        # Handle potential timezone info by parsing appropriately.
        try:
             # Attempt to parse with timezone
            api_datetime_obj = datetime.datetime.fromisoformat(api_timestamp_str)
        except ValueError:
             # Fallback if timezone parsing fails or is not present as expected
             api_datetime_obj = datetime.datetime.strptime(api_timestamp_str, '%Y-%m-%dT%H:%M:%S%z') # Example format

        with connection.cursor() as cursor:
            sql = f"""
            INSERT INTO `{DB_TABLE_NAME}` (`price`, `api_timestamp`)
            VALUES (%s, %s)
            """
            cursor.execute(sql, (price, api_datetime_obj))

        connection.commit()
        print(f"Successfully inserted price {price} at API timestamp {api_timestamp_str} into '{DB_TABLE_NAME}'.")

    except pymysql.Error as e:
        print(f"Error inserting data into {DB_TABLE_NAME}: {e}")
        connection.rollback() # Rollback changes if insertion fails
    except ValueError as e:
         print(f"Error parsing API timestamp string '{api_timestamp_str}': {e}")
         connection.rollback()
    except Exception as e:
         print(f"An unexpected error occurred during database insertion: {e}")
         connection.rollback()


# --- Main Execution ---

if __name__ == "__main__":
    bitcoin_price, api_timestamp_str = get_bitcoin_price()

    if bitcoin_price is not None and api_timestamp_str is not None:
        connection = None
        try:
            # Establish database connection
            connection = pymysql.connect(**db_config)
            print("Database connection successful.")

            # Ensure the table exists
            create_price_table(connection)

            # Insert the retrieved price
            insert_bitcoin_price(connection, bitcoin_price, api_timestamp_str)

        except pymysql.Error as e:
            print(f"Database connection error: {e}")
        except Exception as e:
             print(f"An unexpected error occurred: {e}")
        finally:
            # Close the database connection
            if connection:
                connection.close()
                print("Database connection closed.")
    else:
        print("Could not retrieve Bitcoin price. Data not inserted into database.")
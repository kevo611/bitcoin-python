import mysql.connector
import datetime

# Database connection details
DB_HOST = "localhost"  # Replace with your MySQL host
DB_USER = "kevin"  # Replace with your MySQL username
DB_PASSWORD = "420420"  # Replace with your MySQL password
DB_NAME = "crpytodata"  # Replace with your MySQL database name
TABLE_NAME = "timestamp"
_price = 88888.88
def store_timestamp_in_mysql():
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
        insert_query = f"INSERT INTO {TABLE_NAME} (coin, price, timestamp) VALUES (%s, %f, %s)"
        values = ('bitcoin', 88888.88, now,)

        # Execute the insert query
        mycursor.execute(insert_query, values)
        mydb.commit()

        print(f"Current timestamp '{now.strftime('%Y-%m-%d %H:%M:%S.%f')}' stored in table '{TABLE_NAME}'.")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        # Close the cursor and the database connection
        if 'mydb' in locals() and mydb.is_connected():
            mycursor.close()
            mydb.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    store_timestamp_in_mysql()
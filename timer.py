import time
import datetime
import requests
from bs4 import BeautifulSoup

def print_current_time_with_milliseconds():
    now = datetime.datetime.now()
    print("Current system time:", now.strftime("%Y-%m-%d %H:%M:%S.%f"))

def ten_minute_timer():
    print_current_time_with_milliseconds()
    bitcoin_price = get_bitcoin_price()
    print(f"The current Bitcoin price is: {bitcoin_price}")
    for minute in range(1, 11):
        print(f"Minute {minute} started...")
        time.sleep(60)  # Wait for 1 minute
        print(f"Minute {minute} finished.")
        print_current_time_with_milliseconds()
        bitcoin_price = get_bitcoin_price()
        print(f"The current Bitcoin price is: {bitcoin_price}")
        get_bitcoin_price()
    print("Timer finished! 10 minutes have passed.")

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


if __name__ == "__main__":
    ten_minute_timer()
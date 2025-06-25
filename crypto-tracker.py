import time
import datetime
import requests
import sys # Import the sys module to access command-line arguments
import emoji # Import the emoji library

def print_current_time_with_milliseconds():
    """Prints the current system time with microseconds."""
    now = datetime.datetime.now()
    print("Current system time:", now.strftime("%Y-%m-%d %H:%M:%S.%f"))

def get_coin_price_api(coin_id):
    """Fetches the current price of a specified cryptocurrency using the CoinGecko API."""
    coin_id_lower = coin_id.lower()
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id_lower}&vs_currencies=usd'
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        data = response.json()
        
        # Check if the coin_id actually returned data
        if coin_id_lower not in data:
            # Return a tuple: (price, error_message)
            return None, f"Error: '{coin_id}' not found or no data for this ID from API."
            
        price = data[coin_id_lower]['usd']
        
        # Return the actual price and no error
        return price, None

    except requests.exceptions.RequestException as e:
        return None, f"Error fetching data from API for {coin_id}: {e}"
    except (KeyError, TypeError) as e:
        return None, f"Error parsing API response for {coin_id}: {e}. Make sure '{coin_id}' is a valid CoinGecko ID."

def price_tracker(coin_id_to_track, total_minutes_duration):
    """Tracks and prints the specified cryptocurrency price for a given duration in minutes,
    with 10-second interval print statements during the minute long wait,
    and indicates price change with a thumbs up/down emoji."""
    
    print(f"--- {coin_id_to_track.capitalize()} Price Tracker Started ---")
    print(f"Tracking for a total of {total_minutes_duration} minutes.")
    
    # Define the total sleep duration per minute (60 seconds)
    total_sleep_per_minute = 60
    # Define the interval for print statements during the sleep
    sub_interval = 10
    
    # Initialize previous_price to None so the first fetch doesn't compare
    previous_price = None 

    for minute_count in range(1, total_minutes_duration + 1): # Loop for the specified number of minutes
        print(f"\n--- Starting Cycle {minute_count} of {total_minutes_duration} for {coin_id_to_track.capitalize()} ---")
        print_current_time_with_milliseconds()
        
        current_price_value, error_message = get_coin_price_api(coin_id_to_track)
        
        if error_message:
            print(error_message)
            current_price_display = "N/A" # For display purposes
        else:
            current_price_display = f"${current_price_value:,.8f}"
            
            # --- Add emoji feedback based on price change ---
            feedback_emoji = ""
            if previous_price is not None and current_price_value is not None:
                if current_price_value > previous_price:
                    feedback_emoji = emoji.emojize(":thumbs_up:", language='en')
                elif current_price_value < previous_price:
                    feedback_emoji = emoji.emojize(":thumbs_down:", language='en')
                else:
                    feedback_emoji = emoji.emojize(":neutral_face:", language='en') # Or empty string for no change
            
            # Update previous_price only if we got a valid current price
            if current_price_value is not None:
                previous_price = current_price_value

        print(f"{coin_id_to_track.capitalize()} price at start of Cycle {minute_count}: {current_price_display} {feedback_emoji}")
        
        # Only sleep if it's not the last cycle
        if minute_count < total_minutes_duration:
            for sub_second_count in range(1, total_sleep_per_minute // sub_interval + 1):
                remaining_time = total_sleep_per_minute - (sub_second_count * sub_interval)
                print(f"   Next fetch in approximately {remaining_time} seconds...")
                time.sleep(sub_interval) # Wait for 10 seconds
            
    print(f"--- {coin_id_to_track.capitalize()} Price Tracker Finished ---")

# Example of how to run the tracker
if __name__ == "__main__":
    # Check for command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python your_script_name.py <cryptocurrency_id> [duration_in_minutes]")
        print("Example: python your_script_name.py ethereum 5")
        print("Example: python your_script_name.py bitcoin 10")
        print("Example: python your_script_name.py ripple 3")
        print("\nDefaulting to Ethereum for 10 minutes...")
        price_tracker("ethereum", 10) # Default values if no arguments are provided
    else:
        coin_id_param = sys.argv[1]
        duration_param = 10 # Default duration if not provided

        if len(sys.argv) > 2:
            try:
                duration_param = int(sys.argv[2])
                if duration_param <= 0:
                    print("Duration must be a positive integer. Defaulting to 10 minutes.")
                    duration_param = 10
            except ValueError:
                print("Invalid duration provided. Duration must be an integer. Defaulting to 10 minutes.")
                duration_param = 10
        
        print(f"Tracking: {coin_id_param.capitalize()} for {duration_param} minutes.")
        price_tracker(coin_id_param, duration_param)
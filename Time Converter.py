import pytz
from datetime import datetime
import re
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from functools import lru_cache

# Caching the results of geocoding to avoid repeated API calls
@lru_cache(maxsize=100)  # Cache up to 100 city lookups
def get_timezone_from_city(city_name):
    geolocator = Nominatim(user_agent="city_timezone_finder")
    location = geolocator.geocode(city_name, exactly_one=True)
    
    if location:
        tf = TimezoneFinder()
        timezone_str = tf.timezone_at(lng=location.longitude, lat=location.latitude)
        if timezone_str:
            return timezone_str
    return None

# Function to convert time to Tehran time
def convert_to_tehran_time(input_str):
    # Extract the time and city from the input string
    match = re.match(r"(\d+)\s*(am|pm)\s*(.+)", input_str, re.IGNORECASE)
    
    if match:
        hour = int(match.group(1))
        period = match.group(2).lower()
        city = match.group(3).strip()
        
        # Convert to 24-hour format
        if period == 'pm' and hour != 12:
            hour += 12
        elif period == 'am' and hour == 12:
            hour = 0
        
        # Get the current date
        current_date = datetime.now().date()
        
        # Find the timezone based on the city
        timezone_name = get_timezone_from_city(city)
        if not timezone_name:
            return f"City '{city}' is not recognized or timezone could not be determined."

        # Convert the time in the city's timezone
        city_timezone = pytz.timezone(timezone_name)
        city_time = city_timezone.localize(datetime(current_date.year, current_date.month, current_date.day, hour))
        
        # Convert the time to Tehran timezone
        tehran_timezone = pytz.timezone("Asia/Tehran")
        tehran_time = city_time.astimezone(tehran_timezone)
        
        # Return only the time in 12-hour format with AM/PM
        return tehran_time.strftime("%I:%M %p")
    else:
        return "Invalid input format. Please enter in '8pm california' format."

# Asking the user for input
input_str = input("Enter time and city (e.g., '8pm california'): ").strip()

# Convert and print the result
tehran_time = convert_to_tehran_time(input_str)
print(f"Time in Tehran: {tehran_time}")
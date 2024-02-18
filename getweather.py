# getweather.py
import os
import requests

def get_weather_by_zip(zip_code, country_code='us'):
    api_key = os.getenv('OPENWEATHER_API_KEY')
    if not api_key:
        raise ValueError("OpenWeatherMap API key not found. Please set the OPENWEATHER_API_KEY environment variable.")
    
    base_url = "http://api.openweathermap.org/data/2.5/weather"
    complete_url = f"{base_url}?zip={zip_code},{country_code}&appid={api_key}&units=imperial"

    response = requests.get(complete_url)
    weather_data = response.json()

    if weather_data["cod"] != 200:
        raise Exception("Failed to retrieve weather data.")
    
    return weather_data

def display_weather(zip_code):
    try:
        weather_data = get_weather_by_zip(zip_code)
        weather_description = weather_data["weather"][0]["description"]
        temperature = weather_data["main"]["temp"]
        print(f"Weather: {weather_description}, Temperature: {temperature}°F")
    except Exception as e:
        print(f"Error getting weather data: {e}")

# Example usage
if __name__ == "__main__":
    zip_code = '98040'  # Replace with the desired ZIP code
    display_weather(zip_code)

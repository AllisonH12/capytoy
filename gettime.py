from datetime import datetime
import holidays

def get_detailed_time_info(country_code='US'):
    # Get the current local datetime
    now = datetime.now()

    # Format the datetime and get the day of the week
    formatted_time = now.strftime("%Y-%m-%d %H:%M:%S")
    day_of_week = now.strftime("%A")

    # Check for holidays in the specified country
    country_holidays = holidays.CountryHoliday(country_code)
    today_is_holiday = now.date() in country_holidays
    holiday_name = country_holidays.get(now.date())

    # Prepare the response
    response = f"The local time is: {formatted_time}."
    response += f"\nToday is {day_of_week}."
    
    if today_is_holiday:
        response += f"\nToday is also a holiday: {holiday_name}."
    else:
        response += "\nToday is not a holiday."

    return response

# Example usage
if __name__ == "__main__":
    # You can change 'US' to your country code as needed
    print(get_detailed_time_info('US'))


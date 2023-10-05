import requests
from datetime import datetime, timedelta
import calendar
import json
from getstaffdata import is_person_in_company
import os
from dotenv import load_dotenv

load_dotenv()
# Set application's credentials
tenant_id = os.environ.get('TENANT_ID')
client_id = os.environ.get('CLIENT_ID')
client_secret = os.environ.get('CLIENT_SECRET') 

# Function to get available time according to user email
def get_available_times(fullname, time_interval_minutes=60):
    user_details = is_person_in_company(fullname)
    staff_info = json.loads(user_details)
    if staff_info and isinstance(staff_info, list):
        first_user_info = staff_info[0]  
        user_email = first_user_info.get('Email', 'Email not found')  # Get the email field, or a default value if not found
    else:
        return "There was an error retrieving available time, please try again"
    
    # Obtain an access token
    token_url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    token_data = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret,
        "scope": "https://graph.microsoft.com/.default",
    }
    try:
        token_response = requests.post(token_url, data=token_data)
        token_response.raise_for_status()  # Check for HTTP errors
        access_token = token_response.json().get("access_token")
        if access_token is None:
            raise ValueError("Access token not found in token response")
    except requests.exceptions.RequestException as e:
        print("Token retrieval error:", e)
        if "token_response" in locals():
            print("Token response content:", token_response.content)

    # Get the current time and find the next round hour
    current_time = datetime.utcnow()
    next_round_hour = (current_time + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    
    # Set the start and end times for the availability query for the current day
    start_time = next_round_hour.isoformat()  # Next round hour in UTC
    end_time = (next_round_hour).replace(hour=17, minute=0, second=0, microsecond=0).isoformat()  # 5:00 PM in UTC

    # API endpoint for finding available times
    endpoint = f"https://graph.microsoft.com/v1.0/users/{user_email}/calendar/getSchedule"

    # Specify the payload for the request for the current day
    payload = {
        "Schedules": [user_email],  # Use the user's email or ID
        "StartTime": {
            "dateTime": start_time,
            "timeZone": "UTC",
        },
        "EndTime": {
            "dateTime": end_time,
            "timeZone": "UTC",
        },
    }

    # Set up headers with the access token
    headers = {
        "Authorization": "Bearer " + access_token,
        "Content-Type": "application/json",
    }

   # Make the request for the current day
    try:
        response = requests.post(endpoint, json=payload, headers=headers)
        response.raise_for_status()  # Check for HTTP errors
        data = response.json()
        # Process the data to extract available time slots for the current day
        availability_view = data["value"][0]["availabilityView"]
        current_utc_time = datetime.utcnow() + timedelta(hours=1) #For West African Time (WAT)
        start_timestamp = datetime.strptime(start_time, "%Y-%m-%dT%H:%M:%S")
        available_times = []

        # Check for available time slots for the current day
        for i, slot in enumerate(availability_view):
            if slot == "0":  # Slot is available
                current_time = start_timestamp + timedelta(minutes=i * time_interval_minutes)
                 # Compare with the current UTC time
                if current_time >= current_utc_time:
                    if current_time.weekday() in [calendar.SATURDAY, calendar.SUNDAY]:
                        continue
                    # Check if the time slot is between 8 AM and 5 PM
                    if 8 <= current_time.hour < 17:
                        day_name = calendar.day_name[current_time.weekday()]
                        formatted_start = current_time.strftime('%Y-%m-%d %I:%M %p')  # 12-hour format with AM/PM
                        formatted_end = (current_time + timedelta(minutes=time_interval_minutes)).strftime('%I:%M %p')
                        available_times.append(f"{day_name}, {formatted_start} - {formatted_end}")

        # If no available times for the current day, query for the next day
        if not available_times:
            next_day = current_time + timedelta(days=1)
            start_time = next_day.replace(hour=8, minute=0, second=0, microsecond=0).isoformat()
            end_time = next_day.replace(hour=17, minute=0, second=0, microsecond=0).isoformat()
            
            # Specify the payload for the request for the next day
            payload = {
                "Schedules": [user_email],
                "StartTime": {
                    "dateTime": start_time,
                    "timeZone": "UTC",
                },
                "EndTime": {
                    "dateTime": end_time,
                    "timeZone": "UTC",
                },
            }

            # Make the request for the next day
            response = requests.post(endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            availability_view = data["value"][0]["availabilityView"]
            available_times = []

            for i, slot in enumerate(availability_view):
                if slot == "0":  # Slot is available
                    current_time = start_timestamp + timedelta(minutes=i * time_interval_minutes)
                    if current_time.weekday() in [calendar.SATURDAY, calendar.SUNDAY]:
                        continue
                    if 8 <= current_time.hour < 17:
                        day_name = calendar.day_name[current_time.weekday()]
                        formatted_start = current_time.strftime('%Y-%m-%d %I:%M %p')
                        formatted_end = (current_time + timedelta(minutes=time_interval_minutes)).strftime('%I:%M %p')
                        available_times.append(f"{day_name}, {formatted_start} - {formatted_end}")

        available_times_list = []
        for time_slot in available_times:
            available_times_list.append(time_slot)
        available_times_json = json.dumps(available_times_list)
        return available_times_json

    except requests.exceptions.RequestException as e:
        if "response" in locals() and hasattr(response, "content"):
            return {"error": "Response content", "content": response.content}
       

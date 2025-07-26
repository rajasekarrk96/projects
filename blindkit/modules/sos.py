from twilio.rest import Client
import requests

def get_location():
    try:
        response = requests.get("https://ipinfo.io/json")
        data = response.json()
        location = data.get("loc", "Unknown location")  # lat,long
        city = data.get("city", "Unknown city")
        region = data.get("region", "Unknown region")
        country = data.get("country", "Unknown country")
        # Create Google Maps Link
        if location != "Unknown":
            maps_link = f"https://www.google.com/maps?q={location}"        
        return f"{city}, {region}, {country}\n📍 Location: {location}\n🔗 Google Maps: {maps_link}"
    except Exception as e:
        return "Location unavailable"

def send_sos():
    #client = Client("account", "password")
    
    location = get_location()
    message_body = f"🚨 SOS Alert 🚨\nPlease send help!\nLocation: {location}"
    message = "SOS sent"
    """message = client.messages.create(
        from_="+123456789",
        body=message_body,
        to="+91999963170"
    )"""
    return message.sid
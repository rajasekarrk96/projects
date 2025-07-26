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
    client = Client("ACa10564d5a53f60c978100168e3b2b9e4", "f142c4816281d22b4cf2b2404abeaf9b")
    
    location = get_location()
    message_body = f"🚨 SOS Alert 🚨\nPlease send help!\nLocation: {location}"
    
    message = client.messages.create(
        from_="+18142508047",
        body=message_body,
        to="+919843163170"
    )
    return message.sid
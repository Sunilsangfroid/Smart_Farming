import requests
import os
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage

# Load environment variables
load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "").strip().replace('"', '').replace("'", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip().replace('"', '').replace("'", "")

# Validate API Keys
if not WEATHER_API_KEY:
    raise ValueError("❌ WEATHER_API_KEY is missing. Check your .env file.")
if not GOOGLE_API_KEY:
    raise ValueError("❌ GOOGLE_API_KEY is missing. Check your .env file.")

def get_weather(location):
    """Fetches weather data for the given location from WeatherAPI.com."""
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={location}&days=1"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise error for HTTP error codes
        weather_data = response.json()

        if "error" in weather_data:
            print(f"❌ Weather API Error: {weather_data['error']['message']}")
            return None

        return weather_data
    except requests.exceptions.HTTPError as http_err:
        print(f"❌ HTTP Error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"❌ Request Exception: {req_err}")

    return None


def generate_cultivation_plan(seed_type, soil_type, location, date):
    """Generates a cultivation plan using weather data and Gemini AI."""
    weather_data = get_weather(location)
    if not weather_data:
        return "Unable to fetch weather data at the moment."

    weather_summary = weather_data["forecast"]["forecastday"][0]["day"]["condition"]["text"]

    # Create Prompt
    prompt = f"""
    I am planning to cultivate {seed_type}.
    I have {soil_type} soil available in the region of {location} on {date}.
    The current weather forecast for today is: {weather_summary}.
    Based on this information, provide a detailed cultivation plan including:
    - Soil preparation
    - Irrigation
    - Fertilizer recommendations
    - Best farming practices.
    """

    # Initialize Gemini Model
    model = ChatGoogleGenerativeAI(model='gemini-1.5-pro', api_key=GOOGLE_API_KEY)

    # Generate Response
    message = HumanMessage(content=prompt)
    response = model([message])

    return response.content  # Extract response text properly

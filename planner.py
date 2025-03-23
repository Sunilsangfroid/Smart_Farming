import requests
import os
import json
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from langchain.pydantic_v1 import BaseModel, Field
from typing import List, Optional

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "").strip().replace('"', '').replace("'", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip().replace('"', '').replace("'", "")


if not WEATHER_API_KEY:
    raise ValueError("WEATHER_API_KEY is missing. Check your .env file.")
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEY is missing. Check your .env file.")

class CultivationPlan(BaseModel):
    suitability: str = Field(..., description="Whether the weather is suitable for cultivation")
    problem: Optional[str] = Field(None, description="Potential problems if the weather is unsuitable")
    focus_if_forced: Optional[str] = Field(None, description="Key focus areas if forced to cultivate")
    nearby_better_locations: Optional[List[str]] = Field(None, description="Nearby locations with better weather conditions")
    cultivation_plan: dict = Field(..., description="Detailed cultivation plan with soil preparation, irrigation, fertilizer recommendations, and best practices")

def get_weather(location):
    """Fetches weather data for the given location from WeatherAPI.com."""
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={location}&days=1"
    
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise error for HTTP error codes
        weather_data = response.json()

        if "error" in weather_data:
            print(f"Weather API Error: {weather_data['error']['message']}")
            return None

        return weather_data
    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP Error: {http_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"Request Exception: {req_err}")

    return None


def generate_cultivation_plan(seed_type, soil_type, location, date):
    """Generates a structured cultivation plan considering weather conditions in text format."""
    weather_data = get_weather(location)
    if not weather_data:
        return "Unable to fetch weather data at the moment."

    weather_summary = weather_data["forecast"]["forecastday"][0]["day"]["condition"]["text"]
    temperature = weather_data["forecast"]["forecastday"][0]["day"]["avgtemp_c"]
    rainfall = weather_data["forecast"]["forecastday"][0]["day"]["totalprecip_mm"]

    # Create structured prompt
    prompt = f"""
    I am planning to cultivate {seed_type}.
    I have {soil_type} soil available in {location} on {date}.
    The current weather forecast:
    - Condition: {weather_summary}
    - Avg Temperature: {temperature}°C
    - Rainfall: {rainfall} mm
    
    Based on this, provide a **structured response** in the following text format:
    
    "Cultivation Plan for {seed_type} in {location} on {date}
    Suitability: (Suitable/Unsuitable)
    Potential Problems: (List problems if unsuitable)
    Focus Areas if Forced to Cultivate: (Precautions)
    Nearby Areas with Better Conditions: (List of better locations)
    Cultivation Plan:
       Soil Preparation: (Steps)
       Irrigation: (Watering recommendations)
       Fertilizer Recommendations: (Best fertilizers)
       Best Practices: (Final tips)
    
    Weather Summary:
    - Condition: {weather_summary}
    - Avg Temperature: {temperature}°C
    - Rainfall: {rainfall} mm
    
    Conclusion: (Final recommendation)"
    
    Ensure clarity and proper formatting.
    """

    # Initialize Gemini Model
    model = ChatGoogleGenerativeAI(model='gemini-1.5-pro', api_key=GOOGLE_API_KEY)

    # Generate Response
    message = HumanMessage(content=prompt)
    response = model([message]).content

    return response

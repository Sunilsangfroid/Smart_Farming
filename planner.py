import requests
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage
from dotenv import load_dotenv

load_dotenv()
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")
if not google_api_key:
    raise ValueError("GOOGLE_API_KEY is not set in the environment variables")

def get_weather(location):
    url = f"http://api.weatherapi.com/v1/forecast.json?key={WEATHER_API_KEY}&q={location}&days=7"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    return None

def generate_cultivation_plan(seed_type, soil_type, location, date):
    weather_data = get_weather(location)
    if not weather_data:
        return "Unable to fetch weather data at the moment."

    weather_summary = weather_data["forecast"]["forecastday"][0]["day"]["condition"]["text"]

    prompt = f"""
    I am planning to cultivate {seed_type}. 
    I have {soil_type} soil available in the region of {location} on {date}.
    The current weather forecast for today is: {weather_summary}.
    Based on this information, provide a detailed cultivation plan including soil preparation, irrigation, fertilizer recommendations, and best practices.
    """
    model = ChatGoogleGenerativeAI(model='gemini-1.5-pro', api_key=google_api_key)
    from langchain.schema import HumanMessage
    message = HumanMessage(content=prompt)
    plan = model([message])
    return plan

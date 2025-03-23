import streamlit as st
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from firebase_auth import signup_user, login_user
from farmingbot import get_farming_response
from planner import generate_cultivation_plan
import json

# -------------------------------
# 🔹 Class for Authentication
# -------------------------------
class AuthManager:
    def __init__(self):
        self.user = None

    def signup(self):
        """Handles User Signup"""
        st.header("🔐 Sign Up")
        email = st.text_input("📧 Email")
        password = st.text_input("🔑 Password", type="password")
        if st.button("Sign Up"):
            result = signup_user(email, password)
            if result.get("success"):
                st.success(f"🎉 User created successfully with UID: {result.get('uid')}")
            else:
                st.error(f"⚠️ Signup failed: {result.get('error')}")

    def login(self):
        """Handles User Login"""
        st.header("🔑 Login")
        email = st.text_input("📧 Email", key="login_email")
        password = st.text_input("🔑 Password", type="password", key="login_password")
        if st.button("Login"):
            response = login_user(email, password)
            if "idToken" in response:
                st.success("✅ Logged in successfully!")
                st.session_state["user"] = response
            else:
                st.error("❌ Invalid credentials")

    def is_logged_in(self):
        """Check if user is logged in"""
        return "user" in st.session_state

# -------------------------------
# 🔹 Class for Cultivation Planner
# -------------------------------
class CultivationPlanner:
    def __init__(self):
        self.default_location = {"lat": 28.6139, "lon": 77.2090}  # Default: New Delhi

    def get_location_from_address(self, address):
        """Fetch latitude and longitude from entered location."""
        geolocator = Nominatim(user_agent="geoapi")
        location = geolocator.geocode(address)
        if location:
            return {"lat": location.latitude, "lon": location.longitude}
        return None

    def render_map(self, user_input_location):
        """Render a folium map and update it based on user input."""
        if user_input_location:
            location = self.get_location_from_address(user_input_location)
            if location:
                lat, lon = location["lat"], location["lon"]
            else:
                st.warning("⚠️ Location not found! Showing default map.")
                lat, lon = self.default_location["lat"], self.default_location["lon"]
        else:
            lat, lon = self.default_location["lat"], self.default_location["lon"]

        # Create map centered on detected/default location
        farm_map = folium.Map(location=[lat, lon], zoom_start=10)
        folium.Marker([lat, lon], tooltip="📍 Selected Location").add_to(farm_map)

        # Display the map and capture interactions
        map_data = st_folium(farm_map, height=400, width=700)

        # Handle live location selection
        if map_data and map_data.get("last_clicked"):
            selected_lat = map_data["last_clicked"].get("lat", lat)
            selected_lon = map_data["last_clicked"].get("lng", lon)
            st.success(f"📌 Selected Location: {selected_lat}, {selected_lon}")
        else:
            st.info(f"🌍 Default Location: {lat}, {lon}")

    def render(self):
        st.header("🌱 Cultivation Planner")
        seed_type = st.text_input("🌾 Enter crop/seed type (e.g., Wheat, Rice)")
        soil_type = st.selectbox("🌍 Select Soil Type", ["Loamy", "Sandy", "Clay", "Silty"])
        user_location = st.text_input("📍 Enter your location", placeholder="E.g., Mumbai, Bangalore")
        cultivation_date = st.date_input("📅 Select Date")

        if "cultivation_report" not in st.session_state:
            st.session_state["cultivation_report"] = None  # Initialize

        if st.button("📋 Generate Cultivation Plan"):
            st.session_state["cultivation_report"] = generate_cultivation_plan(seed_type, soil_type, user_location, cultivation_date)

        # Display the saved report
        if st.session_state["cultivation_report"]:
            st.subheader("📋 Generated Cultivation Plan")
            st.write(st.session_state["cultivation_report"])


        self.render_map(user_location)

# -------------------------------
# 🔹 Class for FarmingBot
# -------------------------------
class FarmingBot:
    def __init__(self):
        if "search_history" not in st.session_state:
            st.session_state["search_history"] = []

    def save_search(self, query, response):
        """Stores summarized past searches (Only last 5)"""
        summary = {"query": query, "response": response[:100]}  # Store only first 100 chars
        st.session_state["search_history"].append(summary)

        if len(st.session_state["search_history"]) > 5:
            st.session_state["search_history"].pop(0)  # Keep only last 5 searches

    def render(self):
        st.header("🤖 FarmingBot")
        query = st.text_area("💬 Ask your farming question:")

        if st.button("🔍 Get Answer"):
            answer = get_farming_response(query)
            self.save_search(query, answer)
            st.write(answer)

        # Display search history
        if st.session_state["search_history"]:
            st.subheader("📜 Your Past Searches")
            for i, search in enumerate(st.session_state["search_history"], 1):
                st.write(f"**{i}. {search['query']}** → {search['response']}...")

# -------------------------------
# 🔹 Main Application
# -------------------------------
def main():
    st.title("🌾 Smart Agriculture Platform")

    auth_manager = AuthManager()

    menu = st.sidebar.selectbox("📌 Menu", ["Home", "Signup", "Login"])

    if menu == "Signup":
        auth_manager.signup()
    elif menu == "Login":
        auth_manager.login()

    if auth_manager.is_logged_in():
        st.sidebar.success("✅ Logged in")
        dashboard_page = st.sidebar.radio("📊 Dashboard", ["FarmingBot", "Cultivation Planner", "My Searches"])

        if dashboard_page == "FarmingBot":
            FarmingBot().render()

        elif dashboard_page == "Cultivation Planner":
            CultivationPlanner().render()

        elif dashboard_page == "My Searches":
            st.header("📜 Search History")
            if "search_history" in st.session_state and st.session_state["search_history"]:
                for i, search in enumerate(st.session_state["search_history"], 1):
                    st.write(f"**{i}. {search['query']}** → {search['response']}...")
            else:
                st.info("🔍 No past searches yet.")

if __name__ == "__main__":
    main()

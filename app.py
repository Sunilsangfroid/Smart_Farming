import streamlit as st
from firebase_auth import signup_user, login_user

st.title("Smart Agriculture Platform")

# Sidebar navigation
menu = st.sidebar.selectbox("Menu", ["Home", "Signup", "Login"])

if menu == "Signup":
    st.header("Sign Up")
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    if st.button("Sign Up"):
        result = signup_user(email, password)
        if result.get("success"):
            st.success(f"User created successfully with UID: {result.get('uid')}")
        else:
            st.error(f"Signup failed: {result.get('error')}")


elif menu == "Login":
    st.header("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login"):
        response = login_user(email, password)
        if "idToken" in response:
            st.success("Logged in successfully!")
            st.session_state["user"] = response
            # Optionally, you can provide a link or message to refresh the page.
            st.info("Please refresh the page to continue.")
            # Alternatively, remove the rerun line:
            # st.experimental_rerun()
        else:
            st.error("Invalid credentials")


# If the user is logged in, show the dashboard
if "user" in st.session_state:
    st.sidebar.success("Logged in as: " + st.session_state["user"]["email"])
    dashboard_page = st.sidebar.radio("Dashboard", ["FarmingBot", "Cultivation Planner"])

    if dashboard_page == "FarmingBot":
        st.header("FarmingBot")
        st.subheader("Ask your farming questions below:")
        query = st.text_area("Enter your question:")
        if st.button("Get Answer"):
            from farmingbot import get_farming_response
            answer = get_farming_response(query)
            st.write(answer)

    elif dashboard_page == "Cultivation Planner":
        st.header("Cultivation Planner")
        st.subheader("Plan your cultivation based on your local conditions.")
        seed_type = st.text_input("Enter crop/seed type (e.g., Wheat, Rice)")
        soil_type = st.selectbox("Select Soil Type", ["Loamy", "Sandy", "Clay", "Silty"])
        location = st.text_input("Enter your location")
        cultivation_date = st.date_input("Select Date")
        if st.button("Generate Cultivation Plan"):
            from planner import generate_cultivation_plan
            plan = generate_cultivation_plan(seed_type, soil_type, location, cultivation_date)
            st.write(plan)
            
        # Optionally, add an interactive map for location selection
        import folium
        from streamlit_folium import folium_static
        st.subheader("Select your farm location on the map:")
        # Default coordinates (you can choose a default center)
        lat, lon = 20.5937, 78.9629  
        farm_map = folium.Map(location=[lat, lon], zoom_start=5)
        folium.Marker([lat, lon], tooltip="Farm Location").add_to(farm_map)
        folium_static(farm_map)

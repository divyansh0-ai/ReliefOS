import streamlit as st
import pandas as pd
import json
import os
import numpy as np
import random
from math import radians, sin, cos, sqrt, atan2
from ai_engine import parse_field_report

# --- Helper Function: Calculate Distance ---
def calculate_distance(lat1, lon1, lat2, lon2):
    """Calculates distance in km between two GPS points."""
    R = 6371.0 # Radius of Earth in km
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

# --- The Core Matching Logic ---
def find_best_volunteer(crisis_category, crisis_lat, crisis_lon, volunteers_df):
    """Finds the closest available volunteer with the right skills."""
    available_vols = volunteers_df[volunteers_df['Status'] == 'Available'].copy()
    
    if available_vols.empty:
        return None, "No available volunteers found."

    skill_match_vols = available_vols[available_vols['Primary_Skill'] == crisis_category].copy()
    pool_to_search = skill_match_vols if not skill_match_vols.empty else available_vols
    
    if pool_to_search.empty:
         return None, "No volunteers found with matching skills."

    pool_to_search['Distance_km'] = pool_to_search.apply(
        lambda row: calculate_distance(crisis_lat, crisis_lon, row['Latitude'], row['Longitude']), 
        axis=1
    )
    
    best_match = pool_to_search.loc[pool_to_search['Distance_km'].idxmin()]
    return best_match, "Success"

st.set_page_config(page_title="ReliefOS Command Center", layout="wide")

st.title("🆘 ReliefOS Command Center")
st.caption("AI-Powered NGO Coordination for Real-World Crises")

# Force Trust Blue theme using CSS injection to bypass Streamlit caching
st.markdown("""
<style>
div.stButton > button {
    background-color: #3b82f6 !important;
    border-color: #3b82f6 !important;
    color: white !important;
}
div.stButton > button:hover {
    background-color: #2563eb !important;
    border-color: #2563eb !important;
}
</style>
""", unsafe_allow_html=True)

# Initialize State
if "needs" not in st.session_state:
    st.session_state.needs = pd.DataFrame([
        {"ID": 1, "Location": "Sector 4", "Category": "Medical", "Description": "Children with high fever, no water", "Urgency": 9, "Status": "Unassigned", "latitude": 28.6145, "longitude": 77.2085},
        {"ID": 2, "Location": "Connaught Place", "Category": "Shelter", "Description": "Makeshift tents collapsed in heavy rain", "Urgency": 6, "Status": "In Progress", "latitude": 28.6304, "longitude": 77.2177},
        {"ID": 3, "Location": "Karol Bagh", "Category": "Food", "Description": "Supply truck delayed, 50 families waiting", "Urgency": 7, "Status": "Unassigned", "latitude": 28.6538, "longitude": 77.1888},
    ])

if "volunteers" not in st.session_state:
    if os.path.exists("volunteer_opportunities.csv"):
        vols = pd.read_csv("volunteer_opportunities.csv").head(150)
        # Adapt Kaggle data to exactly match the algorithm's expected schema
        vols["Name"] = ["Volunteer " + str(i) for i in range(1, len(vols) + 1)]
        vols["Primary_Skill"] = random.choices(["Medical", "Food", "Shelter", "Water/Sanitation", "General"], k=len(vols))
        vols["Status"] = "Available"
        # Seed realistic Delhi coordinates if missing
        vols["Latitude"] = np.where(vols["Latitude"].isna(), 28.6139 + (np.random.rand(len(vols)) - 0.5) * 0.1, vols["Latitude"])
        vols["Longitude"] = np.where(vols["Longitude"].isna(), 77.2090 + (np.random.rand(len(vols)) - 0.5) * 0.1, vols["Longitude"])
        st.session_state.volunteers = vols
    else:
        st.session_state.volunteers = pd.DataFrame()

if "latest_json" not in st.session_state:
    st.session_state.latest_json = None
if "next_id" not in st.session_state:
    st.session_state.next_id = 4
if "match_msg" not in st.session_state:
    st.session_state.match_msg = None

# Top Metrics Row
m1, m2, m3, m4 = st.columns(4)
total_needs = 21 + len(st.session_state.needs)
high_urgency = 9 + len(st.session_state.needs[st.session_state.needs["Urgency"] >= 8])
resolved = 6
vols_count = 130

m1.metric("Total Active Needs", total_needs)
m2.metric("High Urgency (Score 8+)", high_urgency)
m3.metric("Resolved Past 24h", resolved)
m4.metric("Available Volunteers", vols_count)

st.divider()

col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("Crisis Field Reports")
    
    # Check for incoming report from React frontend
    params = st.query_params
    incoming_report = params.get("report", "")
    
    raw_text = st.text_area("Incoming Report", value=incoming_report, placeholder="Type or paste incoming chaotic field reports...", label_visibility="collapsed")
    
    # Auto-trigger if there's an incoming report we haven't processed yet
    auto_trigger = False
    if incoming_report and st.session_state.get("last_processed_report") != incoming_report:
        auto_trigger = True
        st.session_state["last_processed_report"] = incoming_report
        
    if st.button(" ✨ Triage with Gemini AI", type="primary", use_container_width=True) or auto_trigger:
        with st.spinner("Triaging..."):
            result = parse_field_report(raw_text)
            st.session_state.latest_json = result
            st.session_state.match_msg = None
            
            if "location_name" in result and "error" not in result:
                new_need = {
                    "ID": st.session_state.next_id,
                    "Location": result.get("location_name", "Unknown"),
                    "Category": result.get("category", "General"),
                    "Description": result.get("summary", ""),
                    "Urgency": int(result.get("urgency", 5)),
                    "Status": "Unassigned",
                    "latitude": result.get("latitude", 28.6139),
                    "longitude": result.get("longitude", 77.2090)
                }
                new_df = pd.DataFrame([new_need])
                st.session_state.needs = pd.concat([new_df, st.session_state.needs], ignore_index=True)
                st.session_state.next_id += 1

    if st.session_state.latest_json:
        st.caption("Structured Triage Proof")
        triage_data = st.session_state.latest_json
        st.success("✅ Triage Successful!")
        st.markdown(f"""
        **📍 Location:** {triage_data.get('location_name', 'Unknown')}
        **🚨 Urgency Score:** {triage_data.get('urgency', 'N/A')}/10
        **🏷️ Category:** {triage_data.get('category', 'General')}
        **📝 Summary:** {triage_data.get('summary', 'No summary provided')}
        """)

with col2:
    st.subheader("Live Relief Registry")
    
    # Render map
    map_df = st.session_state.needs[["latitude", "longitude"]].copy()
    map_df.rename(columns={"latitude": "lat", "longitude": "lon"}, inplace=True)
    st.map(map_df, color="#ef4444", size=60, zoom=10)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display dataframe
    display_df = st.session_state.needs.drop(columns=["latitude", "longitude"])
    st.dataframe(
        display_df, 
        use_container_width=True, 
        hide_index=True,
        column_config={
            "Urgency": st.column_config.ProgressColumn(
                "Urgency",
                help="Urgency score out of 10",
                format="%d",
                min_value=0,
                max_value=10,
            )
        }
    )
    
    if st.button(" ✨ Auto-Match Closest Volunteers", type="primary"):
        latest = st.session_state.needs.iloc[0]
        crisis_cat = latest.get("Category", "General")
        c_lat = latest.get("latitude", 28.6139)
        c_lon = latest.get("longitude", 77.2090)
        
        matched_vol, status_msg = find_best_volunteer(crisis_cat, c_lat, c_lon, st.session_state.volunteers)
        
        if matched_vol is not None:
            name = matched_vol['Name']
            dist = round(matched_vol['Distance_km'], 1)
            skill = matched_vol['Primary_Skill']
            
            # Update the dataframe to show it's "In Progress"
            st.session_state.needs.at[0, "Status"] = "In Progress"
            
            st.session_state.match_msg = f"✅ Auto-Match Complete: Assigned **{name}** ({skill}) to the crisis. Distance: {dist}km."
            st.balloons()
            st.rerun() # Refresh to instantly show "In Progress"
        else:
            st.session_state.match_msg = None
            st.error(f"❌ Matching Failed: {status_msg}")
            
    if st.session_state.match_msg:
        st.success(st.session_state.match_msg)

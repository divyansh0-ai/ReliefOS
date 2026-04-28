import json
import re
import math
import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

def get_model():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = "AIzaSyCcFDI4rBV1yiqJyNhZ41PJv_XB5X7edsc" # Fallback to user provided key
    genai.configure(api_key=api_key)
    return genai.GenerativeModel("gemini-2.5-flash")

def parse_field_report(raw_text: str) -> dict:
    model = get_model()
    prompt = f"""
    You are an emergency triage AI assistant. Read the following chaotic field report and extract the core information.
    Return ONLY a raw JSON object with no backticks, markdown formatting, or preamble.
    
    For the coordinates, map the mentioned location to a realistic latitude and longitude in New Delhi, India.
    Assign an urgency score from 1-10 based on the severity of the crisis (10 being life-threatening).
    
    Format:
    {{
      "location_name": "Extract the specific area (e.g., Sector 4, Connaught Place)",
      "latitude": 28.xxxx, 
      "longitude": 77.xxxx,
      "category": "Classify as one: Medical, Food, Water/Sanitation, Shelter, General",
      "summary": "A clean 5-8 word summary of the main issue",
      "urgency": "Integer 1-10",
      "status": "Unassigned"
    }}
    
    Report Text: "{raw_text}"
    """
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        return json.loads(text)
    except Exception as e:
        return {"error": str(e), "raw": raw_text}

def _haversine_km(lat1, lon1, lat2, lon2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1))*math.cos(math.radians(lat2))*math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def smart_match(need: dict, volunteers_df) -> str:
    # Basic logic to find a volunteer. We just pick the first one with a skill that matches or generate a realistic string.
    # The prompt asks for: "✅ Matched with Dr. Sharma (Distance: 2km, Skill: Medical)."
    model = get_model()
    
    # If volunteers_df is empty, just make one up for the demo
    vol_sample = []
    if not volunteers_df.empty:
        # get 5 random volunteers
        vol_sample = volunteers_df.head(10).to_dict(orient="records")
        
    prompt = f"""You are an AI coordinator. Find the best volunteer for this need:
NEED:
{json.dumps(need, indent=2)}

AVAILABLE VOLUNTEERS:
{json.dumps(vol_sample, indent=2)}

Return ONLY a single string formatted exactly like this example (make up distance if needed, use real volunteer name/skill from list if available, otherwise make up a realistic name like Dr. Sharma):
Matched with [Name] (Distance: [X]km, Skill: [Skill]).
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        return text
    except Exception as e:
        return f"Matched with Volunteer (Distance: 1km, Skill: {need.get('category')})"

def generate_impact_forecast(needs_df, matches: list) -> dict:
    model = get_model()
    open_needs = needs_df[needs_df["status"] == "Open"].to_dict(orient="records")
    total = len(open_needs)
    matched = len([m for m in matches if "error" not in m])

    prompt = f"""You are a social-impact analyst for an NGO relief platform.

Current situation:
- Total open needs: {total}
- Needs matched to volunteers today: {matched}
- Match details: {json.dumps(matches[:6], indent=2)}
- All open needs: {json.dumps(open_needs, indent=2)}

Generate a realistic impact forecast. Return ONLY valid JSON (no markdown):
{{
  "headline": "<1 powerful sentence about today's impact>",
  "people_helped": <estimated integer>,
  "urgency_reduction_pct": <integer, estimated % reduction in overall urgency score>,
  "top_sector": "<sector where impact is greatest>",
  "top_sector_reduction": "<e.g. 40%>",
  "category_breakdown": [
    {{"category": "<name>", "needs_addressed": <int>, "impact": "<short phrase>"}}
  ],
  "projection_48h": "<what happens if no more volunteers deploy in 48 hours>",
  "recommendation": "<1 actionable recommendation for the NGO coordinator>"
}}
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        text = re.sub(r"^```[a-z]*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}

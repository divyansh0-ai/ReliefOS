import pandas as pd
import random
import os

SECTOR_COORDS = {
    "Sector 1":  (28.6448, 77.2167),
    "Sector 2":  (28.6520, 77.2300),
    "Sector 3":  (28.6390, 77.2450),
    "Sector 4":  (28.6280, 77.2100),
    "Sector 5":  (28.6610, 77.2050),
    "Sector 6":  (28.6700, 77.2250),
    "Sector 7":  (28.6350, 77.2600),
    "Sector 8":  (28.6480, 77.2700),
}

class AppState:
    def __init__(self):
        self.needs = pd.DataFrame()
        self.volunteers = pd.DataFrame()
        self.next_id = 1
        self.matches = []
        self.impact = None

state = AppState()

def load_datasets():
    disaster_path = r"C:\Users\Divyansh-PC\Desktop\solution\disaster_response_messages_test.csv"
    vol_path = r"C:\Users\Divyansh-PC\Desktop\solution\volunteer_opportunities.csv"
    
    new_needs = []
    if os.path.exists(disaster_path):
        df_disaster = pd.read_csv(disaster_path)
        if 'message' in df_disaster.columns:
            sample = df_disaster.head(30).to_dict(orient="records")
            for idx, row in enumerate(sample):
                sector = f"Sector {random.randint(1, 8)}"
                coords = SECTOR_COORDS[sector]
                lat = coords[0] + random.uniform(-0.01, 0.01)
                lon = coords[1] + random.uniform(-0.01, 0.01)
                new_needs.append({
                    "id": state.next_id + idx,
                    "location": sector,
                    "lat": lat,
                    "lon": lon,
                    "category": "Other",
                    "description": row['message'][:150] + "..." if len(row['message']) > 150 else row['message'],
                    "urgency_score": random.randint(4, 10),
                    "status": "Open",
                    "assigned_to": None
                })
            state.next_id += len(sample)
    state.needs = pd.DataFrame(new_needs)

    new_vols = []
    if os.path.exists(vol_path):
        df_vol = pd.read_csv(vol_path)
        if 'title' in df_vol.columns:
            sample = df_vol.head(30).to_dict(orient="records")
            for idx, row in enumerate(sample):
                sector = f"Sector {random.randint(1, 8)}"
                coords = SECTOR_COORDS[sector]
                lat = coords[0] + random.uniform(-0.01, 0.01)
                lon = coords[1] + random.uniform(-0.01, 0.01)
                new_vols.append({
                    "id": f"V{idx+1}",
                    "name": f"Volunteer {idx+1}",
                    "skills": [str(row['title'])[:30]],
                    "transport": random.choice(["Car", "Motorcycle", "Truck", "Bike"]),
                    "lat": lat,
                    "lon": lon,
                    "available": True,
                    "sector": sector
                })
    state.volunteers = pd.DataFrame(new_vols)

# Load data when module is imported
load_datasets()

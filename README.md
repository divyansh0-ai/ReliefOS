# 🆘 ReliefOS

**AI-Powered NGO Coordination for Real-World Crises**
*(Google Solution Challenge 2026 Entry)*

ReliefOS is an intelligent, real-time crisis management command center designed to help NGOs turn chaotic disaster reports into targeted, life-saving action. It uses advanced AI (Gemini 2.5 Flash) to instantly parse unstructured field reports, generate accurate geo-coordinates, and algorithmically match critical needs with the closest, most qualified volunteers.

---

## 🌟 Key Features

1. **Dual-Interface Architecture**:
   - A beautiful, responsive **React (Vite)** landing page for public engagement and volunteer onboarding.
   - A high-fidelity, enterprise-grade **Streamlit Command Center** tailored for NGO dispatchers.

2. **AI-Powered Triage Engine**:
   - Ingests messy, unstructured field reports (e.g., WhatsApp messages, raw radio transcriptions).
   - Utilizes **Gemini 2.5 Flash** to instantly extract specific locations, map them to exact GPS coordinates (Latitude/Longitude), classify the crisis category, and assign a 1-10 Urgency Score.

3. **Intelligent "Smart Match" Routing**:
   - Evaluates the live Relief Registry against a database of available volunteers.
   - Uses the **Haversine formula** to calculate precise geographical distances and deploys the closest volunteer with the exact required skill set (e.g., Medical, Shelter, Food).

4. **Dynamic Live Mapping**:
   - Automatically drops visual crisis pins onto a real-time geographical map the millisecond an AI extraction is completed.

---

## 🛠️ Technology Stack

- **Backend / API**: FastAPI, Uvicorn, Python
- **AI Integration**: Google Generative AI (Gemini 2.5 Flash)
- **Dispatcher Dashboard**: Streamlit, Pandas (Data Management & Geospatial Math)
- **Frontend Landing Page**: React (Vite), JavaScript, Vanilla CSS

---

## 🚀 How to Run Locally

To run the entire ReliefOS suite, you need to start three separate processes in your terminal:

### 1. Start the FastAPI Backend
Handles the core data state and API endpoints.
```bash
python -m uvicorn main:app --reload
```
*(Runs on http://localhost:8000)*

### 2. Start the React Frontend
The public-facing landing page and onboarding portal.
```bash
cd frontend
npm install
npm run dev
```
*(Runs on http://localhost:5173)*

### 3. Start the Streamlit Command Center
The dispatcher's live AI triage dashboard.
```bash
streamlit run app.py
```
*(Runs on http://localhost:8501)*

---

## 🌍 The Mission

NGOs suffer from fragmented data during disasters, which slows down volunteer mobilization and costs lives. Traditional software is too administrative and relies on slow, structured data entry. ReliefOS eliminates the bottleneck of manual data entry, enabling small NGOs to operate with the efficiency of a massive agency. Instead of spending hours logging data, they can deploy the right, skilled volunteer in seconds, ensuring resources are optimized for social good.

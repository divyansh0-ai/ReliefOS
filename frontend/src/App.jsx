import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [data, setData] = useState({ needs: [], volunteers: [], matches: [], impact: null });
  const [reportText, setReportText] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
      const res = await fetch(`${apiUrl}/data`);
      const json = await res.json();
      setData(json);
    } catch (err) {
      console.error("Error fetching data:", err);
    }
  };

  const runMatch = async () => {
    setLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
      await fetch(`${apiUrl}/match`, { method: "POST" });
      await fetchData();
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const runForecast = async () => {
    setLoading(true);
    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000/api";
      await fetch(`${apiUrl}/forecast`, { method: "POST" });
      await fetchData();
    } catch (err) {
      console.error(err);
    }
    setLoading(false);
  };

  const submitReport = async () => {
    if (!reportText) return;
    const streamlitUrl = import.meta.env.VITE_STREAMLIT_URL || "http://localhost:8501";
    // Redirect to Streamlit dashboard with the report text
    window.open(`${streamlitUrl}/?report=${encodeURIComponent(reportText)}`, '_blank');
    setReportText("");
  };

  const totalResolved = data.needs.filter(n => n.status === "Resolved").length;
  const criticalNeeds = data.needs.filter(n => n.urgency_score >= 8).length;

  return (
    <>
      <header className="navbar">
        <div className="logo">
            <span className="logo-icon">🆘</span>
            <div className="logo-text">
                <h2>ReliefOS</h2>
                <p>social good compassionate hand</p>
            </div>
        </div>
        <nav className="nav-links">
            <a href="#" className="active">Home</a>
            <a href="#about">About</a>
            <a href="#dashboard">Dashboard</a>
            <a href="#resources">Resources</a>
            <a href="#contact">Contact</a>
        </nav>
        <div className="nav-actions">
            <button className="btn btn-primary" onClick={fetchData}>Refresh Data</button>
        </div>
      </header>

      <section className="hero">
        <div className="hero-content">
            <h1>AI-Powered Triage for Real-World Crises.</h1>
            <p>ReliefOS can connect and activate people globally for NGO work, streamlining field reporting and matching.</p>
            <div className="hero-buttons">
                <button className="btn btn-primary" onClick={() => document.getElementById('dashboard').scrollIntoView()}>Get Started</button>
            </div>
        </div>
        <div className="hero-image">
            <img src="/globe.png" alt="Global connections globe" id="globe-img" />
        </div>
      </section>

      <section className="features">
        <div className="feature-card">
            <div className="feature-icon" style={{fontSize: '2rem'}}>🤖</div>
            <h3>Data Parsing</h3>
            <p>Data parsing, analysis, and active monitoring</p>
        </div>
        <div className="feature-card">
            <div className="feature-icon" style={{fontSize: '2rem'}}>🗺️</div>
            <h3>Dynamic Mapping</h3>
            <p>Connected and responsive dynamic mapping</p>
        </div>
        <div className="feature-card">
            <div className="feature-icon" style={{fontSize: '2rem'}}>🤝</div>
            <h3>Optimized Matching</h3>
            <p>Optimized merit matching for volunteers</p>
        </div>
        <div className="feature-card">
            <div className="feature-icon" style={{fontSize: '2rem'}}>📈</div>
            <h3>Impact Forecast</h3>
            <p>Impact tracking and continuous assessment</p>
        </div>
      </section>

      <section className="dashboard-preview" id="dashboard">
        <div className="preview-header">
            <h2>Live Relief Dashboard</h2>
            <p>Powered by FastAPI, React, and Gemini AI</p>
        </div>
        
        <div className="dashboard-mockup">
            <div className="mockup-sidebar">
                <div className="mockup-logo">🆘</div>
                <div className="mockup-icons">
                    <i className="fa-solid fa-home active"></i>
                    <i className="fa-solid fa-users"></i>
                    <i className="fa-solid fa-folder"></i>
                </div>
            </div>
            <div className="mockup-main">
                <div className="mockup-topbar">
                    <h3>Real-Time Triage Intelligence</h3>
                    <div className="topbar-right">
                        <button className="btn btn-primary btn-sm" onClick={runMatch} disabled={loading}>
                            {loading ? "Processing..." : "Run AI Smart Match"}
                        </button>
                        <button className="btn btn-outline btn-sm" onClick={runForecast} disabled={loading}>
                            Generate Impact Forecast
                        </button>
                    </div>
                </div>

                {data.impact && !data.impact.error && (
                    <div style={{marginBottom: 20, padding: 15, background: '#f0fdfa', borderRadius: 8, border: '1px solid #10b981'}}>
                        <h4 style={{color: '#047857'}}>🌟 {data.impact.headline}</h4>
                        <p style={{fontSize: 12, color: '#065f46'}}>{data.impact.recommendation}</p>
                    </div>
                )}

                <div className="mockup-grid">
                    <div className="mockup-map">
                        <img src="/map-mockup.png" alt="Map View" />
                    </div>
                    <div className="mockup-stats">
                        <div className="stat-box">
                            <i className="fa-solid fa-exclamation-triangle stat-icon red"></i>
                            <div className="stat-value">{criticalNeeds}</div>
                            <div className="stat-label">Critical Urgency</div>
                        </div>
                        <div className="stat-box">
                            <i className="fa-solid fa-users stat-icon blue"></i>
                            <div className="stat-value">{data.volunteers.length}</div>
                            <div className="stat-label">Available Volunteers</div>
                        </div>
                        <div className="stat-box">
                            <i className="fa-solid fa-star stat-icon yellow"></i>
                            <div className="stat-value">{data.matches.length}</div>
                            <div className="stat-label">Active AI Matches</div>
                        </div>
                        <div className="stat-box">
                            <i className="fa-solid fa-check-circle stat-icon green"></i>
                            <div className="stat-value">{totalResolved}</div>
                            <div className="stat-label">Total Resolved</div>
                        </div>
                    </div>
                </div>
                <div className="mockup-bottom">
                    <div className="mockup-table">
                        <div className="table-header">
                            <span>Needs</span>
                            <span>Urgency</span>
                            <span>Status</span>
                            <span>Location</span>
                        </div>
                        {data.needs.slice(0, 5).map((need, idx) => (
                            <div className="table-row" key={idx}>
                                <span title={need.description}>{need.description.substring(0, 30)}...</span>
                                <span className={`urgency-bar ${need.urgency_score >= 8 ? 'high' : need.urgency_score >= 5 ? 'medium' : 'low'}`} style={{width: `${need.urgency_score * 10}%`}}></span>
                                <span>{need.status}</span>
                                <span>{need.location}</span>
                            </div>
                        ))}
                    </div>
                    <div className="mockup-input">
                        <h4>Field Report Ingestion (Gemini)</h4>
                        <p>Type messy, unstructured text and let AI parse it into a structured record.</p>
                        <textarea 
                          style={{width: '100%', padding: 10, borderRadius: 6, border: '1px solid #ccc', marginBottom: 10}} 
                          rows="3" 
                          placeholder="e.g. Found a family in Sector 4 with no clean water..."
                          value={reportText}
                          onChange={(e) => setReportText(e.target.value)}
                        />
                        <button className="btn btn-primary btn-full" onClick={submitReport} disabled={loading}>
                            {loading ? "Parsing..." : "Parse with Gemini"}
                        </button>
                    </div>
                </div>
            </div>
        </div>
        <div style={{textAlign: 'center', marginTop: '40px'}}>
            <a href={import.meta.env.VITE_STREAMLIT_URL || "http://localhost:8501"} className="btn btn-primary" style={{fontSize: '18px', padding: '15px 30px', textDecoration: 'none'}} target="_blank" rel="noopener noreferrer">Explore Live Dashboard</a>
        </div>
      </section>

      <section className="about-section" id="about">
        <div className="about-text">
            <span className="section-tag">About Section</span>
            <h2>Efficiency in Compassion</h2>
            <p>During a crisis, time is the most valuable resource. ReliefOS eliminates the bottleneck of manual data entry by using advanced AI to parse chaotic field reports and instantly deploy the closest, most qualified volunteers to where they are needed most.</p>
        </div>
        <div className="about-images">
            <img src="/about-collage.png" alt="Compassionate volunteers" id="about-img" />
        </div>
      </section>

      <footer className="site-footer">
        <div className="footer-brand">
            <div className="logo">
                <span className="logo-icon">🆘</span>
                <div className="logo-text">
                    <h2>ReliefOS</h2>
                </div>
            </div>
            <p>ReliefOS: Empowering NGOs with intelligent volunteer coordination.</p>
        </div>
        <div className="footer-links">
            <div className="link-col">
                <h4>Features</h4>
                <a href="#">Home</a>
                <a href="#">Features</a>
            </div>
            <div className="link-col">
                <h4>Company</h4>
                <a href="#">About us</a>
                <a href="#">Careers</a>
            </div>
        </div>
        <div className="footer-bottom">
            <p>Clutter-free layout</p>
            <p>Copyright © ReliefOS 2026</p>
        </div>
      </footer>
    </>
  )
}

export default App

// src/pages/Home.jsx
import React from 'react';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const navigate = useNavigate();

  return (
    <div className="home-page-layout container text-center">
      
      {/* 1. Full-Screen Hero Area */}
      <div 
        style={{
          // Ensures vertical centering and full height below the navbar
          minHeight: 'calc(100vh - 70px)', 
          display: 'flex', 
          flexDirection: 'column', 
          justifyContent: 'center', 
          alignItems: 'center',
          padding: '40px 0', 
          marginBottom: '50px',
        }}
      >
        <h1 style={{fontSize: '5em', color: 'var(--primary-color)', marginBottom: '30px', fontWeight: 800}}>
          SamaajSeva
        </h1>
        <h2 style={{fontSize: '2em', color: 'var(--text-color)', maxWidth: '800px', margin: '0 auto', marginBottom: '20px'}}>
          The Web Platform to **Bridge NGOs and Community Donors**
        </h2>
        <p style={{fontSize: '1.2em', color: 'var(--text-light)', fontStyle: 'italic'}}>
          Connecting needs with resources, efficiently and transparently.
        </p>

        {/* Call to Action Button */}
        <button 
          className="primary-button" 
          style={{marginTop: '40px', padding: '18px 50px', fontSize: '1.2em', boxShadow: '0 4px 10px rgba(56, 142, 60, 0.4)'}}
          onClick={() => navigate('/auth')}
        >
          Get Started Today
        </button>
      </div>

      {/* --- 2. Feature Section (How We Help) --- */}
      <h2 style={{fontSize: '2.5em', color: 'var(--primary-color)', marginBottom: '50px', fontWeight: 700, textAlign: 'center'}}>
        Why SamaajSeva?
      </h2>
      <div className="features-section" style={{marginBottom: '80px'}}>
        
        {/* Feature 1: Visibility for NGOs */}
        <div className="feature-card">
            <span className="icon">📝</span>
            <h3 style={{fontSize: '1.4em', fontWeight: 600, color: 'var(--text-color)', marginTop: '10px'}}>Visibility for NGOs</h3>
            <p style={{marginTop: '10px', color: 'var(--text-light)'}}>
              List your urgent resource and volunteer needs to a wider network of donors.
            </p>
        </div>

        {/* Feature 2: Verified Contributions */}
        <div className="feature-card">
            <span className="icon">🤝</span>
            <h3 style={{fontSize: '1.4em', fontWeight: 600, color: 'var(--text-color)', marginTop: '10px'}}>Verified Contributions</h3>
            <p style={{marginTop: '10px', color: 'var(--text-light)'}}>
              Donors find trustworthy causes and track their commitments to ensure fulfillment.
            </p>
        </div>

        {/* Feature 3: Future AI Insights */}
        <div className="feature-card">
            <span className="icon">💡</span>
            <h3 style={{fontSize: '1.4em', fontWeight: 600, color: 'var(--text-color)', marginTop: '10px'}}>Future AI Insights</h3>
            <p style={{marginTop: '10px', color: 'var(--text-light)'}}>
              Ready for integration with ML models for seasonal prediction and urgency prioritization.
            </p>
        </div>
      </div>
      
      <footer>Empowering communities through connection.</footer>
    </div>
  );
};

export default Home;
import React from 'react';
import { Link } from 'react-router-dom';
import '../style/HomePage.css';

function HomePage() {
  return (
    <div className="home-container">
      <h1>Welcome to SkyPredict</h1>
      <p>Your weather prediction companion.</p>
      <Link to="/chat"><button>Start Chat</button></Link>
      <Link to="/about"><button>About Us</button></Link>
      
      {/* Ligne ajoutée pour accéder à la page d'administration */}
      <div className="admin-link">
        <Link to="/admin">Admin Access</Link>
      </div>
    </div>
  );
}

export default HomePage;

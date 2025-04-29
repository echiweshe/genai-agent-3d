import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import SVGGeneratorPage from './pages/SVGGeneratorPage';
import './App.css';

const HomePage = () => (
  <div className="home-page">
    <h1>GenAI Agent 3D</h1>
    <p>A comprehensive system for generating 3D content using AI</p>
    <div className="feature-cards">
      <Link to="/svg-generator" className="feature-card">
        <h2>SVG to Video Generator</h2>
        <p>Convert text descriptions to SVG diagrams and animated 3D videos</p>
      </Link>
      <div className="feature-card disabled">
        <h2>3D Model Generator</h2>
        <p>Generate 3D models from text descriptions (Coming soon)</p>
      </div>
      <div className="feature-card disabled">
        <h2>Scene Editor</h2>
        <p>Create and edit 3D scenes (Coming soon)</p>
      </div>
    </div>
  </div>
);

const NotFoundPage = () => (
  <div className="not-found-page">
    <h1>404 - Page Not Found</h1>
    <p>The page you are looking for does not exist.</p>
    <Link to="/" className="home-link">Return to Home</Link>
  </div>
);

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="app-nav">
          <div className="nav-logo">
            <Link to="/">GenAI Agent 3D</Link>
          </div>
          <ul className="nav-links">
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <Link to="/svg-generator">SVG to Video</Link>
            </li>
          </ul>
        </nav>
        
        <div className="app-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/svg-generator" element={<SVGGeneratorPage />} />
            <Route path="*" element={<NotFoundPage />} />
          </Routes>
        </div>
      </div>
    </Router>
  );
}

export default App;

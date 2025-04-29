import React from 'react';
import SVGGenerator from '../components/svg_generator';
import './SVGGeneratorPage.css';

const SVGGeneratorPage = () => {
  return (
    <div className="svg-generator-page">
      <header className="page-header">
        <h1>SVG to Video Generator</h1>
        <p>Create SVG diagrams from text descriptions and convert them to animated 3D videos</p>
      </header>
      
      <main className="page-content">
        <SVGGenerator />
      </main>
      
      <footer className="page-footer">
        <p>GenAI Agent 3D - SVG to Video Pipeline</p>
      </footer>
    </div>
  );
};

export default SVGGeneratorPage;

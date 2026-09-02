import React from 'react';
import './App.css';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to Your New Landing Page</h1>
        <p>Built automatically by Jarvis.</p>
        <button onClick={() => alert('Contact form coming soon!')}>Contact Us</button>
      </header>
    </div>
  );
}

export default App;

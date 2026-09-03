import React from 'react';
import './App.css';
import Hero from './components/Hero';
import ContactForm from './components/ContactForm';

function App() {
  return (
    <div className="App" style={{ fontFamily: 'sans-serif', maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <Hero />
      <ContactForm />
    </div>
  );
}

export default App;

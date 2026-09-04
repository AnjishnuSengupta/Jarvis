import React, { useState, useEffect, useRef } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Environment } from '@react-three/drei';
import io from 'socket.io-client';

import ArcReactorCore from './components/ArcReactorCore';
import OrbitingRings from './components/OrbitingRings';
import ParticleField from './components/ParticleField';
import VoiceWaveform from './components/VoiceWaveform';

import './App.css';

// We assume the Flask server runs on port 5000
const socket = io('http://127.0.0.1:5000');

function App() {
  const [jarvisState, setJarvisState] = useState('idle'); // idle, listening, thinking, speaking
  const [notifications, setNotifications] = useState([]);
  const [chatLog, setChatLog] = useState([]);
  const [inputText, setInputText] = useState("");

  useEffect(() => {
    // Listen for state changes from backend
    socket.on('state', (data) => {
      if (data.status) setJarvisState(data.status);
      if (data.text) {
        setChatLog((prev) => [...prev, { role: 'jarvis', text: data.text }]);
        // Revert to idle after 3 seconds of speaking
        if (data.status === 'speaking') {
          setTimeout(() => setJarvisState('idle'), 3000);
        }
      }
    });

    // Poll for notifications
    const fetchNotifications = async () => {
      try {
        const res = await fetch("http://127.0.0.1:5000/api/notifications");
        if (res.ok) {
          const data = await res.json();
          setNotifications(data.notifications || []);
        }
      } catch (err) {
        console.error("Notification polling failed");
      }
    };
    
    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);

    return () => {
      socket.off('state');
      clearInterval(interval);
    };
  }, []);

  const handleSend = async (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const userMessage = inputText;
    setInputText("");
    setChatLog((prev) => [...prev, { role: 'user', text: userMessage }]);
    setJarvisState('listening');

    try {
      const res = await fetch("http://127.0.0.1:5000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: userMessage }),
      });
      // The socket event 'state' will handle setting the state to 'thinking' and 'speaking'
      // and appending Jarvis's response to the chatlog.
    } catch (err) {
      console.error(err);
      setJarvisState('idle');
    }
  };

  return (
    <div className="hud-container">
      {/* 3D Background / Hologram */}
      <div className="canvas-container">
        <Canvas camera={{ position: [0, 0, 8], fov: 60 }}>
          <ambientLight intensity={0.5} />
          <pointLight position={[10, 10, 10]} intensity={1} />
          <Environment preset="night" />
          
          <ArcReactorCore state={jarvisState} />
          <OrbitingRings state={jarvisState} />
          <ParticleField state={jarvisState} count={1000} />
          <VoiceWaveform state={jarvisState} amplitude={0.5} />
          
          <OrbitControls enableZoom={false} enablePan={false} autoRotate autoRotateSpeed={0.5} />
        </Canvas>
      </div>

      {/* 2D Overlay Panels */}
      <div className="hud-overlay">
        <header className="hud-header">
          <h1>J.A.R.V.I.S. ONLINE</h1>
          <div className="status-indicator">
            <span className={`dot ${jarvisState}`}></span>
            {jarvisState.toUpperCase()}
          </div>
        </header>

        <main className="hud-main">
          {/* Notifications Panel */}
          <div className="panel notifications-panel">
            <h3>System Alerts</h3>
            {notifications.length === 0 ? (
              <p className="dim">No active alerts.</p>
            ) : (
              <ul>
                {notifications.map((n, i) => (
                  <li key={i}>{n.summary} - {n.time}</li>
                ))}
              </ul>
            )}
          </div>

          {/* Chat / Transcript Panel */}
          <div className="panel chat-panel">
            <div className="chat-log">
              {chatLog.map((msg, i) => (
                <div key={i} className={`chat-bubble ${msg.role}`}>
                  <span className="speaker">[{msg.role.toUpperCase()}]: </span>
                  {msg.text}
                </div>
              ))}
            </div>
            <form onSubmit={handleSend} className="chat-input-form">
              <input
                type="text"
                placeholder="Terminal input..."
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                autoFocus
              />
            </form>
          </div>
        </main>
      </div>
    </div>
  );
}

export default App;

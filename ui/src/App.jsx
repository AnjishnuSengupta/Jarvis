import { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [messages, setMessages] = useState([{ text: "Hello! I am Jarvis.", sender: "bot" }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [notifications, setNotifications] = useState([]);

  useEffect(() => {
    const fetchNotifications = async () => {
      try {
        const response = await fetch("http://127.0.0.1:5000/api/notifications");
        const data = await response.json();
        setNotifications(data.notifications || []);
      } catch (error) {
        console.error("Failed to fetch notifications:", error);
      }
    };

    fetchNotifications();
    const interval = setInterval(fetchNotifications, 30000);
    return () => clearInterval(interval);
  }, []);

  const sendMessage = async () => {
    if (!input.trim()) return;
    
    const newMessages = [...messages, { text: input, sender: "user" }];
    setMessages(newMessages);
    setInput('');
    setLoading(true);

    try {
      // Connect to the local Flask server
      const response = await fetch("http://127.0.0.1:5000/api/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input })
      });
      
      const data = await response.json();
      setMessages([...newMessages, { text: data.response, sender: "bot" }]);
    } catch (error) {
      console.error(error);
      setMessages([...newMessages, { text: "Error connecting to Jarvis backend.", sender: "bot" }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container">
      {notifications.length > 0 && (
        <div className="notifications-overlay">
          {notifications.map((note, idx) => (
            <div key={idx} className="notification-toast">
              🚨 {note}
            </div>
          ))}
        </div>
      )}
      <div className="chat-window">
        {messages.map((msg, idx) => (
          <div key={idx} className={`message-bubble ${msg.sender}`}>
            {msg.text}
          </div>
        ))}
        {loading && <div className="message-bubble bot">Thinking...</div>}
      </div>
      
      <div className="input-area">
        <input 
          type="text" 
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask Jarvis..."
        />
        <button onClick={sendMessage} disabled={loading}>Send</button>
      </div>
    </div>
  );
}

export default App;

import { useState } from 'react';
import './App.css';

interface Message {
  text: string;
  sender: 'user' | 'bot';
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');

  const handleSend = async () => {
    if (input.trim()) {
      const newMessage: Message = { text: input, sender: 'user' };
      setMessages([...messages, newMessage]);
      setInput('');

      // Envoyer le message au backend FastAPI
      const response = await fetch('http://127.0.0.1:8000/predict/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(newMessage),
      });

      const data = await response.json();

      // Ajouter les messages retournés par l'API à l'état
      setMessages(data.messages);
    }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <h1>SkyPredict</h1>
      </div>
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.sender === 'user' ? 'user' : 'bot'}`}
          >
            {msg.text}
          </div>
        ))}
      </div>
      <div className="input-container">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type a message..."
        />
        <button onClick={handleSend}>Send</button>
      </div>
    </div>
  );
}

export default App;

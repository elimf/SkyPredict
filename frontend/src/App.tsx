import { useState } from 'react';
import './App.css';
import axios from 'axios';


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
      try {
        const response = await axios.post('http://localhost:8000/predict', newMessage, {
          headers: {
            'Content-Type': 'application/json',
          },
        });
    
        console.log(response.data);
        const data = await response.data
        setMessages(data.messages);
      } catch (error) {
        console.error('Erreur lors de l\'envoi du message:', error);
      }

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

import { useState } from 'react';
import './App.css';

interface Message {
  text: string;
  sender: 'user' | 'bot';
}

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState<string>('');

  const handleSend = () => {
    if (input.trim()) {
      const newMessage: Message = { text: input, sender: 'user' };
      setMessages([...messages, newMessage]);
      setInput('');

      // Simulate a response from the bot
      setTimeout(() => {
        const botResponse: Message = { text: 'Bot: I received your message!', sender: 'bot' };
        setMessages((prevMessages) => [...prevMessages, botResponse]);
      }, 1000);
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

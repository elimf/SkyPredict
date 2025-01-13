import { useState } from 'react';
import './App.css';
import axios from 'axios';

interface Message {
  text: string;
  sender: 'user' | 'bot';
}
interface DataCity {
  city: string;
  date: string;
}
const countries = [
  { name: 'Basel', flag: '🇨🇭' },
  { name: 'Roma', flag: '🇮🇹' },
  { name: 'Germany', flag: '🇩🇪' },
  { name: 'India', flag: '🇮🇳' },
  { name: 'Japan', flag: '🇯🇵' },
];

function App() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedCountry, setSelectedCountry] = useState<string>(countries[0].name);
  const [selectedDate, setSelectedDate] = useState<string>('');

  const handleSend = async () => {
    if (selectedCountry.trim() && selectedDate) {
      const newMessage: Message = { text: `${selectedCountry} - ${selectedDate}`, sender: 'user' };
      const dataCity : DataCity = {city: selectedCountry, date: selectedDate}
      setMessages([...messages, newMessage]);
      console.log(selectedCountry + ' : ' + selectedDate)
      // Envoyer le message au backend FastAPI
      try {
        const response = await axios.post('http://localhost:8000/predict', dataCity, {
          headers: {
            'Content-Type': 'application/json',
          },
        });

        console.log(response.data);
        const data = await response.data;
        setMessages(data.messages);
      } catch (error) {
        console.error("Erreur lors de l'envoi du message:", error);
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
          <select
              value={selectedCountry}
              onChange={(e) => setSelectedCountry(e.target.value)}
              className="country-select"
          >
            {countries.map((country, index) => (
                <option key={index} value={country.name}>
                  {country.flag} {country.name}
                </option>
            ))}
          </select>
          <input
              type="date"
              value={selectedDate}
              onChange={(e) => setSelectedDate(e.target.value)}
              className="date-picker"
          />
          <button onClick={handleSend}>Send</button>
        </div>
      </div>
  );
}

export default App;
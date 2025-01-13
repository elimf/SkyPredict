import React, { useState } from 'react';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '../style/ChatPage.css';

interface Message {
  text: string;
  sender: 'user' | 'bot';
}
interface Predict {
  sender: 'user' | 'bot';
  town: string
  date: string
  model:string
}
const countries = [
  { name: 'Basel', flag: '🇨🇭' },
  { name: 'Roma', flag: '🇮🇹' },
  { name: 'Budapest', flag: '🇩🇪' },
  { name: 'India', flag: '🇮🇳' },
  { name: 'Japan', flag: '🇯🇵' },
];

const model = [
  { name: 'Prophet', flag: '📈' },
  { name: 'ForestRegressor', flag: '🌳' },
];

function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [selectedCountry, setSelectedCountry] = useState<string>(countries[0].name);
  const [selectedModel, setSelectedModel] = useState<string>(model[0].name);
  const [selectedDate, setSelectedDate] = useState<string>('');

  const handleSend = async () => {
    if (!selectedCountry.trim() || !selectedDate || !selectedModel.trim()) {
      toast.error('Veuillez remplir tous les champs avant de continuer.');
      return;
    }

    const newMessage: Message = { text: `${selectedCountry} - ${selectedDate} (${selectedModel})`, sender: 'user' };
    setMessages([...messages, newMessage]);
    const newPrediction : Predict= {town : selectedCountry, date : selectedDate, model: selectedModel, sender: 'user'}
    try {
      const response = await axios.post('http://localhost:8000/predict', newPrediction);
      const data = response.data;
      setMessages([...messages, { text: data.response, sender: 'bot' }]);
      toast.success('Prédiction réussie !');
    } catch (error) {
      console.error("Erreur lors de l'envoi du message:", error);
      toast.error('Erreur lors de la récupération de la prédiction. Veuillez réessayer.');
    }
  };

  return (
    <div className="prediction-container">
      <div className="prediction-header">
        <h1>SkyPredict</h1>
      </div>
      <div className="chat-window">
        {messages.map((msg, index) => (
          <div key={index} className={`message ${msg.sender === 'user' ? 'user' : 'bot'}`}>
            {msg.text}
          </div>
        ))}
      </div>
      <div className="action-buttons">
        <select value={selectedCountry} onChange={(e) => setSelectedCountry(e.target.value)}>
          {countries.map((country, index) => (
            <option key={index} value={country.name}>
              {country.flag} {country.name}
            </option>
          ))}
        </select>
        <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
          {model.map((mod, index) => (
            <option key={index} value={mod.name}>
              {mod.flag} {mod.name}
            </option>
          ))}
        </select>
        <input type="date" value={selectedDate} onChange={(e) => setSelectedDate(e.target.value)} />
        <button onClick={handleSend}>Send</button>
      </div>
      <ToastContainer />
    </div>
  );
}

export default ChatPage;

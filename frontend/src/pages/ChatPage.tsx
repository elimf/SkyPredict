import { useState, useEffect } from 'react';
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
  { name: 'Budapest', flag: '🇭🇺' },
  { name: 'Ljubljana', flag: '🇸🇮' },
  { name: 'Maastricht', flag: '🇳🇱' },
  { name: 'Malmo', flag: '🇸🇪' },
  { name: 'Montelimar', flag: '🇫🇷' },
  { name: 'Muenchen', flag: '🇩🇪' },
  { name: 'Oslo', flag: '🇩🇰' },
  { name: 'Perpignan', flag: '🇫🇷' },
  { name: 'Sonnblick', flag: '🇦🇹' },
  { name: 'Stockholm', flag: '🇸🇪' },
  { name: 'Tours', flag: '🇫🇷' },
  { name: 'Kassel', flag: '🇩🇪' }
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

  // Charger les messages du localStorage lors du premier rendu
  useEffect(() => {
    const storedMessages = localStorage.getItem('messages');
    if (storedMessages) {
      setMessages(JSON.parse(storedMessages));
    }
  }, []);

  // Sauvegarder les messages dans localStorage chaque fois qu'ils sont modifiés
  useEffect(() => {
    localStorage.setItem('messages', JSON.stringify(messages));
  }, [messages]);

  const handleSend = async () => {
    if (!selectedCountry.trim() || !selectedDate || !selectedModel.trim()) {
      toast.error('Veuillez remplir tous les champs avant de continuer.');
      return;
    }

    const newMessage: Message = { text: `(${selectedModel}) :Pour  ${selectedCountry} à la date suivante ${selectedDate}`, sender: 'user' };
    setMessages((prevMessages) => [...prevMessages, newMessage]);

    const newPrediction: Predict = {
      town: selectedCountry,
      date: selectedDate,
      model: selectedModel,
      sender: 'user',
    };

    try {
      const response = await axios.post('http://localhost:8000/predict', newPrediction);
      const data = response.data;
      setMessages((prevMessages) => [...prevMessages, { text: data.messages.text, sender: 'bot' }]);
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
        <button onClick={handleSend}>Predict</button>
      </div>
      <ToastContainer />
    </div>
  );
}

export default ChatPage;

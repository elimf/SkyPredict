import { useState } from 'react';
import './App.css';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

function App() {
  const [dateInput, setDateInput] = useState<string>('');
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [prediction, setPrediction] = useState<string | null>(null);

  const handlePrediction = async () => {
    if (!dateInput.trim()) {
      setErrorMessage('Veuillez sélectionner une date.');
      setPrediction(null);
      return;
    }

    setErrorMessage(null);

    try {
      const response = await axios.post(
        'http://localhost:8000/predict',
        { date: dateInput, town: "", sender: 'user' },
        { headers: { 'Content-Type': 'application/json' } }
      );
      setPrediction(response.data.prediction);
    } catch (error) {
      console.error('Erreur lors de la récupération de la prédiction:', error);
      setPrediction('Erreur lors de la récupération de la prédiction.');
    }
  };

  const handleHealthCheck = async () => {
    try {
      const response = await axios.get('http://localhost:8000/healthcheck');
      toast.success(`Health Check Status: ${response.data.status}`);
    } catch (error) {
      console.error('Erreur lors de la vérification de l\'état du serveur:', error);
      toast.error('Erreur lors de la vérification de l\'état du serveur.');
    }
  };

  const handleHealthCheckAiModel = async () => {
    try {
      const response = await axios.get('http://localhost:8000/healthcheck_ai_model');
      toast.success(`AI Model Health Check Status: ${response.data.status}`);
    } catch (error) {
      console.error('Erreur lors de la vérification de l\'état du modèle IA:', error);
      toast.error('Erreur lors de la vérification de l\'état du modèle IA.');
    }
  };

  const handleFit = async () => {
    try {
      const response = await axios.get('http://localhost:8000/fit');
      toast.success(`Model Fit: ${response.data}`);
    } catch (error) {
      console.error('Erreur lors de la mise à jour du modèle:', error);
      toast.error('Erreur lors de la mise à jour du modèle.');
    }
  };

  return (
    <div className="prediction-container">
      <header className="prediction-header">
        <h1>SkyPredict</h1>
      </header>

      <div className="input-container">
        <input type="date" value={dateInput} onChange={(e) => setDateInput(e.target.value)} />
        <button onClick={handlePrediction}>Predict</button>
      </div>

      {errorMessage && (
        <div className="error-message">
          <p>{errorMessage}</p>
        </div>
      )}

      {prediction && (
        <div className="prediction-result">
          <h2>Prediction:</h2>
          <p>{prediction}</p>
        </div>
      )}

      <div className="action-buttons">
        <button onClick={handleFit}>Fit</button>
        <button onClick={handleHealthCheck}>Health Check</button>
        <button onClick={handleHealthCheckAiModel}>AI Model Health Check</button>
      </div>

      <ToastContainer />
    </div>
  );
}

export default App;

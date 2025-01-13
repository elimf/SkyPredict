import { useState } from 'react';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '../style/AdminPage.css';


const model = [
  { name: 'Prophet', flag: '📈' },
  { name: 'ForestRegressor', flag: '🌳' },
];

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

function AdminPage() {
  const [loading, setLoading] = useState<boolean>(false);
  const [selectedModel, setSelectedModel] = useState<string>(model[0].name);
  const [selectedCountry, setSelectedCountry] = useState<string>(countries[0].name);


  // Function to handle health check
  const handleHealthCheck = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/healthcheck');
      toast.success(`Health Check Status: ${response.data.status}`);
    } catch (error) {
      console.error('Erreur lors de la vérification de l\'état du serveur:', error);
      toast.error('Erreur lors de la vérification de l\'état du serveur.');
    } finally {
      setLoading(false);
    }
  };

  // Function to handle AI model health check
  const handleHealthCheckAiModel = async () => {
    setLoading(true);
    try {
      const response = await axios.get('http://localhost:8000/healthcheck_ai_model');
      toast.success(`AI Model Health Check Status: ${response.data.status}`);
    } catch (error) {
      console.error('Erreur lors de la vérification de l\'état du modèle IA:', error);
      toast.error('Erreur lors de la vérification de l\'état du modèle IA.');
    } finally {
      setLoading(false);
    }
  };

  // Function to handle model fit
  const handleFit = async () => {
    setLoading(true);
    if(selectedModel == model[0].name){
      try {
        const response = await axios.post('http://localhost:8000/fit-prophet',{city : selectedCountry});
        toast.success(`Model Fit: ${response.data.message}`);
      } catch (error) {
        console.error('Erreur lors de la mise à jour du modèle:', error);
        toast.error('Erreur lors de la mise à jour du modèle.');
      } finally {
        setLoading(false);
      }
    }else{
      try {
        const response = await axios.post('http://localhost:8000/fit',{city : selectedCountry});
        toast.success(`Model Fit: ${response.data.message}`);
      } catch (error) {
        console.error('Erreur lors de la mise à jour du modèle:', error);
        toast.error('Erreur lors de la mise à jour du modèle.');
      } finally {
        setLoading(false);
      }
    }

  };

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
      </div>
      <div className="admin-actions">
        <select value={selectedModel} onChange={(e) => setSelectedModel(e.target.value)}>
          {model.map((mod, index) => (
              <option key={index} value={mod.name}>
                {mod.flag} {mod.name}
              </option>
          ))}
        </select>
        <select value={selectedCountry} onChange={(e) => setSelectedCountry(e.target.value)}>
          {countries.map((country, index) => (
              <option key={index} value={country.name}>
                {country.flag} {country.name}
              </option>
          ))}
        </select>
        <button onClick={handleFit} disabled={loading}>{loading ? 'Loading...' : 'Fit'}</button>
        <button onClick={handleHealthCheck} disabled={loading}>{loading ? 'Loading...' : 'Health Check'}</button>
        <button onClick={handleHealthCheckAiModel}
                disabled={loading}>{loading ? 'Loading...' : 'AI Model Health Check'}</button>
      </div>
      <div className="logs-container">
        <h2>System Logs</h2>
        {/* Placeholder for system logs */}
      </div>
      <ToastContainer/>
    </div>
  );
}

export default AdminPage;
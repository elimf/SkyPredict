import { useState } from 'react';
import axios from 'axios';
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import '../style/AdminPage.css';

function AdminPage() {
  const [loading, setLoading] = useState<boolean>(false);

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
    try {
      const response = await axios.get('http://localhost:8000/fit');
      toast.success(`Model Fit: ${response.data.message}`);
    } catch (error) {
      console.error('Erreur lors de la mise à jour du modèle:', error);
      toast.error('Erreur lors de la mise à jour du modèle.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="admin-container">
      <div className="admin-header">
        <h1>Admin Dashboard</h1>
      </div>
      <div className="admin-actions">
        <button onClick={handleFit} disabled={loading}>{loading ? 'Loading...' : 'Fit'}</button>
        <button onClick={handleHealthCheck} disabled={loading}>{loading ? 'Loading...' : 'Health Check'}</button>
        <button onClick={handleHealthCheckAiModel} disabled={loading}>{loading ? 'Loading...' : 'AI Model Health Check'}</button>
      </div>
      <div className="logs-container">
        <h2>System Logs</h2>
        {/* Placeholder for system logs */}
      </div>
      <ToastContainer />
    </div>
  );
}

export default AdminPage;
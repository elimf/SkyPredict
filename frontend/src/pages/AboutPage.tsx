import React, { useEffect, useState } from 'react';
import axios from 'axios';

function AboutPage() {
  const [loading, setLoading] = useState<boolean>(true); // Pour afficher le message de chargement
  const [explainMessage, setExplainMessage] = useState<string>(''); // Message à afficher
  const [error, setError] = useState<string | null>(null); // Pour gérer les erreurs de l'appel API

  useEffect(() => {
    // Effectuer l'appel API pour obtenir le message d'explication
    const fetchExplainMessage = async () => {
      try {
        const response = await axios.get('http://localhost:8000/explain'); // Remplacez par votre endpoint API réel
        setExplainMessage(response.data.message); // Assurez-vous que la réponse contient un champ 'message'
        setLoading(false); // Charger terminé
      } catch (error) {
        console.error("Erreur lors de la récupération du message:", error);
        setError("Erreur lors de la récupération de l'explication."); // Afficher l'erreur si l'appel échoue
        setLoading(false); // Charger terminé
      }
    };

    fetchExplainMessage();
  }, []);

  return (
    <div className="about-container">
      {loading ? (
        <div className="loading-message">
          <h2>Loading...</h2>
          <p>We are preparing everything for you...</p>
        </div>
      ) : error ? (
        <div className="error-message">
          <h2>{error}</h2>
        </div>
      ) : (
        <div className="about-content">
          <h1>About SkyPredict</h1>
          <p>{explainMessage}</p>
        </div>
      )}
    </div>
  );
}

export default AboutPage;

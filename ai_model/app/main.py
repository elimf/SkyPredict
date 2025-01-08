from fastapi import FastAPI, HTTPException
from app.schemas import PredictData
from app.data_preprocessing import data_preparation_0, data_preparation_1, extract_date_features, day_in_Life, prepare_data
from app.comet_ml_integration import load_model_from_comet, log_model_to_comet, log_metrics_to_comet
from app.models import model_pipeline
from sklearn.model_selection import train_test_split
import pandas as pd

# Création de l'application FastAPI
app = FastAPI()

@app.get("/fit")
async def fit_model():
    try:
        df = pd.read_csv("weather.csv")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Le fichier 'weather.csv' est introuvable.")
    
    # Prétraiter les données
    df = prepare_data(df, 2)
    
    # Sélectionner les features (X) et la cible (y)
    x = df[['precipitation', 'windspeed', 'pressure', 'year', 'month', 'day']]
    y = df['tempmean']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    
    # Entraîner le modèle
    model_pipeline.fit(x, y)
    
    # Enregistrer le modèle dans Comet.ml
    log_model_to_comet(model_pipeline)
        
    # Log des métriques dans Comet.ml
    log_metrics_to_comet(model_pipeline, x, y)
    
    return {"message": "Modèle entraîné et sauvegardé avec succès"}

@app.post("/predict")
async def predict(predict_data: PredictData):
    # Charger le modèle depuis Comet.ml
    model = load_model_from_comet()
    if model is None:
        raise HTTPException(status_code=404, detail="Modèle non trouvé dans Comet.ml. Entraînez d'abord le modèle.")
    
    # Convertir les données de prédiction en DataFrame
    features_df = pd.DataFrame(predict_data.features)
    
    # Faire la prédiction
    predictions = model.predict(features_df)
    
    # Log des prédictions dans Comet.ml
    log_metrics_to_comet(model, predictions=predictions)
    
    return {"predictions": predictions.tolist()}

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "L'API est opérationnelle"}

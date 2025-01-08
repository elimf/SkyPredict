from fastapi import FastAPI
from pydantic import BaseModel
import pandas as pd
import joblib

app = FastAPI()

# Charger le modèle une fois pour toute
model = joblib.load('ai_model/model.pkl')

# Définir un modèle de données pour les entrées
class Message(BaseModel):
    text: str

@app.post("/predict/")
async def predict(message: Message):
    # Convertir le message en un DataFrame Pandas
    data = pd.DataFrame([{"text": message.text}])

    # Faire une prédiction avec le modèle
    prediction = model.predict(data)

    # Retourner la prédiction
    return {"prediction": prediction[0]}

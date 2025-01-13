import logging
import sys
import os
from datetime import datetime

import httpx
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Ajouter /app au sys.path pour que les modules app soient trouvés
sys.path.append(os.path.dirname(__file__))

# Définir le modèle Message
class Message(BaseModel):
    text: str
    sender: str


class DataCity(BaseModel):
    city: str
    date: str

class PredictionData(BaseModel):
    date : datetime
    yhat: float
    yhat_lower: float
    yhat_upper: float
# Initialiser FastAPI
app = FastAPI()

allowed_origins = [
    "http://localhost",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["X-Requested-With", "Content-Type"],
)

# Définir les routes
router = APIRouter()

# Liste pour stocker les messages
messages: List[Message] = []

async def call_external_api():
    url = "http://ai_model:8001/healthcheck"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Lève une exception pour les erreurs HTTP
        return response.json()
    except httpx.RequestError as e:
        logging.error(f"Erreur de connexion à l'API externe: {e}")
        raise HTTPException(status_code=502, detail="Erreur de connexion à l'API externe")
    except httpx.HTTPStatusError as e:
        logging.error(f"Erreur HTTP depuis l'API externe: {e}")
        raise HTTPException(status_code=502, detail=f"Erreur HTTP depuis l'API externe: {e.response.status_code}")
    except Exception as e:
        logging.error(f"Erreur inattendue: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")


async def predictDatawithProphet(data : DataCity):
    url = "http://127.0.0.1:8001/predict-prophet"
    data.city = data.city.upper()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data.dict())
            response.raise_for_status()
        prediction = PredictionData(**response.json()['predictions'])
        return prediction
    except httpx.RequestError as e:
        logging.error(f"Erreur de connexion à l'API externe: {e}")
        raise HTTPException(status_code=502, detail="Erreur de connexion à l'API externe")
    except httpx.HTTPStatusError as e:
        logging.error(f"Erreur HTTP depuis l'API externe: {e}")
        raise HTTPException(status_code=502, detail=f"Erreur HTTP depuis l'API externe: {e.response.status_code}")
    except Exception as e:
        logging.error(f"Erreur inattendue: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

@router.post("/predict")
async def predict(message: Message):
    # Ajouter le message reçu à la liste
    messages.append(message)
    
    external_response = await call_external_api()
    # Simuler une réponse du bot
    bot_message = Message(text=external_response['status'], sender="bot")
    messages.append(bot_message)
    
    return {"messages": messages}

@router.post("/predict-prophet")
async def predict(data: DataCity):
    print(data)
    external_response = await call_external_api()

    predict1 = await predictDatawithProphet(data)

    # Simuler une réponse du bot
    msg = f"La température prévue pour le {predict1.date.strftime('%d/%m/%Y')} est en moyenne de {predict1.yhat:.2f}°C, avec une variation entre {predict1.yhat_lower:.2f}°C et {predict1.yhat_upper:.2f}°C."
    print(msg)
    mee = Message(text=msg, sender="bot")
    messages.append(mee)
    #bot_message = Message(text=external_response['status'], sender="bot")

    return {"messages": messages}
# Inclure les routes dans l'application FastAPI
app.include_router(router)

# Si vous souhaitez exécuter le serveur à partir de ce fichier (sans Docker par exemple),
# vous pouvez ajouter ce bloc conditionnel pour exécuter l'application avec Uvicorn en mode développement.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

import logging
import httpx
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# Définir le modèle Message
class Predict(BaseModel):
    town: str 
    sender: str 
    date: str
    model:str 
    prediction: Optional[str] = None
class DataCity(BaseModel) :
    city: str
    date: str
class PredictionData(BaseModel):
    date : date
    yhat: float
    yhat_lower: float
    yhat_upper: float

class Message(BaseModel):
    text: str
    sender: str

class TrainRequest(BaseModel):
    city: str
# Initialiser l'application FastAPI
app = FastAPI(
    title="Backend API",
    description="API pour le Chatbot",
    version="0.1",
)

# Liste des origines autorisées pour CORS
allowed_origins = [
    "http://localhost",
    "http://localhost:5173",
]

# Ajouter le middleware CORS pour autoriser les requêtes depuis les origines spécifiées
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["X-Requested-With", "Content-Type"],
)

# Définir le routeur pour les différentes routes de l'API
router = APIRouter()

async def predictRandomForest(data: DataCity):
    # Appeler directement l'API externe pour obtenir la prédiction
    url = "http://ai_model:8001/predict"
    # ! Attention: le modèle de données de l'API externe doit correspondre à celui de l'API Backend
    data.city = data.city.upper()

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data.dict())
            response.raise_for_status()  # Vérifier la réponse HTTP
            external_response = response.json()  # Extraire le JSON de la réponse
    except httpx.RequestError as e:
        logging.error(f"Erreur de connexion à l'API externe: {e}")
        raise HTTPException(status_code=502, detail="Erreur de connexion à l'API externe")
    except httpx.HTTPStatusError as e:
        logging.error(f"Erreur HTTP depuis l'API externe: {e}")
        raise HTTPException(status_code=502, detail=f"Erreur HTTP depuis l'API externe: {e.response.status_code}")
    except Exception as e:
        logging.error(f"Erreur inattendue: {e}")
        raise HTTPException(status_code=500, detail="Erreur interne du serveur")

    # Simuler la réponse du bot et l'ajouter à la liste des prédictions
    msg = f"La température prévue pour le {data.date} est en moyenne de {external_response['prediction'][0]:.2f}°C."
    print(msg)
    return Message(text=msg, sender="bot")




async def predictDatawithProphet(data : DataCity):
    url = "http://ai_model:8001/predict-prophet"
    data.city = data.city.upper()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data.dict())
            response.raise_for_status()
        predict1 = PredictionData(**response.json()['predictions'])
        msg = f"La température prévue pour le {predict1.date.strftime('%d/%m/%Y')} est en moyenne de {predict1.yhat:.2f}°C, avec une variation entre {predict1.yhat_lower:.2f}°C et {predict1.yhat_upper:.2f}°C."
        mee = Message(text=msg, sender="bot")
        return mee
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
async def predict(predict: Predict):
    if predict.model == 'Prophet':
        data_city : DataCity = DataCity(city=predict.town, date=predict.date)
        msg = await predictDatawithProphet(data_city)
        return {"messages": msg}
    else:
        data_city : DataCity = DataCity(city=predict.town, date=predict.date)
        msg = await predictRandomForest(data_city)
        return {"messages": msg}



# Route pour entraîner le modèle
@router.post("/fit")
async def training(train :TrainRequest):
    url = "http://ai_model:8001/fit"
    try:
        timeout = httpx.Timeout(connect=10.0, read=120.0, write=120.0, pool=120.0)
        train.city = train.city.upper()
        
        # Utiliser l'objet Timeout dans AsyncClient
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url,json=train.dict())
            response.raise_for_status()  # Vérifier la réponse HTTP
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


@router.post("/fit-prophet")
async def trainingProphet(train :TrainRequest):
    url = "http://ai_model:8001/fit-prophet"
    try:
        timeout = httpx.Timeout(connect=10.0, read=120.0, write=120.0, pool=120.0)
        train.city = train.city.upper()
        # Utiliser l'objet Timeout dans AsyncClient
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.post(url, json=train.dict())
            response.raise_for_status()  # Vérifier la réponse HTTP
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

# Route pour expliquer le modèle
@router.get("/explain")
async def explain():
    url = "http://ai_model:8001/explain"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Vérifier la réponse HTTP
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

# Route de vérification de l'état de l'API Backend
@app.get("/healthcheck")
async def healthcheck():
    return JSONResponse(content={"status": "L'API Backend est opérationnelle"})

# Route de vérification de l'état de l'API AI Model
@router.get("/healthcheck_ai_model")
async def healthcheck_ai_model():
    url = "http://ai_model:8001/healthcheck"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()  # Vérifier la réponse HTTP
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


# Inclure les routes dans l'application FastAPI
app.include_router(router)

# Exécution de l'application avec Uvicorn si ce fichier est exécuté directement
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

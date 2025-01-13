import logging
import httpx
from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
from datetime import date

# Définir le modèle de données pour la prédiction
class Predict(BaseModel):
    town: str 
    sender: str 
    date: date  
    prediction: Optional[str] = None

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
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["X-Requested-With", "Content-Type"],
)

# Définir le routeur pour les différentes routes de l'API
router = APIRouter()

# Liste pour stocker les prédictions effectuées
predicts: List[Predict] = []

# Route pour effectuer une prédiction
@router.post("/predict")
async def predict(predict: Predict):
    print(predict)
    # Ajouter la prédiction de l'utilisateur à la liste des prédictions
    predicts.append(predict)
    
    # Appeler directement l'API externe pour obtenir la prédiction
    url = "http://ai_model:8001/predict"
    # ! Attention: le modèle de données de l'API externe doit correspondre à celui de l'API Backend
    data = {"text": predict.text, "sender": predict.sender}
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=data)
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
    bot_predict = Predict(town=predict.town, sender="bot", date=predict.date, prediction=external_response['predictions'])
    predicts.append(bot_predict)
    
    return JSONResponse(content={"predicts": predicts})

# Route pour entraîner le modèle
@router.get("/fit")
async def training():
    url = "http://ai_model:8001/fit"
    try:
        timeout = httpx.Timeout(connect=10.0, read=120.0, write=120.0, pool=120.0)
        
        # Utiliser l'objet Timeout dans AsyncClient
        async with httpx.AsyncClient(timeout=timeout) as client:
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

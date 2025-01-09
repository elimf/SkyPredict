import logging
import sys
import os
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
    
# Initialiser FastAPI
app = FastAPI()

allowed_origins = [
    "http://localhost"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
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



@router.post("/predict")
async def predict(message: Message):
    # Ajouter le message reçu à la liste
    messages.append(message)
    
    external_response = await call_external_api()
    # Simuler une réponse du bot
    bot_message = Message(text=external_response['status'], sender="bot")
    messages.append(bot_message)
    
    return {"messages": messages}

# Inclure les routes dans l'application FastAPI
app.include_router(router)

# Si vous souhaitez exécuter le serveur à partir de ce fichier (sans Docker par exemple),
# vous pouvez ajouter ce bloc conditionnel pour exécuter l'application avec Uvicorn en mode développement.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

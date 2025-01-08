import sys
import os
from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

# Ajouter /app au sys.path pour que les modules app soient trouvés
sys.path.append(os.path.dirname(__file__))

# Définir le modèle Message
class Message(BaseModel):
    text: str
    sender: str

# Configuration de CORS
def configure_cors(app):
    origins = [
        "*", 
    ]

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Initialiser FastAPI
app = FastAPI()

# Ajouter la configuration CORS
configure_cors(app)

# Définir les routes
router = APIRouter()

# Liste pour stocker les messages
messages: List[Message] = []

@router.post("/predict")
async def predict(message: Message):
    # Ajouter le message reçu à la liste
    messages.append(message)
    
    # Simuler une réponse du bot
    bot_message = Message(text="Bot: Je suis bien reçu votre message!", sender="bot")
    messages.append(bot_message)
    
    return {"messages": messages}

# Inclure les routes dans l'application FastAPI
app.include_router(router)

# Si vous souhaitez exécuter le serveur à partir de ce fichier (sans Docker par exemple),
# vous pouvez ajouter ce bloc conditionnel pour exécuter l'application avec Uvicorn en mode développement.
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)

from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Définir les origines autorisées (ici on permet localhost:5173, où tourne votre React)
origins = [
    "http://localhost:5173",  # Frontend React (Vite)
]

# Ajouter le middleware CORS à l'application
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permet uniquement cette origine
    allow_credentials=True,
    allow_methods=["*"],  # Permet toutes les méthodes HTTP
    allow_headers=["*"],  # Permet tous les en-têtes
)

# Définir le modèle de message
class Message(BaseModel):
    text: str
    sender: str  # 'user' ou 'bot'

# Liste pour stocker les messages
messages: List[Message] = []

@app.post("/send_message/")
async def send_message(message: Message):
    # Ajouter le message reçu à la liste
    messages.append(message)
    
    # Simuler une réponse du bot
    bot_message = Message(text="Bot: Je suis bien reçu votre message!", sender="bot")
    messages.append(bot_message)
    
    return {"messages": messages}

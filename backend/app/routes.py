from fastapi import APIRouter
from app.models import Message
from typing import List

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

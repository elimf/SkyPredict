from pydantic import BaseModel
from typing import List

class PredictData(BaseModel):
    features: List[dict]  # Liste de caractéristiques pour la prédiction

# Utiliser l'image officielle de MLflow
FROM python:3.9-slim

# Mettre à jour les packages
RUN apt-get update && apt-get install -y git && apt-get clean

# Installer les dépendances de MLflow
RUN pip install --no-cache-dir mlflow[extras]

# Créer un dossier pour stocker les modèles et logs
RUN mkdir -p /mlflow/models


# Lancer le serveur MLflow
CMD mlflow ui --host 0.0.0.0 --port 5005

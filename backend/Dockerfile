# Utiliser l'image officielle de Python
FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers nécessaires dans le conteneur
COPY app/main.py /app/
COPY app/requirements.txt /app/

# Installer les dépendances
RUN pip install --no-cache-dir -r /app/requirements.txt

# Exposer le port 8000
EXPOSE 8000

# Lancer l'application avec Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

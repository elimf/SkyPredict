# SkyPredict Model IA

Ce projet constitue le model IA de l'application **SkyPredict**. Il s'agit d'un service Web basé sur **FastAPI** et **Uvicorn** pour prédire des données en temps réel.

## Prérequis

Avant de commencer, assurez-vous que vous avez Python 3.10 ou une version compatible installée sur votre machine.

Vous pouvez vérifier la version de Python avec :

```bash
python3 --version
```

Installation
1. Créer un environnement virtuel
Créez un environnement virtuel pour isoler les dépendances du projet.

```bash
python3 -m venv env
```
2. Activer l'environnement virtuel
Sur macOS/Linux :

```bash
source env/bin/activate
```
Sur Windows :

```bash
.\env\Scripts\activate
```
3. Installer les dépendances
Installez toutes les dépendances nécessaires en utilisant pip :

```bash
pip install -r app/requirements.txt
```
4. Lancer le backend
Démarrez le serveur backend avec Uvicorn pour lancer l'application en mode développement avec rechargement automatique :

``` bash
uvicorn app.main:app --reload --host 127.0.0.1 --port 8001
```
Cela démarre l'API sur http://127.0.0.1:8001 par défaut.

SkyPredict Backend © 2025 - Tous droits réservés.
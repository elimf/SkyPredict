from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import os
import pandas as pd
import numpy as np
from comet_ml import Experiment
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
from sklearn.impute import SimpleImputer
from sklearn.compose import make_column_selector
import joblib

# Configuration de Comet.ml
experiment = Experiment(
    api_key="EulD4XLfDwCGLlvfZnDzz7Bx3",
    project_name="general",
    workspace="elimf"
)

app = FastAPI()

# Définition du modèle de données pour la prédiction
class PredictData(BaseModel):
    features: List[dict]

# Sélectionner les colonnes numériques
num_selector = make_column_selector(dtype_include=np.number)

# Prétraitement des données
num_tree_processor = SimpleImputer(strategy="mean", add_indicator=True)
tree_preprocessor = make_column_transformer((num_tree_processor, num_selector))

# Création du pipeline du modèle
model_pipeline = make_pipeline(tree_preprocessor, RandomForestRegressor(n_estimators=100, random_state=42))

# Fonctions de prétraitement
def data_preparation_0(df):
    for i in df.columns:
        l = i.split("_")
        if len(l) != 1:
            if len(l) > 2:
                i1 = l[1] + l[2]
            else:
                i1 = l[1]
            i1 += "_" + l[0]
            df.rename(columns={i: i1}, inplace=True)
    return df

def data_preparation_1(df):
    df["id"] = df.index
    df_long = pd.wide_to_long(df.reset_index(), stubnames=[
        'precipitation', 'tempmean', 'tempmin',
        'tempmax', 'windspeed', 'pressure'], i=['DATE'], j='town', sep='_', suffix='.+')
    df_long.reset_index()
    df3 = df_long[['precipitation', 'tempmean', 'tempmin', 'tempmax', 'windspeed', 'pressure']]
    df3.reset_index(inplace=True)
    return df3

def extract_date_features(df):
    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m%d')
    df['year'] = df['DATE'].dt.year
    df['month'] = df['DATE'].dt.month
    df['day'] = df['DATE'].dt.day
    df = df.drop(columns='DATE')
    return df

def day_in_Life(df, number):
    for i in range(1, number + 1):
        df[[f"tempmean{i}", f"tempmax{i}"]] = df.groupby(['town'])[["tempmean", "tempmax"]].shift(i)
    return df


# Fonction pour récupérer le modèle depuis Comet.ml
def load_model_from_comet(model_name="TheModel"):
    try:
        # Récupérer le modèle depuis Comet.ml en utilisant son nom
        model = experiment.get_model(model_name)
        return model
    except Exception as e:
        print(f"Erreur lors du chargement du modèle depuis Comet.ml : {e}")
        return None

# Fonction pour enregistrer les métriques dans Comet.ml
def log_metrics_to_comet(model, x=None, y=None, predictions=None):
    if x is not None and y is not None:
        experiment.log_metric("train_score", model.score(x, y))
    if predictions is not None:
        experiment.log_metric("prediction_sample", predictions[:10].tolist())

@app.get("/fit")
async def fit_model():
    try:
        df = pd.read_csv("weather.csv")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Le fichier 'weather.csv' est introuvable.")
    print("Fichier chargé avec succès")
    # Prétraiter les données
    df = data_preparation_0(df)
    df = data_preparation_1(df)
    df = extract_date_features(df)
    df = day_in_Life(df, 2)
    
    # Sélectionner les features (X) et la cible (y)
    x = df[['precipitation', 'windspeed', 'pressure', 'year', 'month', 'day']]
    y = df['tempmean']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    
    # Entraîner le modèle
    model_pipeline.fit(x_train, y_train)
    
    # Enregistrer le modèle dans Comet.ml
    joblib.dump(model_pipeline, "model_pipeline.pkl")
    experiment.log_model("TheModel", "model_pipeline.pkl")
    # Supprimer le fichier généré après avoir loggé le modèle
    if os.path.exists("model_pipeline.pkl"):
        os.remove("model_pipeline.pkl")
        print("Fichier 'model_pipeline.pkl' supprimé avec succès.")
    else:
        print("Le fichier 'model_pipeline.pkl' n'existe pas.")  
    # Log des métriques dans Comet.ml
    log_metrics_to_comet(model_pipeline, x_test, y_test)
    
    return {"message": "Modèle entraîné et sauvegardé avec succès"}

@app.post("/predict")
async def predict(predict_data: PredictData):
    # Charger le modèle depuis Comet.ml
    model = load_model_from_comet()
    if model is None:
        raise HTTPException(status_code=404, detail="Modèle non trouvé dans Comet.ml. Entraînez d'abord le modèle.")
    
    # Convertir les données de prédiction en DataFrame
    features_df = pd.DataFrame(predict_data.features)
    
    # Faire la prédiction
    predictions = model.predict(features_df)
    
    # Log des prédictions dans Comet.ml
    log_metrics_to_comet(model, predictions=predictions)
    
    return {"predictions": predictions.tolist()}

@app.get("/healthcheck")
async def healthcheck():
    return {"status": "L'API est opérationnelle"}

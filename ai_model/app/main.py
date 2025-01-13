from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List
import os
import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
from sklearn.impute import SimpleImputer
from sklearn.compose import make_column_selector
from mlflow.models.signature import infer_signature
from mlflow.tracking import MlflowClient
import mlflow
import mlflow.sklearn
import time
from prophet import Prophet
from datetime import datetime
import joblib

app = FastAPI(
    title="AI Model API",
    description="API pour la prédiction de la température",
    version="0.1",
)

allowed_origins = [
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["X-Requested-With", "Content-Type"],
)

# Définition du modèle de données pour la prédiction
class PredictData(BaseModel):
    features: List[float]

class DataCity(BaseModel):
    city: str
    date: str

class PredictionData(BaseModel):
    date : datetime
    yhat: float
    yhat_lower: float
    yhat_upper: float
class TrainRequest(BaseModel):
    city: str
# Sélectilonner les colonnes numériques
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
    df['dayofweek_num']=df['DATE'].dt.dayofweek
    df['dayofweek_name']=df['DATE'].dt.day_name()
    #df = df.drop(columns='DATE')
    return df

def day_in_Life(df, number):
    for i in range(1, number + 1):
        df[[f"tempmean{i}", f"tempmax{i}"]] = df.groupby(['town'])[["tempmean", "tempmax"]].shift(i)
    return df

def calcul_day_since_last(date: str):
    start_date = datetime(2010, 1, 1)
    ending_date = pd.to_datetime(date, format="%Y-%m-%d")
    return (ending_date - start_date).days

def load_model_prophet(model_name="TheModel"):
    try:
        return joblib.load(model_name)
    except Exception as e:
        print(f"Erreur lors du chargement du modèle depuis Comet.ml : {e}")
        return None

@app.post("/fit")
async def fit_model(data : TrainRequest):
    mlflow.set_tracking_uri("http://mlflow:5005")
    try:
        df = pd.read_csv("weather.csv")
        if df.empty:
            raise HTTPException(status_code=400, detail="Le fichier 'weather.csv' est vide.")
    except pd.errors.ParserError:
        raise HTTPException(status_code=400, detail="Le fichier 'weather.csv' a un format incorrect.")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Le fichier 'weather.csv' est introuvable.")
    
    # Prétraiter les données
    df = data_preparation_0(df)
    df = data_preparation_1(df)
    df = extract_date_features(df)
    df = day_in_Life(df, 2)
    df_city = df[df['town'] == data.city]
    
    
    # Convertir les colonnes susceptibles de contenir des valeurs manquantes en float
    df_city[['precipitation', 'windspeed', 'pressure', 'year', 'month', 'day']] = df_city[['precipitation', 'windspeed', 'pressure', 'year', 'month', 'day']].astype('float64')
    
    # Sélectionner les colonnes numériques
    num_selector = make_column_selector(dtype_include=np.number)
    num_tree_processor = SimpleImputer(strategy="mean", add_indicator=True)
    tree_preprocessor = make_column_transformer((num_tree_processor, num_selector))

    # Création du pipeline du modèle
    model = make_pipeline(tree_preprocessor, RandomForestRegressor(n_estimators=100, random_state=42))
    
    # Sélectionner les features (X) et la cible (y)
    x = df_city[['precipitation', 'windspeed', 'pressure', 'year', 'month', 'day']]
    y = df_city['tempmean']
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)
    model_name = "model-" + data.city + '-forest'
    # Vérifier si un run est déjà actif et terminer celui-ci si nécessaire
    if mlflow.active_run():
        mlflow.end_run()
        
    # Démarrer une session MLflow
    start_time = time.time()
    with mlflow.start_run():
        # Entraîner le modèle
        model.fit(x_train, y_train)
        
        # Calculer la performance sur le test
        y_pred = model.predict(x_test)
        signature = infer_signature(x_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        score = model.score(x_test, y_test)
        
        # Enregistrer les paramètres et métriques dans MLflow
        mlflow.log_param("model_type", "RandomForestRegressor")  # Enregistrer le type de modèle
        mlflow.log_param("test_size", 0.2)  # Enregistrer la taille du test
        mlflow.log_metrics({"mse": mean_squared_error(y_test, y_pred)})
        
        # Enregistrer le modèle dans MLflow
        try:
            mlflow.sklearn.log_model(sk_model=model,artifact_path="skypredict-model", signature=signature,registered_model_name=model_name)
        except Exception as e:
            print(f"Erreur lors de l'enregistrement du modèle : {str(e)}")
        
        
        # Enregistrer la durée de l'entraînement
        mlflow.log_metric("training_duration", time.time() - start_time)
        
        # Retourner un message de succès
        return JSONResponse(content={
            "message": "Modèle entraîné et sauvegardé avec succès",
            "model_name": model_name,  # Nom du modèle
            "mse": mse,
            "score": score, 
            "training_duration": time.time() - start_time
        })


@app.post("/fit-prophet")
async def fit_prophet(data : TrainRequest):
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

    df['DATE'] = pd.to_datetime(df['DATE'], format='%Y%m%d')
    df = df.rename(columns={'DATE': 'ds', 'tempmean': 'y'})
    df_city = df[df['town'] == data.city]
    df_city = df_city[['ds', 'y', 'tempmean1',	'tempmax1',	'tempmean2','tempmax2','year','month','day', 'dayofweek_name', 'dayofweek_num']]
    df_city
    model = Prophet(changepoint_prior_scale=0.01).fit(df_city)

    model_name = "model-" + data.city + '-prophet'

    if os.path.exists(model_name):
        os.remove(model_name)
        print("Fichier "+model_name+" supprimé avec succès.")
    else:
        print("Le fichier "+model_name+" n'existe pas.")

    joblib.dump(model, model_name)

    return {"message": "Modèle entraîné et sauvegardé avec succès"}

@app.post("/predict")
async def predict(data: DataCity):    
    try:
        # Assurez-vous que les données sont sous forme de liste
        ending_date = pd.to_datetime(data.date, format="%Y-%m-%d")
        year = ending_date.year
        month = ending_date.month
        day = ending_date.day
        features_list = [5.2, 10.3, 1012, year, month, day]
        if not isinstance(features_list, list):
            raise HTTPException(status_code=400, detail="Les données de prédiction doivent être une liste.")
    except ValueError:
        raise HTTPException(status_code=400, detail="Les données de prédiction sont mal formatées.")
    
    # Connexion à MLflow (en utilisant l'URL du conteneur Docker)
    mlflow.set_tracking_uri("http://mlflow:5005")  # "mlflow" est le nom du service dans Docker Compose
    
    # Récupérer la dernière version du modèle depuis MLflow
    model_name = "model-" + data.city + '-forest'
    client = MlflowClient()
    
    # Récupérer la dernière version du modèle
    try:
        latest_version = client.get_latest_versions(model_name, stages=["None"])[-1].version
    except IndexError:
        raise HTTPException(status_code=404, detail="Aucune version de modèle trouvée.")
    
    model_uri = f"models:/{model_name}/{latest_version}"
    
    # Charger le modèle
    try:
        model = mlflow.sklearn.load_model(model_uri)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du chargement du modèle : {str(e)}")
    
    if model is None:
        raise HTTPException(status_code=404, detail="Modèle non trouvé dans MLflow. Entraînez d'abord le modèle.")
    
    # Transformer les données de prédiction en DataFrame
    features_df = pd.DataFrame([features_list], columns=["precipitation", "windspeed", "pressure", "year", "month", "day"])
    
    # Faire la prédiction
    try:
        predictions = model.predict(features_df)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la prédiction : {str(e)}")
    
    # Log des prédictions dans MLflow (facultatif)
    with mlflow.start_run():
        mlflow.log_param("input_features", features_list)  # Log des données d'entrée
        mlflow.log_metric("prediction_count", len(predictions))  # Log du nombre de prédictions
    
    # Retourner les prédictions
    return JSONResponse(content={"prediction": predictions.tolist()})

@app.post("/predict-prophet")
async def predict(data : DataCity):
    name_model = "model-" + data.city + '-prophet'
    model = load_model_prophet(model_name=name_model)
    if model is None:
        raise HTTPException(status_code=404, detail="Modèle non trouvé dans Comet.ml. Entraînez d'abord le modèle.")

    future = model.make_future_dataframe(periods=calcul_day_since_last(data.date))
    forecast = model.predict(future)
    last_row = forecast.iloc[-1]
    ds_value = last_row['ds']
    yhat_value = last_row['yhat']
    yhat_lower_value = last_row['yhat_lower']
    yhat_upper_value = last_row['yhat_upper']
    prediction_data = PredictionData(
        date=ds_value,
        yhat=yhat_value,
        yhat_lower=yhat_lower_value,
        yhat_upper=yhat_upper_value
    )
    return {"predictions": prediction_data}
@app.get("/healthcheck")
async def healthcheck():
    return JSONResponse(content={"status": "L'API du modèle est opérationnelle"})

@app.get("/explain")
async def explain():
    return JSONResponse(content={"message": "Explication de l'API"})
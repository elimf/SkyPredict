import plotly.express
import pandas as pd
from comet_ml import Experiment
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.compose import make_column_transformer
from sklearn.impute import SimpleImputer
from sklearn.compose import make_column_selector
from sklearn.ensemble import RandomForestRegressor
import joblib
import numpy as np

# Initialisation de l'expérience Comet.ml
experiment = Experiment(
    api_key="EulD4XLfDwCGLlvfZnDzz7Bx3",
    project_name="general",
    workspace="elimf"
)

# Chargement des données
df = pd.read_csv("weather.csv")

# Préparation des données
def data_preparation_0(df):
    for i in df.columns:
        l = i.split("_")
        if len(l) != 1:
            i1 = l[1] + l[2] if len(l) > 2 else l[1]
            i1 += "_" + l[0]
            df.rename(columns={i: i1}, inplace=True)
    return df

def data_preparation_1(df):
    df["id"] = df.index
    df_long = pd.wide_to_long(df.reset_index(), stubnames=['precipitation', 'tempmean', 'tempmin','tempmax','windspeed','pressure'], i=['DATE'], j='town',sep='_',suffix='.+')
    df_long.reset_index()
    df_long
    df3 = df_long[['precipitation', 'tempmean', 'tempmin','tempmax','windspeed','pressure']]
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

df = data_preparation_0(df)
df = data_preparation_1(df)
df = extract_date_features(df)
df = day_in_Life(df, 2)

# Construction du pipeline
num_selector = make_column_selector(dtype_include=np.number)
num_tree_processor = SimpleImputer(strategy="mean", add_indicator=True)
tree_preprocessor = make_column_transformer((num_tree_processor, num_selector))
reg = make_pipeline(tree_preprocessor, RandomForestRegressor(n_estimators=100, random_state=42))

# Division des données
x = df[['precipitation', 'windspeed', 'pressure', 'year', 'month', 'day']]
y = df['tempmean']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

# Entraînement du modèle
reg.fit(x_train, y_train)

# Enregistrement du modèle
# joblib.dump(reg, "reg.pkl")
experiment.log_model("TheModel", "reg.pkl")

# Évaluation du modèle
train_score = reg.score(x_train, y_train) * 100
test_score = reg.score(x_test, y_test) * 100
print("Train score:", train_score)
print("Test score:", test_score)

# Enregistrement des résultats dans Comet.ml
experiment.log_metric("Train score", train_score)
experiment.log_metric("Test score", test_score)

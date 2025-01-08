from comet_ml import Experiment

# Configuration de Comet.ml
experiment = Experiment(
    api_key="EulD4XLfDwCGLlvfZnDzz7Bx3",
    project_name="general",
    workspace="elimf"
)

# Fonction pour enregistrer le modèle dans Comet.ml
def log_model_to_comet(model):
    experiment.log_model("TheModel", model)

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

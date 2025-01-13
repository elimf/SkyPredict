# SkyProject

SkyProject est une application basée sur une architecture de microservices, comprenant des services pour le frontend, le backend, l'API du modèle, et MLflow pour le suivi des expériences de machine learning.

## Structure des Microservices

- **Frontend** : Interface utilisateur pour interagir avec l'application.
- **Backend** : Gère la logique métier et les opérations de base de données.
- **Model-API** : Fournit les endpoints pour l'inférence des modèles de machine learning.
- **MLflow** : Utilisé pour le suivi des expériences de machine learning, y compris les paramètres, les métriques et les artefacts.

## Prérequis

Assurez-vous que vous avez installé les outils suivants :

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/)

## Lancer l'application avec Docker Compose

Pour démarrer l'ensemble des services de SkyProject, suivez les étapes ci-dessous :

1. Clonez le dépôt :

   ```bash
    git clone https://github.com/votre-utilisateur/skyproject.git
    cd skyproject
   ```

2. Lancez les services avec docker-compose :

```bash 
    docker-compose up
```

Cette commande construira et démarrera tous les conteneurs définis dans le fichier docker-compose.yml.

3. Accédez à l'application :

Frontend : Ouvrez votre navigateur et allez à http://localhost:<frontend-port>
Backend API : Disponible à http://localhost:<backend-port>/api
Model-API : Points de terminaison pour l'inférence à http://localhost:<model-api-port>/predict
MLflow : Interface web accessible à http://localhost:<mlflow-port>


## Configuration

Les ports et autres configurations peuvent être personnalisés dans le fichier docker-compose.yml. Assurez-vous que les ports définis ne sont pas en conflit avec d'autres services en cours d'exécution sur votre machine.

## Arrêter les services
Pour arrêter et supprimer les conteneurs, utilisez :

```bash
    docker-compose down
```
Cela arrêtera tous les services et supprimera les réseaux et volumes créés par docker-compose.

De plus il y a les fichiers pour un aperçu de l'évolution des itérations des modèles 
``` bash
    /SkyPredict/SkyPredict.ipynb
```
On a aussi une partie sur des Scalers et PCA qu'on a tenté de mettre en place sans resultat

``` bash
    /SkyPredict/pca_scalers.ipynb
```


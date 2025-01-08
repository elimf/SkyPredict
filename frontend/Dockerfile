# Étape 1 : Construire l'application React
FROM node:18 AS build

# Définir le répertoire de travail
WORKDIR /app

# Copier package.json et package-lock.json (si disponible)
COPY package*.json ./

# Installer les dépendances
RUN npm install

# Copier tous les fichiers du frontend
COPY . .

# Construire l'application React
RUN npm run build

# Étape 2 : Serveur Nginx pour servir le contenu statique
FROM nginx:alpine

# Copier le build React depuis l'étape précédente
COPY --from=build /app/dist /usr/share/nginx/html

# Exposer le port 80 pour servir l'application
EXPOSE 80

# Lancer Nginx
CMD ["nginx", "-g", "daemon off;"]

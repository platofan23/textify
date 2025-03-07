# Dockerfile

# Basis-Image für Node.js
FROM node:18-alpine

# Arbeitsverzeichnis im Container erstellen und festlegen
WORKDIR /frontend

# Kopiere den gesamten Frontend-Ordner in das Arbeitsverzeichnis im Container
COPY ./ /frontend

# Installiere die Abhängigkeiten
RUN npm install

# Port definieren, auf dem der Vite-Server läuft
EXPOSE 5173

# Startbefehl für den Vite-Server
CMD ["npm", "run", "dev"]

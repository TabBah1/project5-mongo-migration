# 1. Image de base : Python 3.10 léger
FROM python:3.10-slim

# 2. On empêche Python de générer des fichiers .pyc et on force l'affichage des logs
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 3. Dossier de travail à l'intérieur du conteneur
WORKDIR /app

# 4. Installation des dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copie de tout ton projet dans le conteneur
COPY . .

# 6. Commande par défaut : on garde le conteneur allumé pour pouvoir lancer nos commandes
CMD ["tail", "-f", "/dev/null"]
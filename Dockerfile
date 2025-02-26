# Python Image
FROM python:3.11.9

# Arbeitsverzeichnis im Container setzen
WORKDIR /app
ENV PYTHONPATH "${PYTHONPATH}:/app"

# Kopiere den Anwendungscode in den Container
COPY . /app/

# Abhängigkeiten installieren
RUN pip install --no-cache-dir -r requirements.txt

# Setze eine Umgebungsvariable
ENV PORT 8501
ENV APP_TITLE "Movie It"
ENV DOCKER_ENV=true 

# Starte die streamlit-App direkt mit dem Python-Interpreter
CMD ["streamlit", "run", "main.py"]
# Movie-Abschlussprojekt

Unser Abschlussprojekt fuer die Data Science Weiterbildung.
Achtung!!! Reihenfolge wichtig!!!

1. Zuerst `pre-processing.py` ausfuehren, um die benoetigten .csv Dateien in Datasets zu erstellen (kann ein paar Minuten dauern).  
    Musste ausgelagert werden, da Projekt sonst zu gross fuer das verschicken gewesen waere.

2. Danach in einer Konsole der Wahl zum Projektordner navigieren.

3. Docker-Image erstellen: in der Konsole: `docker build -t movie_it .` ausfuehren.
    - Das erstellen des Images dauert etwas laenger je nach Internetverbindung und Hardwareg (bei mir 400mb/s Internetspeed, 32GB DDR5 Ram und Ryzen 7500F Prozessor, ca. 10min). Kann zu lange dauern oder fehlschlagen. In diesem Fall bitte eine virtuelle Umgebung aufbauen. Erlaeutert im Abschnitt Alternative.

4. Wenn der Build erfolgreich war, starten des Containers in der Konsole mit: `docker run -p 8501:8501 movie_it` .

5. Jetzt kann die App in einem Browser der Wahl unter `http://localhost:8501` erreicht werden.



**Alternative ueber eine Virtuelle Umgebung. In diesem Fall mit Conda und PowerShell:**

1. Es muss Conda installiert sein.

2. In der PowerShell oder einer anderen Konsole zum Projektordner navigieren. Am einfachsten ist Rechtsklick im Projektordner auf eine freie Flaeche und dann 'Open in Terminal' oder aehnliches.

3. In der Konsole `conda create -n namedesprojekts python=3.11.9`  eingeben. Das erstellt eine Conda Umgebung mit Python 3.11.9.

4. Das Environment aktivieren mit `conda activate namedesprojekts` . Das es aktiviert ist und man in der isolierten Umgebung ist sieht man daran, dass `(namedesprojekts)`  vor dem Ordnerpfad steht.
    - Falls der Aktivierungsbefehl nichts bewirkt: `conda init powershell` eingeben (Falls man mit PowerShell arbeitet). Danach die Konsole schliessen und neustarten und zum Ordner navigieren. 
        - Falls conda init PowerShell nicht funktioniert --> nur `conda init` versuchen.
        - Dann `conda activate namedesprojekts` nochmal ausfuehren um das Environment zu aktivieren.

5. Entweder ihr seht jetzt schon `(namedesprojekts)` vor dem Ordnerpfad oder ihr checkt mit `conda info --envs` ob es aktiv ist. Das seht ihr an dem Sternchen vor dem environment.

6. Jetzt sollte das environment aktiv sein. Also Zeit die Abhaengigkeiten darin zu installieren. Dazu reicht es, wenn ihr jetzt `pip install -r requirements.txt` eintippt. Warten bis alle in der Umgebung installiert sind (kann dauern, ist natuerlich wieder abhaengig von der Internetverbindung).

7. Dann pre-processing starten mit `python pre_processing.py`. Das dauert dann etwas je nach Hardware.

8. Wenn das abgeschlossen ist, die streamlit Anwendung oeffnen mit `streamlit run main.py` .

9. Geniessen


**Zum mehrmaligen ausfuehren:**
Nachdem die Dateien durch `pre_processing.py` einmal erstellt sind, kann dieser Schritt und der Schritt das Environment aufzubauen uebersprungen werden.

1. In der Konsole zum Ordner des Projektes navigieren.

2. Conda Umgebung mit `conda activate namedesprojekts` aktivieren.

3. Streamlit Anwendung mit `streamlit run main.py` starten.





**Zustaendigkeiten**:
- Initiale Idee und finden des Original Datensatzes auf Kaggle: Florian
- Visualisierungen und Visualisierungsfilter: Marc
- Filteroptionen und Filmsuche: Florian
- Filmvorschlaege: Florian
- Grundlegendes Data Cleaning: Florian
- Scrapen korrekter Nominierungen, Awards und Oscar-Nominierungen (ca. 6400 Filme): Marc
- Oscar und Award Prediction: Jiries
- Zusammenfuehren des Codes und grundlegendes Farbdesign/Startseite: Marc
- Aufbau Dockerfile und Requirements, Virtual Environment: Marc
- 
-

Vielen Dank fuers ausprobieren der App und wir hoffen, dass du einen passenden Film gefunden hast.
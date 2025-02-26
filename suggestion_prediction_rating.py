import streamlit as st
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
import time
import re


# Pipline um alle Funktionen einzubinden. Später wird NUR diese Funktion in die main.py übergeben. Debugging-Nachrichten wurden hier komplett entfernt

def run_movie_suggestion_pipeline():
    """Pipeline für die Movie Suggestions - Stufenweise Verarbeitung."""

    # 1. Funktion zum suchen von Filmen und diese in eine Liste einfügen 
    search_and_select_movies()

    # 2. Wenn Liste mit gesammelten Filem "abgesendet" werden, läuft im Hintergrund der Prozess um ähnliche Filme zu finden, welche dem Benutzer zum Bewerten später vorgeschlagen werden (anhand der Cosine-Similarity Matrix)
    if "movies_submitted" in st.session_state and st.session_state.movies_submitted:
        get_similar_movies_multi()  # Berechnet ähnliche Filme
        st.session_state.movies_submitted = False  # Zurücksetzen
        st.rerun()  # UI aktualisieren

    # 3. Sobald Liste mit ähnlichen Filmen erstellt wurde (geht eigentlich fix) werden diese Filme dem Nutzer hiermit zur Bewertung vorgeschlagen
    if "similar_movies" in st.session_state and not st.session_state.similar_movies.empty:
        get_user_ratings_streamlit()
    
    # 4. Rating Status default auf False, wird später auf True gesetzt damit die Pipeline weiter läuft
    rating_completed = st.session_state.get("rating_completed", False)
    
    # 5. Falls die Bewertung abgeschlossen wurde, starte die Skalierung der Bewertung, da die Similarity-Matrix auch mit skalierten Ratings berechnet wurde. Müssen wir erst umrechnen, um die eine Vorhersage der Ratings für unbekannte Filme zu machen, da die Vorhersagen ebenfalls auf der Similarity - Matrix basieren.
    if rating_completed:

        if "df_rated_movies" in st.session_state and not st.session_state.df_rated_movies.empty:
            scale_user_ratings()  # Aufruf der funktion welche für die Skalierung verantwortlich ist
            # Nur anzeigen, aber nicht sofort rerunnen.
            st.session_state.rating_completed = "scaled_done"  # Neues Flag setzen

        else:
            st.error("Oops, something went screenly wrong! 🎬😬")

    # 6. Wird ausgeführt wenn die Skalierung funktioniert hat. Jetzt werden unbewertete Filme gesucht, von diesen dann Ähnlichkeiten zu deinen Bekannten bzw. Bewerteten Filme berechnet und für die Filme mit hoher Ähnlichkeit eine Bewertung vorhergesagt 

    get_top_similar_unrated_movies() # Ist die Funktion die initial dafür übergeben wird

    if "scaled_rated_movies" in st.session_state:
        get_top_similar_unrated_movies() # Noch ein kleine If-Bedingung zum überprüfen. Sollte immer greifen.

    # Falls unbewertete Filme gefunden wurden, berechne gewichtete Ähnlichkeit
    if "top_unrated_movies" in st.session_state:
        compute_weighted_similarity()

    # Falls Ähnlichkeit berechnet wurde, mache Vorhersagen für unbewertete Filme, anhand des angepassten ratings
    if "similarity_sums" in st.session_state:
        predict_adjusted_ratings()

    # Falls Vorhersagen berechnet wurden, transformiere zurück auf IMDb-Skala
    if "predicted_adjusted_ratings" in st.session_state:
        transform_to_imdb_scale()

    # 7. Finale Empfehlungen als Liste anzeigen
    if "final_predictions" in st.session_state:
        
        st.markdown(
                f"""
                <div style="background-color:  #c7dafa ; padding:12px; border-radius:10px; text-align:left;">
                    <h4 style="color: #000000 ; margin: 0;">🎬 Step 3: &nbsp;&nbsp;&nbsp;&nbsp;Enjoy your movie night  </h4>
                </div>
                """,
                unsafe_allow_html=True
            )
        st.markdown("")
        st.markdown("")

        if st.button("🔄 **Reset the Movie Madness - Klick me to reset all and start again** 🔄", key="reset_rating_button_2"):
            reset_rating()
            
        st.info("🍿 Check out this table to discover new movies and see your personal predicted rating! 🍿") 

        # Sicherstellen, dass `final_predictions` existiert
        if "final_predictions" in st.session_state and not st.session_state.final_predictions.empty:
            df_predictions = st.session_state.final_predictions[["title", "predicted_rating"]].copy()
        else:
            st.error("🚨 `final_predictions` ist nicht vorhanden oder leer! Überprüfe vorherige Schritte.")
            return  # Pipeline abbrechen, falls `final_predictions` fehlt

        # Zugriff auf `df_movie_filter`, um `Rating`, `Year` & `Movie Link` zu holen und noch kleiner WorkAround für die Darstellung
        if "df_movie_filter" in st.session_state:
            df_movie_filter = st.session_state.df_movie_filter[["title", "year", "rating", "movie link"]].copy()

            # 🔥 `title_with_year` erstellen
            df_movie_filter["title_with_year"] = df_movie_filter["title"] + " (" + df_movie_filter["year"].astype(str) + ")"

            # Sicherstellen, dass `year` existiert
            if "year" not in df_predictions.columns:
                df_predictions = df_predictions.merge(df_movie_filter[["title", "year"]], on="title", how="left")

            # title_with_year erstellen
            df_predictions["title_with_year"] = df_predictions.apply(
                lambda row: f"{row['title']} ({int(row['year'])})" if pd.notna(row['year']) else row['title'],
                axis=1
            )

            # Merge mit `df_movie_filter`, um IMDb-Link & Public Rating hinzuzufügen
            df_predictions = df_predictions.merge(
                df_movie_filter[["title_with_year", "rating", "movie link"]],
                on="title_with_year",
                how="left"
            )

            # Unnötige Spalten entfernen
            df_predictions = df_predictions.drop(columns=["title", "year"], errors="ignore")

        else:
            st.warning("⚠️ `df_movie_filter` fehlt in `st.session_state`. IMDb-Links und Public Ratings können nicht angezeigt werden.")

        # Spalten umbenennen & Reihenfolge anpassen
        df_predictions = df_predictions.rename(columns={
            "title_with_year": "Title",
            "predicted_rating": "Predicted Rating",
            "rating": "Public Rating",
            "movie link": "Movie Link"
        })

        # Spalten in die gewünschte Reihenfolge bringen
        df_predictions = df_predictions[["Title", "Predicted Rating", "Public Rating", "Movie Link"]]

        # Identische Duplikate entfernen (gleicher Titel, gleiche Jahreszahl)
        df_predictions = df_predictions.drop_duplicates(subset=["Title"])

        # Falls es mehrere Einträge mit demselben Filmtitel gibt, nur den mit dem höchsten Public Rating behalten
        df_predictions["Base Title"] = df_predictions["Title"].apply(lambda x: x.rsplit(" (", 1)[0])  # Entferne die Jahreszahl für Gruppierung
        df_predictions = df_predictions.sort_values(by=["Base Title", "Public Rating"], ascending=[True, False])  # Sortiere nach Public Rating
        df_predictions = df_predictions.drop_duplicates(subset=["Base Title"], keep="first")  # Behalte nur den besten
        df_predictions = df_predictions.sort_values(by=["Public Rating"], ascending=[False])

        # Nummerierung hinzufügen
        df_predictions.insert(0, "#", range(1, len(df_predictions) + 1))

        # IMDb-Link klickbar machen
        df_predictions["Movie Link"] = df_predictions["Movie Link"].apply(
            lambda x: f'<a href="{x}" target="_blank">🔗 IMDb</a>' if pd.notna(x) else "N/A"
        )

        # Entferne die Hilfsspalte "Base Title"
        df_predictions = df_predictions.drop(columns=["Base Title"])

        # CSS für Tabelle
        custom_css = """
            <style>
                table {
                    margin-left: auto;
                    margin-right: auto;
                    border-collapse: collapse;
                    width: 100%;
                    border: 2px solid #fafabf;
                }
                th {
                    background-color: #001645 !important;  /* Dunkelblauer Header */
                    color: #fafabf !important;  /* Gelbe Schrift */
                    font-weight: bold;
                    text-transform: uppercase;
                    text-align: center !important;  /* Zentriert */
                    vertical-align: middle !important;  /* Vertikal mittig */
                    border: 2px solid #fafabf;
                    padding: 10px;  /* Gleichmäßiger Abstand */
                }
                td {
                    text-align: center !important;
                    padding: 8px;
                }
               
            </style>
        """

        # 🏆 **Finale Tabelle anzeigen**
        st.markdown(custom_css, unsafe_allow_html=True)  # CSS für zentrierte Werte
        st.markdown(df_predictions.to_html(escape=False, index=False), unsafe_allow_html=True)

# Alle Funktionen welche ich für die Pipeline benötige. Was die Funktionen machen steht immer im Doc-String, werde ich nicht weiter kommentieren. Nur die einzelnen Schritte in der Funktion, wenn diese nicht offensichtlich sind.

def reset_rating():
    """
    Setzt die gesamte Rating-Sektion zurück.
    Löscht alle gespeicherten Bewertungen, aber behält die wichtigen DataFrames.
    """
    keys_to_keep = ["df_test_similarity", "df_test_similarity_scaled", "cosine_similarity_matrix", "df_movie_filter"]
    
    # ALLE alten Bewertungen sicher löschen
    keys_to_delete = [
        "selected_movies", "rated_movies", "df_rated_movies", "adjusted_ratings",
        "similar_movies", "top_unrated_movies", "similarity_sums",
        "predicted_adjusted_ratings", "final_predictions", "df_top_movies"
    ]

    for key in keys_to_delete:
        if key in st.session_state:
            del st.session_state[key]

    # Alle anderen Keys entfernen außer die wichtigen, doppelte Absicherung
    keys_to_reset = [key for key in st.session_state.keys() if key not in keys_to_keep]

    for key in keys_to_reset:
        del st.session_state[key]

    st.rerun()  # UI neu laden


def search_and_select_movies():
    """Ermöglicht das Suchen, Auswählen und Verwalten von Filmen mit Jahreszahlen zur besseren Unterscheidung."""
    
    st.markdown("""
        <style>
        div[data-testid="stButton"] > button {
            background-color: #fafabf  !important; /* 🔥 Rot */
            color: black !important;
            font-weight: bold !important;
            border-radius: 8px !important;
            padding: 8px 20px !important;
            border: none !important;
            transition: 0.3s !important;
        }
        div[data-testid="stButton"] > button:hover {
            background-color: #CC0000 !important; /* Dunkleres Rot beim Hover */
        }
        </style>
    """, unsafe_allow_html=True)

    if st.button("🔄 **Reset the Movie Madness - Klick me to reset all and start again** 🔄", key="reset_rating_button"):
        reset_rating()

    st.markdown("---")

    st.markdown(
            f"""
            <div style="background-color:   #c7dafa ; padding:12px; border-radius:10px; text-align:left;">
                <h4 style="color: #000000 ; margin: 0;">🔍 Step 1: &nbsp;&nbsp;&nbsp;&nbsp;Search and select movies you know </h4>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("")

    # Sicherstellen, dass die Film-Liste existiert
    if "selected_movies" not in st.session_state:
        st.session_state.selected_movies = []

    # Sicherstellen, dass das Dataset geladen ist
    if "df_movie_filter" not in st.session_state:
        st.error("Oops, something went screenly wrong! DataFrame (df_movie_filter) not in session state. Plese restart the App.")
        return

    if "df_test_similarity" not in st.session_state:
        st.error("Oops, something went screenly wrong! DataFrame (df_test_similarity) not in session state. Plese restart the App.")
        return

    # Nur Filme, die auch in df_test_similarity existieren
    df_filter = st.session_state.df_movie_filter
    df_similarity = st.session_state.df_test_similarity
    df = df_filter[df_filter['title'].isin(df_similarity['title'])] # Abgleich der Filme

    search_query = st.text_input("**Type a movie title or some magical keywords and let's see if we can find the movie you're thinking of!**").strip() # Filme suchen anahnd von Titel oder Key-Words

    selected_title = None  # Standardwert für Auswahlfeld

    if search_query:
        filtered_df = df[df['title'].str.contains(search_query, case=False, na=False)] 

        if not filtered_df.empty:
            # Gruppiere Filme mit identischem Titel, aber unterschiedlichen Jahren
            title_years = filtered_df.groupby('title')['year'].apply(list).to_dict()

            # Erstelle eine Liste für das Dropdown (jedes Jahr einzeln anzeigen)
            unique_titles_with_years = sorted([
                f"{title} ({year})" for title, years in title_years.items() for year in years
            ])

            selected_title = st.selectbox("**Select a movie from the list:**", ["Select a movie..."] + unique_titles_with_years)

            if selected_title != "Select a movie...":
                match = re.match(r"^(.*?) \((\d{4})\)$", selected_title)
                if match:
                    title_only, year_only = match.groups()
                    year_only = int(year_only)

                    # Suche nach exakt passendem Film
                    matched_movie = filtered_df[
                        (filtered_df['title'] == title_only) &
                        (filtered_df['year'] == year_only)
                    ]

                    if not matched_movie.empty:
                        selected_movie = f"{title_only} ({year_only})"  # **Titel + Jahr speichern!**

                        if selected_movie not in st.session_state.selected_movies:
                            st.session_state.selected_movies.append(selected_movie)
                            st.rerun()  # UI sofort aktualisieren

    # Anzeige der ausgewählten Filme
    
    st.markdown("""
        <style>
            /* Hintergrundfarbe & Schriftfarbe der ausgewählten Elemente (Chips) */
            div[data-testid="stMultiSelect"] span {
                background-color: #001645 !important;  /* Dunkelblau */
                color: white !important;  /* Weiße Schrift */
                font-weight: bold !important;  /* Fettschrift */
                border-radius: 8px !important;  /* Abgerundete Ecken */
                padding: 5px 10px !important;  /* Abstand um den Text */
                white-space: nowrap !important;  /* Verhindert Zeilenumbrüche */
                overflow: visible !important;  /* Zeigt den gesamten Text */
                text-overflow: clip !important;  /* Kein "..." mehr */
                max-width: none !important;  /* Keine Begrenzung der Breite */
            }

            /* Farbe des "X"-Symbols im Chip */
            div[data-testid="stMultiSelect"] svg {
                fill: white !important;  /* Macht das X-Symbol weiß */
            }
        </style>
    """, unsafe_allow_html=True)

    
    if st.session_state.selected_movies:
        selected_movies = st.multiselect(
            "**Your current selections:**",
            options=st.session_state.selected_movies,
            default=st.session_state.selected_movies
        )

        # Falls ein Film entfernt wurde, aktualisiere die Liste
        if set(selected_movies) != set(st.session_state.selected_movies):
            st.session_state.selected_movies = selected_movies
            st.rerun()

        # "Submit known films"-Button (Deaktiviert, wenn keine Filme vorhanden sind)
        if st.button("👉🏾 **Klick me to go on** 👈🏾", disabled=not st.session_state.selected_movies):
            st.session_state.movies_submitted = True
            st.rerun()

    st.markdown("---")
   
def get_similar_movies_multi():
    """Berechnet eine Liste ähnlicher Filme mit Berücksichtigung von Titel + Jahr (über den Index)."""
    
    if "selected_movies" not in st.session_state or not st.session_state.selected_movies:
        st.error("Oops, something went screenly wrong! (error code: find similar movies failed)")
        return

    if "df_test_similarity_scaled" not in st.session_state or "df_test_similarity" not in st.session_state or "cosine_similarity_matrix" not in st.session_state:
        st.error("Oops, something went screenly wrong! (error code: find similar movies failed)")
        return

    # Titel + Jahreszahl aus der Session holen
    selected_movies_with_years = st.session_state.selected_movies

    # DataFrames mit allen Filmen laden
    df_scaled = st.session_state.df_test_similarity_scaled
    df_original = st.session_state.df_test_similarity  # Hier holen wir uns das Jahr
    similarity_matrix = st.session_state.cosine_similarity_matrix

    # Filme nach Titel suchen → Exakte Identifizierung über den Index!
    valid_indices = []
    for movie in selected_movies_with_years:
        match = re.match(r"^(.*?) \((\d{4})\)$", movie)
        if match:
            title_only, year_only = match.groups()
            year_only = int(year_only)

            # Finde den Index des Films in df_original
            matched_movie = df_original[
                (df_original['title'].str.lower() == title_only.lower()) & (df_original['year'] == year_only)
            ]

            if not matched_movie.empty:
                movie_index = matched_movie.index[0]  # Index des Films
                valid_indices.append(movie_index)
            else:
                st.warning(f"⚠️ '{movie}' wurde nicht im Dataset gefunden und wird ignoriert!")

    if not valid_indices:
        st.error("Oops, something went screenly wrong! Your movie taste is too unique! 😅🎥")
        return

    # Similarity-Werte holen und sortieren
    similarities = similarity_matrix[valid_indices].toarray()
    mean_similarities = np.mean(similarities, axis=0)
    similar_indices = np.argsort(mean_similarities)[::-1]

    # Nutzer-Filme rausfiltern (damit er nicht seine eigenen Filme zurückbekommt)
    similar_indices = [idx for idx in similar_indices if idx not in valid_indices]

    # Top 25 ähnliche Filme auswählen (hier kann man auch mehr einstellen)
    top_n = 25
    top_similar_movies = df_scaled.iloc[similar_indices].copy()
    top_similar_movies = top_similar_movies.iloc[:top_n].copy()
    top_similar_movies["similarity_score"] = mean_similarities[top_similar_movies.index]

    # Jahreszahl aus `df_original` holen
    top_similar_movies["year"] = df_original.loc[top_similar_movies.index, "year"].values

    # Titel + Jahr für eindeutige Anzeige
    top_similar_movies["title_with_year"] = top_similar_movies["title"] + " (" + top_similar_movies["year"].astype(str) + ")"

    # Ergebnis in `st.session_state` speichern
    st.session_state.similar_movies = top_similar_movies[['title_with_year', 'similarity_score']].reset_index(drop=True)

def get_user_ratings_streamlit():
    """
    Streamlit-Funktion zur schrittweisen Bewertung der bekannten & vorgeschlagenen Filme.
    Der Nutzer bewertet einen Film nach dem anderen durch einfaches Anklicken einer Zahl.
    """

    # Sicherstellen, dass die Bewertungs-Daten als Liste existieren
    if "rated_movies" not in st.session_state:
        st.session_state.rated_movies = []

    # Sicherstellen, dass df_rated_movies existiert, falls noch nicht
    if "df_rated_movies" not in st.session_state:
        st.session_state.df_rated_movies = pd.DataFrame(columns=["title", "rating"])

    # Sicherstellen, dass ähnliche Filme vorhanden sind
    if "similar_movies" not in st.session_state or st.session_state.similar_movies.empty:
        st.error("❌ No movies available for rating. Please select and submit known movies first.")
        return

    # Nutzer-Filme + Ähnliche Filme kombinieren
    all_movies = st.session_state.selected_movies + st.session_state.similar_movies["title_with_year"].tolist()
    total_movies = len(all_movies)
    rated_count = len(st.session_state.rated_movies)

    st.markdown(
            f"""
            <div style="background-color:   #c7dafa ; padding:12px; border-radius:10px; text-align:left;">
                <h4 style="color: #000000 ; margin: 0;">👌 Step 2: &nbsp;&nbsp;&nbsp;&nbsp;Rate your and the suggestet movies </h4>
            </div>
            """,
            unsafe_allow_html=True
        )
    
    st.markdown("")
    st.markdown("")

    st.info("**Rate the movies one by one till you finish the line or klick the button below to shorten your way.**\n\n Rating scale* \n\n ◉ &nbsp;&nbsp;&nbsp; 0 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;... 🤷‍♀️ (Don't know this movie - keep it for later) \n\n ◉ &nbsp;&nbsp;&nbsp;&nbsp;1 &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;... 🤮 (Never watch again - no films like this anymore) \n\n ◉ &nbsp;&nbsp;&nbsp;&nbsp; 5-6 &nbsp;... 😌 (Kinda ok - maybe watch again in a few years) \n\n ◉ &nbsp;&nbsp;&nbsp;&nbsp; 10 &nbsp;&nbsp;... 😍 (Love this movie - please more films like this) \n\n **Make sure you have rated at least 2-3 movies*")
    st.write("")


    current_movie = None  

    if rated_count < total_movies:
        current_movie = all_movies[rated_count]
    elif rated_count == total_movies:
    
        st.session_state.rating_completed = True

        message_box = st.empty()  # Platzhalter für die Nachrichten

        # Sofortige Nachricht
        message_box.success("✅ Rating complete or stopped! Processing your data...")

        time.sleep(3)  # Warte 3 Sekunden

        # Update auf zweite Nachricht
        message_box.success("🔍 My highly sophisticated movie radar is scanning...")

        time.sleep(5)  # Warte weitere 5 Sekunden 

        # Finale Nachricht
        message_box.success("🎬 Please wait for the next big hit – just for you...")

        # Erzeuge df_rated_movies, falls noch nicht vorhanden
        if "df_rated_movies" not in st.session_state or st.session_state.df_rated_movies.empty:
            st.session_state.df_rated_movies = pd.DataFrame(st.session_state.rated_movies)
       
        return  # Verlasse die Funktion nach der endgültigen Speicherung      
  
# Nur wenn `current_movie` definiert wurde, geht das Rating weiter
    if current_movie is not None:
        # Film-Titel zentriert und größer darstellen

        st.markdown("")

        st.markdown(
        f"""
        <div style="background-color:  #fafabf; padding: 5px; border-radius:25px; text-align:center; font-size:35px; display: flex; justify-content: center; align-items: center; gap: 00px; color: black;">
            🎥&nbsp;&nbsp; <b> '{current_movie}' </b> &nbsp;&nbsp; 🎥
        </div>
        """,
        unsafe_allow_html=True
        )

        st.markdown("")
        st.markdown("")

        rating = st.radio(
            f"Rating-Scale",
            options=[None] + list(range(11)),
            format_func=lambda x: "Select a rating" if x is None else ("0 (Don't know)" if x == 0 else str(x)),
            horizontal=True,
            key=f"rating_input_{rated_count}"
        )


    # Sobald eine Bewertung ausgewählt wird, sofort speichern
    if rating is not None and rating != "Select a rating":
        # Sicherstellen, dass die Bewertung nicht doppelt gespeichert wird
        if not any(entry["title"] == current_movie for entry in st.session_state.rated_movies):
            st.session_state.rated_movies.append({"title": current_movie, "rating": rating})
            
        # Automatisch zum nächsten Film springen
        st.rerun()  
    
    # Fortschrittsanzeige
    st.progress(rated_count / total_movies)
    st.write(f"**{rated_count}/{total_movies} movies rated**")

    if "rating_completed" in st.session_state and st.session_state.rating_completed:
            message_box = st.empty()  # 🛠 Platzhalter für die Nachrichten

            # 1️⃣ Sofortige Nachricht
            message_box.success("✅ Rating complete or stopped! Processing your data...")

            time.sleep(3)  # ⏳ Warte 2 Sekunden

            # 2️⃣ Update auf zweite Nachricht
            message_box.success("🔍 My highly sophisticated movie radar is scanning...")

            time.sleep(5)  # ⏳ Warte weitere 3 Sekunden (insgesamt 5 Sekunden)

            # 3️⃣ Finale Nachricht
            message_box.success("🎬 Please wait for the next big hit – just for you...")

            return

    # Stop Rating-Button
    if st.button("👉🏾 **Klick me to stop rating & make movie suggestions** 👈🏾", key="stop_rating_button"):
        
        # Setze `rating_completed = True`, wichtig für Schritt in der Pipeline
        st.session_state.rating_completed = True

        # Erzeuge `df_rated_movies`, falls noch nicht vorhanden
        if "df_rated_movies" not in st.session_state or st.session_state.df_rated_movies.empty:
            st.session_state.df_rated_movies = pd.DataFrame(st.session_state.rated_movies)

        st.rerun()  # Erst jetzt die UI neu laden
        return  

    st.markdown("---")
    
    # Falls bereits `rating_completed` gesetzt wurde, keine weiteren Bewertungen anzeigen. Kann glaube raus weil dürfte nie bis hier hin kommen. Kleiens Back up falls der ode nicht greift.
    if "rating_completed" in st.session_state and st.session_state.rating_completed:
        message_box = st.empty()  # Platzhalter für die Nachrichten

        # 1Sofortige Nachricht
        message_box.success("✅ Rating complete or stopped! Processing your data...")

        time.sleep(3)  # ⏳ Warte 3 Sekunden

        # Update auf zweite Nachricht
        message_box.success("🔍 My highly sophisticated movie radar is scanning...")

        time.sleep(5)  # ⏳ Warte weitere 5 Sekunden 

        # Finale Nachricht
        message_box.success("🎬 Please wait for the next big hit – just for you...")

        return
  
def scale_user_ratings():
    """
    Skaliert die Nutzerbewertungen basierend auf dem ursprünglichen öffentlichem IMDb-Rating und dem StandardScaler.
    Berechnet auch die Abweichung der Nutzerbewertung vom Public-Rating (adjusted_rating).
    Speichert das Ergebnis in `st.session_state.scaled_rated_movies`.
    """
    st.write("---")
    
    # Prüfen, ob alle notwendigen Daten vorhanden sind
    required_keys = ["rated_movies", "df_test_similarity", "df_test_similarity_scaled"]
    missing_keys = [key for key in required_keys if key not in st.session_state]

    if missing_keys:
        st.error(f"🚨 [DEBUG] Missing keys in session_state: {missing_keys}")
        return

    # Prüfen, ob die Daten leer sind
    if not st.session_state.rated_movies:
        st.error("🚨 [DEBUG] No user ratings found. Please rate some movies first.")
        return
    if st.session_state.df_test_similarity.empty or st.session_state.df_test_similarity_scaled.empty:
        st.error("🚨 [DEBUG] One of the datasets is empty! Check dataset loading.")
        return

    # Erstelle eine Kopie der Bewertungen als DataFrame
    df_rated_movies = pd.DataFrame(st.session_state.rated_movies)

    if df_rated_movies.empty:
        st.error("🚨 [DEBUG] Error: `df_rated_movies` is empty after conversion! Something went wrong.")
        return

    # Entfernen der Filme, die mit 0 bewertet wurden
    df_rated_movies = df_rated_movies[df_rated_movies['rating'] != 0] # !!!!!! absolut wichtige Zeile. 0 hat ja bedeutet man kennt die Filme nicht und nicht das es die schlechteste Bewertung ist. Daher müssen die raus. Auch aus dem Grund, dass diese Filme in der Similarity-Matrix weider gefunden werden können als Vorschläge. Das hat mich am Anfang zur Verzweiflung gebracht, weil die predicteten ratings so ******* waren

    # StandardScaler für Public Ratings anwenden
    scaler = StandardScaler()
    scaler.fit(st.session_state.df_test_similarity[['rating']])
  
    # Movie-Index hinzufügen (mit Titel + Jahr)
    df_rated_movies['movie_index'] = df_rated_movies['title'].apply(
        lambda title_with_year: (
            st.session_state.df_test_similarity.index[
                (st.session_state.df_test_similarity['title'].str.lower() == re.match(r"^(.*?) \((\d{4})\)$", title_with_year).group(1).lower()) &
                (st.session_state.df_test_similarity['year'] == int(re.match(r"^(.*?) \((\d{4})\)$", title_with_year).group(2)))
            ][0]
            if re.match(r"^(.*?) \((\d{4})\)$", title_with_year) and 
            st.session_state.df_test_similarity[
                (st.session_state.df_test_similarity['title'].str.lower() == re.match(r"^(.*?) \((\d{4})\)$", title_with_year).group(1).lower()) &
                (st.session_state.df_test_similarity['year'] == int(re.match(r"^(.*?) \((\d{4})\)$", title_with_year).group(2)))
            ].shape[0] > 0
            else None
        )
    )


    if df_rated_movies['movie_index'].isnull().any():
        st.error("🚨 Sorry. Some movies were not found in `df_test_similarity`. This App is still in progress. Contat developer team")
        return

    df_rated_movies['public_rating'] = df_rated_movies['movie_index'].apply(
        lambda idx: st.session_state.df_test_similarity.loc[idx, 'rating']
        if idx in st.session_state.df_test_similarity.index else None
    )

    if df_rated_movies['public_rating'].isnull().any():
        st.error("🚨 [DEBUG] Error: Some movies do not have a public rating! Check dataset.")
        return

    # Nutzerbewertungen skalieren (reshape für 2D-Array)
    df_rated_movies['scaled_rating'] = scaler.transform(df_rated_movies[['rating']]).flatten()

    # Skalierte Public Ratings abrufen
    df_rated_movies['scaled_public_rating'] = df_rated_movies['movie_index'].apply(
        lambda idx: st.session_state.df_test_similarity_scaled.loc[idx, 'rating']
        if idx in st.session_state.df_test_similarity_scaled.index else None
    )

    if df_rated_movies['scaled_public_rating'].isnull().any():
        st.error("🚨 [DEBUG] Error: Some movies do not have a scaled public rating! Check dataset.")
        return

    # Adjusted Rating berechnen (Differenz zwischen scaled_rating & scaled_public_rating)
    df_rated_movies['adjusted_rating'] = df_rated_movies['scaled_rating'] - df_rated_movies['scaled_public_rating']

    # Ergebnis in den Session State speichern
    st.session_state.df_rated_movies = df_rated_movies  
    
    st.session_state.adjusted_ratings = st.session_state.df_rated_movies[['movie_index', 'adjusted_rating']]

def get_top_similar_unrated_movies(top_n=100):
    """Findet unbewertete Filme mit hoher Ähnlichkeit zu bereits bewerteten Filmen."""

    if "adjusted_ratings" not in st.session_state:
        # st.error("🚨 [DEBUG] Adjusted Ratings fehlen! Starte erst die Berechnung.")
        return
    if "df_test_similarity_scaled" not in st.session_state or "cosine_similarity_matrix" not in st.session_state:
        st.error("🚨 [DEBUG] Benötigte Datensätze fehlen.")
        return

    df_movies_scaled = st.session_state.df_test_similarity_scaled
    similarity_matrix = st.session_state.cosine_similarity_matrix
    rated_indices = st.session_state.df_rated_movies['movie_index'].values

    # Unbewertete Filme finden
    unrated_indices = [i for i in range(len(df_movies_scaled)) if i not in rated_indices]
    similarity_scores = []

    for i in unrated_indices:
        sim_scores = similarity_matrix[i, rated_indices]
        avg_similarity = np.mean(sim_scores)
        similarity_scores.append((i, avg_similarity))

    similarity_scores.sort(key=lambda x: x[1], reverse=True)
    top_similar_unrated_movies = similarity_scores[:top_n]

    df_top_movies = pd.DataFrame(
        [(idx, 
        f"{df_movies_scaled.iloc[idx]['title']} ({int(df_movies_scaled.iloc[idx]['year'])})", 
        similarity) for idx, similarity in top_similar_unrated_movies],
        columns=['movie_index', 'title_with_year', 'similarity_score']
    )

    st.session_state.top_unrated_movies = df_top_movies
  
def compute_weighted_similarity():
    """Berechnet die aufsummierte Ähnlichkeit für jeden unbewerteten Film."""

    if "top_unrated_movies" not in st.session_state:
        st.error("🚨 Sorry, we have no unrated films for you. You watched all movies in the world")
        return
    if "adjusted_ratings" not in st.session_state:
        st.error("🚨 Saving your ratings failed!")
        return

    similarity_matrix = st.session_state.cosine_similarity_matrix
    rated_indices = st.session_state.df_rated_movies['movie_index'].values
    unrated_indices = st.session_state.top_unrated_movies['movie_index'].values

    similarity_sums = {i: np.sum(similarity_matrix[i, rated_indices]) for i in unrated_indices}

    st.session_state.similarity_sums = similarity_sums
    
def predict_adjusted_ratings():
    """Berechnet vorhergesagte Nutzerbewertungen für unbewertete Filme."""

    if "similarity_sums" not in st.session_state:
        st.error("🚨 Sorry, some glitch in the matrix! Restart the App.")
        return
    if "adjusted_ratings" not in st.session_state:
        st.error("🚨 Saving your ratings failed. Restart the App.")
        return

    similarity_matrix = st.session_state.cosine_similarity_matrix
    rated_indices = st.session_state.df_rated_movies['movie_index'].values
    unrated_indices = st.session_state.top_unrated_movies['movie_index'].values
    adjusted_ratings_dict = dict(zip(
        st.session_state.df_rated_movies['movie_index'],
        st.session_state.df_rated_movies['adjusted_rating']
    ))

    predicted_ratings = {}

    for i in unrated_indices:
        sim_scores = similarity_matrix[i, rated_indices]
        weighted_ratings = np.dot(sim_scores.toarray().flatten(), [adjusted_ratings_dict[j] for j in rated_indices])

        predicted_ratings[i] = weighted_ratings / st.session_state.similarity_sums[i] if st.session_state.similarity_sums[i] > 0 else 0

    st.session_state.predicted_adjusted_ratings = predicted_ratings
    
def transform_to_imdb_scale():
    """Transformiert die vorhergesagten Ratings zurück auf die IMDb-Skala und begrenzt sie auf [1, 10]."""

    if "predicted_adjusted_ratings" not in st.session_state:
        st.error("🚨 [DEBUG] Es gibt keine vorhergesagten Ratings! Führe zuerst `predict_adjusted_ratings()` aus.")
        return

    df_movies_original = st.session_state.df_test_similarity
    predictions = []

    for movie_index, adjusted_rating in st.session_state.predicted_adjusted_ratings.items():
        original_public_rating = df_movies_original.loc[movie_index, 'rating']

        # Begrenze das Rating auf den Bereich [1, 10] --> durch Rundungen könnte es sont auf 10.X gehen
        final_rating = round(min(max(adjusted_rating + original_public_rating, 1), 10), 1)
        predictions.append((movie_index, df_movies_original.loc[movie_index, 'title'], final_rating))

    df_final_predictions = pd.DataFrame(predictions, columns=['movie_index', 'title', 'predicted_rating'])
    df_final_predictions = df_final_predictions.sort_values(by='predicted_rating', ascending=False)

    st.session_state.final_predictions = df_final_predictions



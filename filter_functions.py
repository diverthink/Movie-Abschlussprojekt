import pandas as pd
import streamlit as st
import ast
import re


def search_by_title(df, search_query):
    """Filtert Filme basierend auf einer Suchanfrage mit mehreren Keywords im Titel."""
    if not search_query.strip():
        return df  # Falls kein Suchtext eingegeben wurde, gebe den gesamten DataFrame zurück

    search_query = search_query.lower()  # Kleinbuchstaben für eine case-insensitive Suche
    query_words = search_query.split()  # Zerlegt die Eingabe in einzelne Wörter

    # Filtere Filme, bei denen **alle** Suchbegriffe irgendwo im Titel vorkommen
    filtered_df = df[df['title'].str.lower().apply(lambda title: all(word in title for word in query_words))]

    return filtered_df

def search_by_title_interface(df):
    """Implementiert die Suchfunktion nach Titel mit Einklapp-Option."""
    
    st.markdown(
        f"""
        <div style="background-color:   #c7dafa ; padding:12px; border-radius:10px; text-align:left;">
            <h4 style="color: #000000 ; margin: 0;">🔍 Search for a movie by title or keyword to view details</h4>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("")

    with st.expander("**🔽 Search options**", expanded=False):

        col1, col2 = st.columns([1, 1])  # Gleichmäßige Breite für beide Spalten

        with col1:
            # ✅ Suchfeld in ein Formular packen (damit "Enter" den Button auslöst)
            with st.form(key="search_form"):
                search_query = st.text_input("⌨️ Enter movie title or keywords:")
                submit_search = st.form_submit_button("Search")

            if "filtered_df" not in st.session_state:
                st.session_state.filtered_df = None
            if "selected_movie" not in st.session_state:
                st.session_state.selected_movie = None
            if "show_details" not in st.session_state:
                st.session_state.show_details = False  # 🚀 Neuer Zustand für "Show Details"

            # ✅ Falls "Enter" gedrückt oder Button geklickt wurde → Suche ausführen
            if submit_search:
                st.session_state.filtered_df = search_by_title(df, search_query)
                st.session_state.selected_movie = None  
                st.session_state.show_details = False  # Zurücksetzen, falls eine neue Suche startet

    if st.session_state.filtered_df is not None and not st.session_state.filtered_df.empty:

        with col2:
            with st.form(key="details_form"):
                # ✅ Gruppiere Filme mit identischem Titel, aber unterschiedlichen Jahren
                title_years = st.session_state.filtered_df.groupby('title')['year'].apply(list).to_dict()

                # ✅ Erstelle eine Liste für das Dropdown (jedes Jahr einzeln anzeigen)
                unique_titles_with_years = sorted([
                    f"{title} ({year})" for title, years in title_years.items() for year in years
                ])

                # 🔽 Auswahlfeld für Filme mit Jahr
                selected_title = st.selectbox(
                    f"✅ Found {len(unique_titles_with_years)} movies:",
                    unique_titles_with_years,
                    key="selected_title_dropdown"
                )

                # ✅ Eindeutige Filmauswahl basierend auf `title` und `year`
                if selected_title:
                    match = re.match(r"^(.*?) \((\d{4})\)$", selected_title)
                    if match:
                        title_only, year_only = match.groups()
                        year_only = int(year_only)

                        # Suche nach exakt passendem Film
                        matched_movie = st.session_state.filtered_df[
                            (st.session_state.filtered_df['title'] == title_only) &
                            (st.session_state.filtered_df['year'] == year_only)
                        ]

                        if not matched_movie.empty:
                            st.session_state.selected_movie = matched_movie.iloc[0]

                # ✅ "Show details"-Button sendet das Formular
                show_details = st.form_submit_button("Show details")

        # Nach Klick auf den Button werden die Details angezeigt
        if show_details and st.session_state.selected_movie is not None:
            with st.expander("**🔽 Movie information**", expanded=True):
                st.markdown("")
                display_movie_details(st.session_state.selected_movie)

def display_movie_details(selected_movie):
    """Zeigt alle Details eines ausgewählten Films an - mit IMDb-Link, 3 strukturierten Zeilen, Trennlinien & zentrierter Formatierung."""

    # 🛠 Sicherstellen, dass 'genres', 'stars' und 'directors' immer Listen sind
    def safe_convert(value):
        """Konvertiert Strings mit Listen in echte Listen und ersetzt NaN/float durch eine leere Liste."""
        if isinstance(value, list):
            return value  # Falls bereits eine Liste → kein Problem
        elif isinstance(value, str):
            try:
                return ast.literal_eval(value)  # Falls String einer Liste → umwandeln
            except (SyntaxError, ValueError):
                return []  # Falls fehlerhafter String → leere Liste
        return []  # Falls float, NaN oder anderer Typ → leere Liste zurückgeben

    # 🎭 Genres, ⭐ Stars, 🎬 Directors sicher umwandeln
    genres = safe_convert(selected_movie.get('genres'))
    stars = safe_convert(selected_movie.get('stars'))
    directors = safe_convert(selected_movie.get('directors'))

    imdb_link = selected_movie.get('movie link', None)

    # 🎬 Film-Titelbox
    st.markdown(
        f"""
        <div style="background-color:  #fafabf; padding: 5px; border-radius:25px; text-align:center; font-size:35px; display: flex; justify-content: center; align-items: center; gap: 00px; color: black;">
            🎥&nbsp;&nbsp; <b>{selected_movie['title']}</b> &nbsp;&nbsp; 🎥
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("")
    st.markdown("<br>", unsafe_allow_html=True)  # Leerer Abstand    

    # 📌 CSS für Trennlinien zwischen Spalten
    st.markdown(
        """
        <style>
        .custom-column {
            display: flex; /* Flexbox aktivieren */
            flex-direction: column; /* Spaltenanordnung */
            align-items: center; /* Vertikale Zentrierung */
            justify-content: center; /* Inhalt mittig setzen */
            text-align: center;
            width: 100%;
            font-size: 23px;
            height: 100%; /* Damit sich die Höhe anpasst */
        }
        .separator {
            border-left: 3px solid #101435 !important;
            height: 110px;
            margin: 0px 15px !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    # 📌 CSS für zentrierte Überschriften & anpassbare Größen
    value_style = "text-align:center; font-size:25px; font-weight: bold;"  

    # 🔹 **ZEILE 1 (3 Spalten: IMDb Rating | Release Year | Duration)**
    col1, sep1, col2, sep2, col3 = st.columns([1, 0.1, 1, 0.1, 1])

    with col1:
        st.markdown(f"<p class='custom-column'>⭐ IMDb Rating ⭐</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='{value_style}'>{selected_movie['rating']} / 10</p>", unsafe_allow_html=True)

    with sep1:
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

    with col2:
        st.markdown(f"<p class='custom-column'>📅 Release Year 📅</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='{value_style}'>{selected_movie['year']}</p>", unsafe_allow_html=True)

    with sep2:
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

    with col3:
        st.markdown(f"<p class='custom-column'>⏳ Duration ⏳</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='{value_style}'>{int(selected_movie['duration'])} min</p>" if not pd.isna(selected_movie['duration']) else "<p style='{value_style}'>N/A</p>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown("")
    st.markdown(
        f"""
        <div style="background-color:  #101435; padding:1.5px; border-radius:25px; text-align:center; font-size:1px; display: flex; justify-content: center; align-items: center; gap: 00px; color: black;">
            &nbsp; 
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("")
    st.markdown("")

    # 🔹 **ZEILE 2 (Genres | Stars | Directors)**
    col_left, sep3, col_middle, sep4, col_right = st.columns([1, 0.1, 1, 0.1, 1])

    with col_left:
        st.markdown(f"<p class='custom-column'>🎭 Genres 🎭</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='{value_style}'>{' | '.join(genres)}</p>" if genres else "<p style='{value_style}'>Not specified</p>", unsafe_allow_html=True)

    with sep3:
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

    with col_middle:
        st.markdown(f"<p class='custom-column'>👨‍👩‍👧‍👦 Stars 👨‍👩‍👧‍👦</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='{value_style}'>{' | '.join(stars)}</p>" if stars else "<p style='{value_style}'>Not specified</p>", unsafe_allow_html=True)

    with sep4:
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

    with col_right:
        st.markdown(f"<p class='custom-column'>🎬 Directors 🎬</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='{value_style}'>{' | '.join(directors)}</p>" if directors else "<p style='{value_style}'>Not specified</p>", unsafe_allow_html=True)

    st.markdown("")
    st.markdown(
        f"""
        <div style="background-color:  #101435; padding: 1.5px; border-radius:25px; text-align:center; font-size:1px; display: flex; justify-content: center; align-items: center; gap: 00px; color: black;">
            &nbsp; 
        </div>
        """,
        unsafe_allow_html=True
    )
    st.markdown("")
    st.markdown("")

    # 🔹 **ZEILE 3 (Audience Suitability | Leer | Leer)**
    col_a, sep5, col_b, sep6, col_c = st.columns([1, 0.1, 1, 0.1, 1])

    with col_a:
        st.markdown(f"<p class='custom-column'>🎟️ Audience Suitability 🎟️</p>", unsafe_allow_html=True)
        st.markdown(f"<p style='{value_style}'>{selected_movie.get('mpa_category', 'Unknown')}</p>", unsafe_allow_html=True)

    with sep5:
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)
    
    with col_b:
        st.markdown(f"<p class='custom-column'>ℹ️ More Inoformation ℹ️</p>", unsafe_allow_html=True)  # Überschrift mit Icons

        imdb_button = f"""
        <div style="display: flex; justify-content: center; align-items: center; height: 100%;">
            <a href="{imdb_link}" target="_blank" style="text-decoration:none;">
                <button style="background-color:#204991; color:#fafabf; padding:3px 12px; font-size:25px; font-weight:bold; border:none; border-radius:8px; cursor:pointer;">
                    Klick me for IMDb Page
                </button>
            </a>
        </div>
        """
        st.markdown(imdb_button, unsafe_allow_html=True)

    with sep6:
        st.markdown("")

    with col_c:
        st.markdown("")

    st.markdown("")
    st.markdown("")
    st.markdown("")
  
def search_by_criteria_interface(df):
    """Implementiert die Filterfunktion nach Kriterien."""
    
    st.markdown(
            f"""
            <div style="background-color:   #c7dafa ; padding:12px; border-radius:10px; text-align:left;">
                <h4 style="color: #000000 ; margin: 0;">🔍 Search for movies based on specific criteria and get a list of matching films</h4>
            </div>
            """,
            unsafe_allow_html=True
        )
    st.markdown("")

    with st.expander("**🔽 Filter options**", expanded=False):
        st.markdown("")
        st.markdown("")
        
        st.markdown(
        f"""
        <div style="background-color:  #fafabf; padding: 5px; border-radius:20px; text-align:center; font-size:35px; display: flex; justify-content: center; align-items: center; gap: 00px; color: black;">
            🎞️ Filter movies based on various criteria 🎞️
        </div>
        """,
        unsafe_allow_html=True
        )    

        st.markdown("")
        st.markdown("")
        st.markdown("")

        # Zeile 1: Year, Duration, Rating
        col1, col2, col3 = st.columns(3, gap="large")

        with col1:
            st.markdown(
                """
                <div style="background-color: #001645; padding: 2px; border-radius: 15px; 
                            text-align: center; font-size: 25px; font-weight: bold; color: white;">
                    Year
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("")
            year_min, year_max = int(df['year'].min()), int(df['year'].max())
            year_range = st.slider(
                "▪️ Select Year Range\n\n &nbsp; ", 
                year_min, year_max, 
                (year_min, year_max)
            )
            

        with col2:
            st.markdown(
                """
                <div style="background-color: #001645; padding: 2px; border-radius: 15px; 
                            text-align: center; font-size: 25px; font-weight: bold; color: white;">
                    Duration
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("")
            duration_min, custom_max = 0, 300  # Sichtbare Obergrenze
            duration_range = st.slider(
                "▪️ Select duration range (minutes)\n\n &nbsp;",
                duration_min,
                custom_max,
                (duration_min, custom_max),
                help="Drag to filter to max (300), to include all longer movies."
            )

        with col3:
            st.markdown(
                """
                <div style="background-color: #001645; padding: 2px; border-radius: 15px; 
                            text-align: center; font-size: 25px; font-weight: bold; color: white;">
                    Rating (IMDb)
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("")
            rating_min, rating_max = 0.0, 10.0
            rating_range = st.slider(
                "▪️ Select rating range\n\n &nbsp;", 
                rating_min, rating_max, 
                (rating_min, rating_max)
            )
        
        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown("")
        
        st.markdown(
        f"""
        <div style="background-color:  #101435; padding:0.5px; border-radius:25px; text-align:center; font-size:1px; display: flex; justify-content: center; align-items: center; gap: 00px; color: black;">
            &nbsp; 
        </div>
        """,
        unsafe_allow_html=True
        )

        st.markdown("")
        st.markdown("")
        st.markdown("")
        

        # Zeile 2: Genres, MPA Rating
        col4, col5 = st.columns(2, gap="large")

        with col4:
            st.markdown(
                """
                <div style="background-color: #001645; padding: 2px; border-radius: 15px; 
                            text-align: center; font-size: 25px; font-weight: bold; color: white;">
                    Genres
                </div>
                """,
                unsafe_allow_html=True
            )

            st.markdown("")
            st.markdown("")
            st.markdown("")
        
            # Sicherstellen, dass 'genres' echte Listen sind
            df['genres'] = df['genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

            # Alle einzigartigen Genres sammeln
            genre_categories = sorted(set(genre for genres in df['genres'].dropna() for genre in genres))

            # Multiselect für Genres
            selected_genres = st.multiselect(
                "▪️ Select genres", 
                genre_categories
            )



        with col5:
            st.markdown(
                """
                <div style="background-color: #001645; padding: 2px; border-radius: 15px; 
                            text-align: center; font-size: 25px; font-weight: bold; color: white;">
                    Audience Suitability
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("")   
            st.markdown("")
            st.markdown("")         
                        
            # Alle einzigartigen MPA-Kategorien direkt aus der Spalte holen
            mpa_categories = sorted(df['mpa_category'].dropna().unique())
            
            # Multiselect-Widget mit diesen Kategorien
            selected_mpa = st.multiselect(
                "▪️ Select age categories", 
                mpa_categories
            )


        st.markdown("")
        st.markdown("")
        st.markdown("")
        
        st.markdown(
        f"""
        <div style="background-color:  #101435; padding:0.5px; border-radius:25px; text-align:center; font-size:1px; display: flex; justify-content: center; align-items: center; gap: 00px; color: black;">
            &nbsp; 
        </div>
        """,
        unsafe_allow_html=True
        )
        st.markdown("")
        st.markdown("")
        st.markdown("")

        # Sicherstellen, dass Session State-Variablen existieren
        if "saved_stars" not in st.session_state:
            st.session_state.saved_stars = []
        if "saved_directors" not in st.session_state:
            st.session_state.saved_directors = []
        if "star_search_input" not in st.session_state:
            st.session_state.star_search_input = ""
        if "director_search_input" not in st.session_state:
            st.session_state.director_search_input = ""

        # Zeile 3: Stars, Directors
        col6, col7 = st.columns(2, gap="large")

        with col6:
            st.markdown(
                """
                <div style="background-color: #001645; padding: 2px; border-radius: 15px; 
                            text-align: center; font-size: 25px; font-weight: bold; color: white;">
                    Stars
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("")    
            st.markdown("")
            st.markdown("")
      
            
            # 1️⃣ Suchfeld für Namen (Feld 1)
            star_search = st.text_input(
                "▪️ Enter star name", 
                value=st.session_state.star_search_input, 
                key="star_search_box"
                )

            # 2️⃣ Dropdown mit Vorschlägen (Feld 2)
            all_stars = sorted(set(star.strip() for stars in df['stars'].dropna() for star in eval(stars)))
            possible_stars = [star for star in all_stars if star_search.lower() in star.lower()] if star_search else []

            st.markdown("")
            st.markdown("")
            selected_star = st.selectbox("▪️ Select from search results", [""] + possible_stars, index=0, key="star_selectbox")

            # ✅ Falls ein Star in der Dropdown-Liste ausgewählt wird → Direkt zur Liste hinzufügen!
            if selected_star and selected_star not in st.session_state.saved_stars:
                st.session_state.saved_stars.append(selected_star)

            # 3️⃣ Darstellung als klickbare Chips
            st.markdown("""
                <style>
                    /* Hintergrundfarbe & Schriftfarbe der ausgewählten Elemente (Chips) */
                    div[data-testid="stMultiSelect"] span {
                        background-color: #001645 !important;  /* Dunkelblau */
                        color: white !important;  /* Weiße Schrift */
                        font-weight: bold !important;  /* Fettschrift */
                        border-radius: 8px !important;  /* Abgerundete Ecken */
                        padding: 5px 10px !important;  /* Abstand um den Text */
                    }

                    /* Farbe des "X"-Symbols im Chip */
                    div[data-testid="stMultiSelect"] svg {
                        fill: white !important;  /* Macht das X-Symbol weiß */
                    }
                </style>
            """, unsafe_allow_html=True)
            st.markdown("")


            if st.session_state.saved_stars:
                remove_star = st.multiselect("▪️ Selected Stars", options=st.session_state.saved_stars, default=st.session_state.saved_stars, key="remove_star_multiselect")
                st.session_state.saved_stars = remove_star  # Aktualisierung der Liste

        with col7:
            st.markdown(
                """
                <div style="background-color: #001645; padding: 2px; border-radius: 15px; 
                            text-align: center; font-size: 25px; font-weight: bold; color: white;">
                    Directors
                </div>
                """,
                unsafe_allow_html=True
            )
            st.markdown("")         
            st.markdown("")
            st.markdown("")   
           
            # 1️⃣ Suchfeld für Namen (Feld 1)
            director_search = st.text_input(
                "▪️ Enter director name", 
                value=st.session_state.director_search_input, 
                key="director_search_box"
            )

            # 2️⃣ Dropdown mit Vorschlägen (Feld 2)
            all_directors = sorted(set(director.strip() for directors in df['directors'].dropna() for director in eval(directors)))
            possible_directors = [director for director in all_directors if director_search.lower() in director.lower()] if director_search else []

            st.markdown("")
            st.markdown("")

            selected_director = st.selectbox("▪️ Select from search results", [""] + possible_directors, index=0, key="director_selectbox")

            st.markdown("")
            st.markdown("")

            # ✅ Falls ein Director in der Dropdown-Liste ausgewählt wird → Direkt zur Liste hinzufügen!
            if selected_director and selected_director not in st.session_state.saved_directors:
                st.session_state.saved_directors.append(selected_director)

            # 3️⃣ Darstellung als klickbare Chips (wie in Genres)
            if st.session_state.saved_directors:
                remove_director = st.multiselect("▪️ Selected Directors", options=st.session_state.saved_directors, default=st.session_state.saved_directors, key="remove_director_multiselect")
                st.session_state.saved_directors = remove_director  # Aktualisierung der Liste

        st.markdown("")
        st.markdown("")
        st.markdown("")
        st.markdown(
        f"""
        <div style="background-color:  #101435; padding:0.5px; border-radius:25px; text-align:center; font-size:1px; display: flex; justify-content: center; align-items: center; gap: 00px; color: black;">
            &nbsp; 
        </div>
        """,
        unsafe_allow_html=True
        )
        st.markdown("") 
        st.markdown("") 
    

        # Anwenden der Filter
        
        if st.button("Apply Filters"):
            filtered_df = df.copy()

            # Sicherstellen, dass die Spalte 'duration' existiert
            if 'duration' not in filtered_df.columns:
                st.error("Duration column is missing from the dataset.")
                return

            # 1️⃣ Year, Duration & Rating filtern
            filtered_df = filtered_df[(filtered_df['year'] >= year_range[0]) & (filtered_df['year'] <= year_range[1])]

            if duration_range[1] == custom_max:  # Falls Schieberegler am Maximum ist
                filtered_df = filtered_df[filtered_df['duration'] >= duration_range[0]]
            else:
                filtered_df = filtered_df[
                    (filtered_df['duration'] >= duration_range[0]) & 
                    (filtered_df['duration'] <= duration_range[1])
                ]

            filtered_df = filtered_df[(filtered_df['rating'] >= rating_range[0]) & (filtered_df['rating'] <= rating_range[1])]

            # 2️⃣ Genres filtern
            if selected_genres:
                filtered_df = filtered_df[filtered_df['genres'].apply(lambda x: any(genre in x for genre in selected_genres))]

            # 3️⃣ Stars filtern - jetzt mit Fix!
            if st.session_state.saved_stars:
                # Sicherstellen, dass jeder Eintrag in 'stars' eine Liste ist
                filtered_df['stars'] = filtered_df['stars'].apply(lambda x: eval(x) if isinstance(x, str) else ([] if pd.isna(x) else x))

                # Filterung durchführen
                filtered_df = filtered_df[filtered_df['stars'].apply(
                    lambda x: isinstance(x, list) and any(star.lower() in [s.lower() for s in x] for star in st.session_state.saved_stars)
                )]



            # 4️⃣ Directors filtern
            # Sicherstellen, dass alle Werte in 'directors' Listen sind, sonst leere Liste setzen
            filtered_df['directors'] = filtered_df['directors'].apply(lambda x: eval(x) if isinstance(x, str) else ([] if pd.isna(x) else x))

            # ✅ Filterlogik für Directors aktualisieren
            if st.session_state.saved_directors:
                filtered_df = filtered_df[filtered_df['directors'].apply(lambda x: any(director in x for director in st.session_state.saved_directors))]


            # 5️⃣ MPA filtern
            if selected_mpa:
                filtered_df = filtered_df[filtered_df['mpa_category'].isin(selected_mpa)]

            # 🔍 Debug: Anzahl gefundener Filme
            st.write(f"✅ Found {len(filtered_df)} movies matching your criteria.")

            # Falls keine Filme gefunden wurden
            if filtered_df.empty:
                st.warning("No movies found! Try adjusting the filters.")



            # Tabellendarstellung

            def ensure_list(items):
                """Konvertiert Strings mit Listenformat in echte Listen."""
                if isinstance(items, str):
                    try:
                        return ast.literal_eval(items)
                    except (SyntaxError, ValueError):
                        return []
                return items if isinstance(items, list) else []

            def format_genres(genres):
                """Formatiert die Genres für die Anzeige (kommagetrennt, ohne Klammern)."""
                return ", ".join(genres) if isinstance(genres, list) else "Not specified"

            def format_list(items):
                """Formatiert eine Liste als kommagetrennten String und entfernt eckige Klammern."""
                items = ensure_list(items)  
                return ", ".join(map(str, items)) if items else "Not specified"

            # ✅ Sicherstellen, dass `filtered_df` keine View ist (Fehlermeldung vermeiden)
            filtered_df = filtered_df.copy()

            # 🔥 Verarbeitung der Listenfelder
            filtered_df['genres'] = filtered_df['genres'].apply(ensure_list)
            filtered_df['stars'] = filtered_df['stars'].apply(ensure_list)
            filtered_df['directors'] = filtered_df['directors'].apply(ensure_list)

            # 🔥 Formatierte Spalten für die Anzeige
            filtered_df['genres'] = filtered_df['genres'].apply(format_genres)
            filtered_df['stars'] = filtered_df['stars'].apply(format_list)
            filtered_df['directors'] = filtered_df['directors'].apply(format_list)

            # ✅ Sortiere die Filme nach IMDb-Rating (höchstes zuerst)
            filtered_df = filtered_df.sort_values(by="rating", ascending=False)

            filtered_df['duration'] = filtered_df['duration'].astype(int)

            # ✅ Sicherstellen, dass 'movie link' existiert und nicht gelöscht wurde
            if "movie link" not in filtered_df.columns:
                st.error("🚨 Spalte 'movie link' fehlt im DataFrame!")

            # ✅ Tabelle mit formatierten Spalten erstellen (aber OHNE 'movie link')
            table = filtered_df[['title', 'year', 'duration', 'rating', 'genres', 'stars', 'directors', 'mpa_category']].copy()

            # 🔥 Links klickbar machen (IMDB-Link wird im Titel hinterlegt)
            if "movie link" in filtered_df.columns:
                table["title"] = filtered_df.apply(
                    lambda x: f'<a href="{x["movie link"]}" target="_blank">{x["title"]}</a>'
                    if pd.notna(x["movie link"]) else x["title"], axis=1
                )

            # ✅ Spaltenüberschriften anpassen (ohne den Link extra anzuzeigen!)
            table.columns = [
                "Movie title",
                "Release (year)",
                "Duration (min)",
                "Rating (IMDb)",
                "Genres",
                "Stars",
                "Directors",
                "Audience Suitability"
            ]


            # ✅ HTML + Style für optimale Spaltenbreiten & zentrierten Text
            st.markdown(
                """
                <style>
                    table {
                        margin-left: auto;
                        margin-right: auto;
                        border-collapse: collapse;
                        width: 100%;
                        border: 2px solid #fafabf;
                    }

                    /* 🔹 Zentrierte Spaltenüberschriften */
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

                    /* 🔹 Tabellenzellen auch zentrieren */
                    td {
                        text-align: center !important;
                        vertical-align: middle !important;
                        padding: 8px;
                    }

                    /* 🔹 Optimierte Spaltenbreiten */
                    th:nth-child(1), td:nth-child(1) { width: 300px; }  /* Movie Title */
                    th:nth-child(2), td:nth-child(2) { width: 80px; }  /* Year */
                    th:nth-child(3), td:nth-child(3) { width: 80px; }  /* Duration */
                    th:nth-child(4), td:nth-child(4) { width: 80px; }  /* Rating */
                    th:nth-child(5), td:nth-child(5),
                    th:nth-child(6), td:nth-child(6),
                    th:nth-child(7), td:nth-child(7) { width: 200px; }  /* Genres, Stars, Directors */
                    th:nth-child(8), td:nth-child(8) { width: 150px; }  /* Audience Suitability */

                    /* 🔹 Hover-Effekt für bessere UX */
                    tr:hover {
                        background-color: #16213e !important;
                    }
                </style>
                """,
                unsafe_allow_html=True
            )


            # ✅ Tabelle sauber anzeigen
            st.markdown(table.to_html(index=False, escape=False), unsafe_allow_html=True)
            st.markdown("")


       


def movie_filter_interface():
    """Implementiert die Benutzeroberfläche für den Movie Filter in Streamlit."""
    
    # 1️⃣ Überprüfen, ob der DataFrame existiert
    if "df_movie_filter" not in st.session_state:
        st.error("Dataset `df_movie_filter` not found in session state. Please check if it was loaded properly.")
        return
    
    df = st.session_state.df_movie_filter

    # 2️⃣ Abschnitt: Search by Title
    search_by_title_interface(df)

    # 3️⃣ Abschnitt: Search by Criteria
    search_by_criteria_interface(df)


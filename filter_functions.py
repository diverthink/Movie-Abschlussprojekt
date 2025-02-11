import os
import pandas as pd
import streamlit as st


def load_movie_data(path=None):
    """Lädt den bereinigten Film-DataFrame aus einer CSV-Datei."""
    if path is None:
        # Dynamischer Pfad relativ zum Verzeichnis der Datei
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, "Datasets", "df_movie_filter.csv")
    return pd.read_csv(path)

def search_by_title(df, search_query):
    """Filtert Filme basierend auf einer Suchanfrage im Titel."""
    search_query = search_query.lower()
    filtered_df = df[df['Title'].str.contains(search_query, case=False, na=False)]
    return filtered_df

def map_genres_to_categories(genres, mapping):
    """Ordnet Genres den definierten Kategorien zu."""
    result = set()
    for genre in genres:
        for category, specific_genres in mapping.items():
            if genre in specific_genres:
                result.add(category)
    return list(result)

def get_genre_mapping():
    """Gibt die Zuordnung von Genres zu Kategorien zurück."""
    return {
    "Action": [
        'Action', 'Action Epic', 'B-Action', 'Car Action', 'Gun Fu', 
        'Martial Arts', 'One-Person Army Action', 'Kung Fu', 
        'Samurai', 'Sword & Sandal', 'Swashbuckler', 'Buddy Cop', 
        'Spy'
    ],
    "Abenteuer": [
        'Adventure', 'Adventure Epic', 'Animal Adventure', 'Desert Adventure', 
        'Dinosaur Adventure', 'Globetrotting Adventure', 'Jungle Adventure', 
        'Mountain Adventure', 'Sea Adventure', 'Space Sci-Fi', 'Urban Adventure', 
        'Quest', 'Survival', 'Road Trip'
    ],
    "Horror": [
        'Horror', 'B-Horror', 'Monster Horror', 'Psychological Horror', 
        'Slasher Horror', 'Supernatural Horror', 'Teen Horror', 
        'Vampire Horror', 'Werewolf Horror', 'Zombie Horror', 
        'Splatter Horror', 'Found Footage Horror', 'Folk Horror', 
        'Giallo', 'Kaiju', 'Witch Horror', 'Body Horror'
    ],
    "Thriller": [
        'Thriller', 'Conspiracy Thriller', 'Political Thriller', 'Erotic Thriller', 
        'Psychological Thriller', 'Serial Killer', 'Heist', 'Crime', 'Cop Drama', 
        'Drug Crime', 'Gangster', 'Police Procedural', 'Legal Thriller', 
        'Suspense Mystery'
    ],
    "Science-Fiction": [
        'Sci-Fi', 'Sci-Fi Epic', 'Dystopian Sci-Fi', 'Cyber Thriller', 
        'Cyberpunk', 'Steampunk', 'Alien Invasion', 'Artificial Intelligence', 
        'Time Travel', 'Mecha', 'Superhero'
    ],
    "Fantasy": [
        'Fantasy', 'Dark Fantasy', 'Fantasy Epic', 'Sword & Sorcery', 
        'Supernatural Fantasy', 'Fairy Tale', 'Isekai', 'Slice of Life', 
        'Teen Fantasy'
    ],
    "Komödie": [
        'Comedy', 'Dark Comedy', 'Farce', 'High-Concept Comedy', 'Quirky Comedy', 
        'Raunchy Comedy', 'Romantic Comedy', 'Screwball Comedy', 'Slapstick', 
        'Stoner Comedy', 'Teen Comedy', 'Buddy Comedy', 'Parody', 'Satire', 
        'Sketch Comedy', 'Mockumentary', 'Sitcom'
    ],
    "Drama": [
        'Drama', 'Costume Drama', 'Cop Drama', 'Crime', 'Docudrama', 'Family', 
        'Historical Epic', 'Legal Drama', 'Medical Drama', 'Period Drama', 
        'Political Drama', 'Prison Drama', 'Psychological Drama', 'Showbiz Drama', 
        'Teen Drama', 'Tragedy', 'Workplace Drama', 'Financial Drama', 
        'Korean Drama', 'Biography', 'Dark Romance'
    ],
    "Romantik": [
        'Romance', 'Feel-Good Romance', 'Holiday Romance', 'Teen Romance', 
        'Tragic Romance', 'Steamy Romance', 'Romantic Epic'
    ],
    "Musik und Tanz": [
        'Musical', 'Classic Musical', 'Pop Musical', 'Rock Musical', 
        'Concert', 'Music', 'Jukebox Musical', 'Music Documentary'
    ],
    "Sport": [
        'Baseball', 'Basketball', 'Boxing', 'Extreme Sport', 'Football', 
        'Motorsport', 'Soccer', 'Sport', 'Sports Documentary', 'Water Sport'
    ],
    "Krimi": [
        'True Crime', 'Heist', 'Drug Crime', 'Gangster', 'Hard-boiled Detective', 
        'Bumbling Detective', 'Cozy Mystery'
    ],
    "Dokumentationen": [
        'Documentary', 'Crime Documentary', 'Food Documentary', 
        'Military Documentary', 'Nature Documentary', 
        'Political Documentary', 'Science & Technology Documentary', 
        'Travel Documentary', 'Faith & Spirituality Documentary', 'History Documentary', 
        'Game Show', 'News', 'Reality TV', 'Talk Show'
    ],
    "Western": [
        'Western', 'Contemporary Western', 'Classical Western', 
        'Spaghetti Western', 'Western Epic'
    ],
    "Animation": [
        'Animation', 'Anime', 'Hand-Drawn Animation', 'Stop Motion Animation', 
        'Adult Animation', 'Computer Animation'
    ],
    "Kinder und Familie": [
        'Family', 'Holiday Family', 'Teen Adventure', 'Coming-of-Age', 
        'Holiday', 'Holiday Animation', 'Holiday Comedy'
    ],
    "Historisch": [
        'Historical Epic', 'History', 'Period Drama'
    ],
    "Krieg": [
        'War', 'War Epic'
    ],
    "Mystery": [
        'Mystery', 'Whodunnit'
    ],
    "Sonstiges": [
        'Epic', 'Stand-Up', 'Iyashikei', 'Josei', 'Seinen', 'Shōjo', 
        'Shōnen', 'Soap Opera'
    ]
}

def display_movie_details(selected_movie):
    """Zeigt alle Details eines ausgewählten Films an."""
    st.subheader(f"Details for: {selected_movie['Title']}")
    st.write(f"**Year:** {selected_movie['Year']}")

    # Duration
    duration = selected_movie['Duration']
    if pd.isna(duration):
        st.write("**Duration:** Not specified")
    else:
        st.write(f"**Duration:** {int(duration)} minutes")

    st.write(f"**Rating:** {selected_movie['Rating']}")

    # Genres
    genres = eval(selected_movie['genres']) if isinstance(selected_movie['genres'], str) else selected_movie['genres']
    if genres:
        genre_mapping = get_genre_mapping()
        categories = map_genres_to_categories(genres, genre_mapping)
        st.write(f"**Genres:** {', '.join(categories)}")
    else:
        st.write("**Genres:** Not specified")

    # Oscars
    st.write(f"**Oscars:** {selected_movie['oscars']}")

    # Stars
    stars = eval(selected_movie['stars']) if isinstance(selected_movie['stars'], str) else selected_movie['stars']
    if stars:
        st.write("**Stars:**")
        for star in stars:
            st.markdown(f"- {star}")
    else:
        st.write("**Stars:** Not specified")

    # Directors
    directors = eval(selected_movie['directors']) if isinstance(selected_movie['directors'], str) else selected_movie['directors']
    if directors:
        st.write("**Directors:**")
        for director in directors:
            st.markdown(f"- {director}")
    else:
        st.write("**Directors:** Not specified")

    st.write(f"**MPA Rating:** {selected_movie['MPA']}")
    st.markdown(f"[Movie Link]({selected_movie['Movie Link']})")

def search_by_title_interface(df):
    """Implementiert die Suchfunktion nach Titel mit Einklapp-Option."""
    with st.expander("Search by Title", expanded=True):
        search_query = st.text_input("Enter movie title or keywords:")

        # Session State für gefilterte Ergebnisse und ausgewählten Film
        if "filtered_df" not in st.session_state:
            st.session_state.filtered_df = None
        if "selected_movie" not in st.session_state:
            st.session_state.selected_movie = None

        # Suchbutton
        if st.button("Search", key="search_title_button"):
            # Suche ausführen
            st.session_state.filtered_df = search_by_title(df, search_query)
            st.session_state.selected_movie = None  # Zurücksetzen, wenn neue Suche gestartet wird

        # Gefilterte Ergebnisse anzeigen
        if st.session_state.filtered_df is not None and not st.session_state.filtered_df.empty:
            st.write(f"Found {len(st.session_state.filtered_df)} movies:")
            selected_title = st.selectbox(
                "Select a movie to view details:",
                st.session_state.filtered_df['Title'].tolist(),
                key="selected_title_dropdown"
            )

            # Aktualisiere den ausgewählten Film
            if selected_title:
                st.session_state.selected_movie = st.session_state.filtered_df[
                    st.session_state.filtered_df['Title'] == selected_title
                ].iloc[0]

        # Details des ausgewählten Films anzeigen
        if st.session_state.selected_movie is not None:
            display_movie_details(st.session_state.selected_movie)

def search_by_criteria_interface(df):
    """Implementiert die Filterfunktion nach Kriterien."""
    with st.expander("Search by Criteria", expanded=False):
        st.write("Filter movies based on various criteria.")

        # Zeile 1: Year, Duration, Rating
        col1, col2, col3 = st.columns(3, gap="large")

        with col1:
            st.subheader("Year")
            year_min, year_max = int(df['Year'].min()), int(df['Year'].max())
            year_range = st.slider("Select Year Range", year_min, year_max, (year_min, year_max))

        with col2:
            st.subheader("Duration")
            duration_min, custom_max = 0, 300  # Sichtbare Obergrenze
            duration_range = st.slider(
                "Select Duration Range (minutes)",
                duration_min,
                custom_max,
                (duration_min, custom_max),
                help="Drag to filter to max (300), to include all longer movies."
            )

        with col3:
            st.subheader("Rating")
            rating_min, rating_max = 0.0, 10.0
            rating_range = st.slider("Select Rating Range", rating_min, rating_max, (rating_min, rating_max))

        st.divider()

        # Zeile 2: Genres, MPA Rating
        col4, col5 = st.columns(2, gap="large")

        with col4:
            st.subheader("Genres")
            genre_mapping = get_genre_mapping()
            genre_categories = list(genre_mapping.keys())  # Nur Hauptkategorien
            selected_genres = st.multiselect("Select Genres", genre_categories)

        with col5:
            st.subheader("Audience Suitability")
            mpa_categories = {
                "All Ages (+0)": ['G', 'TV-G', 'TV-Y', 'TV-Y7', 'K-A', 'Approved'],
                "Parental Guidance (+13)": ['PG', 'PG-13', 'M/PG', 'TV-PG', 'TV-13', 'TV-14'],
                "Mature Audiences (+18)": ['R', 'MA-17', 'TV-MA', 'NC-17', 'X'],
                "Not Rated/Other": ['Not Rated', 'Unrated', 'Passed', 'GP']
            }
            selected_categories = st.multiselect("Select MPA Categories", list(mpa_categories.keys()))
            selected_mpa = [mpa for category in selected_categories for mpa in mpa_categories[category]]

        st.divider()

        # Zeile 3: Stars, Directors
        col6, col7 = st.columns(2, gap="large")

        with col6:
            st.subheader("Stars")
            star_search = st.text_input("Search for Stars:")
            selected_stars = []
            if star_search:
                all_stars = [star.strip() for stars in df['stars'].dropna() for star in eval(stars)]
                possible_stars = sorted(set(star for star in all_stars if star_search.lower() in star.lower()))
                selected_stars = st.multiselect("Select Stars", possible_stars)

        with col7:
            st.subheader("Directors")
            director_search = st.text_input("Search for Directors:")
            selected_directors = []
            if director_search:
                all_directors = [director.strip() for directors in df['directors'].dropna() for director in eval(directors)]
                possible_directors = sorted(set(director for director in all_directors if director_search.lower() in director.lower()))
                selected_directors = st.multiselect("Select Directors", possible_directors)

        st.divider()

        # Zeile 4: Oscars
        st.subheader("Oscars")
        oscars_filter = st.checkbox("Only show movies with Oscars")

        # Anwenden der Filter
        if st.button("Apply Filters"):
            filtered_df = df.copy()

            # Sicherstellen, dass die Spalte 'Duration' existiert
            if 'Duration' not in filtered_df.columns:
                st.error("Duration column is missing from the dataset.")
                return


            # Filter anwenden
            filtered_df = filtered_df[(filtered_df['Year'] >= year_range[0]) & (filtered_df['Year'] <= year_range[1])]

            # Filterlogik für Duration
            if duration_range[1] == custom_max:  # Schieberegler auf Maximum
                filtered_df = filtered_df[filtered_df['Duration'] >= duration_range[0]]
            else:  # Bereich innerhalb von 0 bis custom_max
                filtered_df = filtered_df[
                    (filtered_df['Duration'] >= duration_range[0]) & 
                    (filtered_df['Duration'] <= duration_range[1])
                ]

            filtered_df = filtered_df[(filtered_df['Rating'] >= rating_range[0]) & (filtered_df['Rating'] <= rating_range[1])]

            if selected_genres:
                filtered_df = filtered_df[filtered_df['genres'].apply(lambda x: isinstance(x, str) and any(genre in x for genre in selected_genres))]

            if oscars_filter:
                filtered_df = filtered_df[filtered_df['oscars'] > 0]

            if selected_stars:
                filtered_df = filtered_df[filtered_df['stars'].apply(lambda x: isinstance(x, str) and any(star in eval(x) for star in selected_stars))]

            if selected_directors:
                filtered_df = filtered_df[filtered_df['directors'].apply(lambda x: isinstance(x, str) and any(director in eval(x) for director in selected_directors))]

            if selected_mpa:
                filtered_df = filtered_df[filtered_df['MPA'].isin(selected_mpa)]

            # Tabellendarstellung
            def format_genres(genres):
                genre_mapping = get_genre_mapping()
                genres_list = eval(genres) if isinstance(genres, str) else []
                categories = map_genres_to_categories(genres_list, genre_mapping)
                return "<br>".join(categories) if categories else "Not specified"

            def format_list(items):
                return "<br>".join(eval(items)) if isinstance(items, str) else "Not specified"

            def map_mpa_category(mpa):
                for category, subcategories in mpa_categories.items():
                    if mpa in subcategories:
                        return category
                return "Unknown"

            filtered_df['Genres'] = filtered_df['genres'].apply(format_genres)
            filtered_df['Stars'] = filtered_df['stars'].apply(format_list)
            filtered_df['Directors'] = filtered_df['directors'].apply(format_list)
            filtered_df['MPA'] = filtered_df['MPA'].apply(map_mpa_category)

            table = filtered_df[['Title', 'Year', 'Duration', 'Rating', 'Genres', 'Stars', 'Directors', 'MPA', 'oscars']]
            table['Duration'] = table['Duration'].astype(int)
            table['Year'] = table['Year'].astype(int)
            table['Title'] = table.apply(lambda x: f"<a href='{x['Movie Link']}' target='_blank'>{x['Title']}</a>" if 'Movie Link' in x and pd.notna(x['Movie Link']) else x['Title'], axis=1)
            table.rename(columns={'oscars': 'Oscars'}, inplace=True)
            

            # Tabelle zentrieren
            st.markdown(
                """
                <style>
                table {
                    margin-left: auto;
                    margin-right: auto;
                }
                th, td {
                    text-align: center;
                }
                </style>
                """,
                unsafe_allow_html=True
            )

            st.write(f"Filtered {len(filtered_df)} movies:")
            # Spaltenüberschriften anpassen (z. B. "Duration (min)" und "Rating (IMDb)" mit Umbruch)
            table.columns = [
                "Title",
                "Year",
                "Duration<br>(min)",
                "Rating<br>(IMDb)",
                "Genres",
                "Stars",
                "Directors",
                "Audience Suitability",
                "Oscars"
            ]
            
            st.markdown(table.to_html(index=False, escape=False), unsafe_allow_html=True)

       


def movie_filter_interface():
    """Implementiert die Benutzeroberfläche für den Movie Filter in Streamlit."""
    # Laden der Daten
    df = load_movie_data()

    # Abschnitt: Search by Title
    search_by_title_interface(df)

    # Abschnitt: Search by Criteria
    search_by_criteria_interface(df)








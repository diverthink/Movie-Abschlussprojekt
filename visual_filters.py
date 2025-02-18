import streamlit as st
import pandas as pd
import ast

def filter_options(df):

    if 'visual_filters' not in st.session_state:
        st.session_state['visual_filters'] = {}

    col1, col2, col3 = st.columns(3, gap="large")

    with col1:
        st.subheader("Year")
        year_min, year_max = int(df['Year'].min()), int(df['Year'].max())
        st.session_state['visual_filters']['year_range'] = st.slider("Select Year Range", year_min, year_max, (year_min, year_max), key='year')

    with col2:
        st.subheader("Duration")
        duration_min, custom_max = 0, 300  # Sichtbare Obergrenze
        st.session_state['visual_filters']['duration_range'] = st.slider(
            "Select Duration Range (minutes)",
            duration_min,
            custom_max,
            (duration_min, custom_max),
            help="Drag to filter to max (300), to include all longer movies.",
            key='duration'
        )

    with col3:
        st.subheader("Rating")
        rating_min, rating_max = 0.0, 10.0
        st.session_state['visual_filters']['rating_range'] = st.slider("Select Rating Range", rating_min, rating_max, (rating_min, rating_max), key='rating')

    st.divider()

    # Zeile 2: Genres, MPA Rating
    col4, col5 = st.columns(2, gap="large")

    with col4:
        st.subheader("Genres")
        df['main_genres'] = df['main_genres'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        exploded_genres = df.explode('main_genres')
        genres_to_choose = list(exploded_genres['main_genres'].unique())  # Nur Hauptkategorien
        st.session_state['visual_filters']['selected_genres'] = st.multiselect("Select Genres", genres_to_choose)

    with col5:
        st.subheader("Audience Suitability")
        st.session_state['visual_filters']['selected_categories'] = st.multiselect("Select MPA Categories", list(df['MPA_category'].unique()))

    st.divider()

    # Zeile 3: Stars, Directors
    col6, col7 = st.columns(2, gap="large")

    with col6:
        st.subheader("Stars")
        stars_df = pd.DataFrame()
        stars_df['stars'] = df['stars'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        exploded_stars = stars_df.explode('stars')
        stars_to_choose = list(exploded_stars['stars'].unique())  # Einzelne Stars
        st.session_state['visual_filters']['selected_stars'] = st.multiselect(label='Search for Stars', options=stars_to_choose, placeholder="Select Stars")

    with col7:
        st.subheader("Directors")
        director_df = pd.DataFrame()
        director_df['directors'] = df['directors'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        exploded_directors = director_df.explode('directors')
        directors_to_choose = list(exploded_directors['directors'].unique())  # Einzelne Directors
        st.session_state['visual_filters']['selected_directors'] = st.multiselect("Search for Directors", directors_to_choose, placeholder='Select Directors')

    st.divider()

    # Zeile 4: Oscars
    st.subheader("Oscars")
    st.session_state['visual_filters']['oscars_filter'] = st.checkbox("Only show movies with Oscars")

    # Anwenden der Filter
    filtered_df = df.copy()

    filters = st.session_state['visual_filters']

    # Sicherstellen, dass die Spalte 'Duration' existiert
    if 'Duration' not in filtered_df.columns:
        st.error("Duration column is missing from the dataset.")
        return

    # Jahr filtern
    year_range = filters.get('year_range', (df['Year'].min(), df['Year'].max()))
    filtered_df = filtered_df[(filtered_df['Year'] >= year_range[0]) & (filtered_df['Year'] <= year_range[1])]

    # Dauer filtern
    duration_range = filters.get('duration_range', (0, 300))
    if duration_range[1] == 300:  # Schieberegler auf Maximum
        filtered_df = filtered_df[filtered_df['Duration'] >= duration_range[0]]
    else:
        filtered_df = filtered_df[
            (filtered_df['Duration'] >= duration_range[0]) & 
            (filtered_df['Duration'] <= duration_range[1])
        ]

    # Bewertung filtern
    rating_range = filters.get('rating_range', (0.0, 10.0))
    filtered_df = filtered_df[(filtered_df['Rating'] >= rating_range[0]) & (filtered_df['Rating'] <= rating_range[1])]

    # Genre filtern
    selected_genres = filters.get('selected_genres', [])
    if selected_genres:
        filtered_df = filtered_df[filtered_df['main_genres'].apply(lambda x: isinstance(x, list) and any(genre in x for genre in selected_genres))]

    # Oscars filtern
    oscars_filter = filters.get('oscars_filter', False)
    if oscars_filter:
        filtered_df = filtered_df[filtered_df['oscars'] > 0]

    # Stars filtern
    selected_stars = filters.get('selected_stars', [])
    if selected_stars:
        filtered_df['stars'] = filtered_df['stars'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        filtered_df = filtered_df[filtered_df['stars'].apply(lambda x: isinstance(x, list) and any(star in x for star in selected_stars))]

    # Regisseure filtern
    selected_directors = filters.get('selected_directors', [])
    if selected_directors:
        filtered_df['directors'] = filtered_df['directors'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
        filtered_df = filtered_df[filtered_df['directors'].apply(lambda x: isinstance(x, list) and any(director in x for director in selected_directors))]

    # MPA-Kategorie filtern
    selected_categories = filters.get('selected_categories', [])
    if selected_categories:
        filtered_df = filtered_df[filtered_df['MPA_category'].isin(selected_categories)]

    return filtered_df
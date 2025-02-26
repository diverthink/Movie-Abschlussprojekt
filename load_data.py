import streamlit as st
import pandas as pd
import pickle
import os

import visualisation_data_cleaning

def load_datasets():
    """Lädt alle benötigten Datensätze in st.session_state, falls sie noch nicht vorhanden sind."""

    # Setze den Pfad zum Hauptordner (wo `main.py` liegt)
    script_dir = os.path.dirname(os.path.abspath(__file__))  
    dataset_dir = os.path.join(script_dir, "Datasets")  # Richtiges Verzeichnis

    # 1️⃣ Lade `df_movie_filter.csv`
    if "df_movie_filter" not in st.session_state:
        movie_filter_path = os.path.join(dataset_dir, "df_movie_filter.csv")
        st.session_state.df_movie_filter = pd.read_csv(movie_filter_path)

    # 2️⃣ Lade `df_test_similarity_scaled.csv`
    if "df_test_similarity_scaled" not in st.session_state:
        similarity_scaled_path = os.path.join(dataset_dir, "df_test_similarity_scaled.csv")
        st.session_state.df_test_similarity_scaled = pd.read_csv(similarity_scaled_path)

    # 3️⃣ Lade `df_test_similarity.csv`
    if "df_test_similarity" not in st.session_state:
        similarity_path = os.path.join(dataset_dir, "df_test_similarity.csv")
        st.session_state.df_test_similarity = pd.read_csv(similarity_path)

    # 4️⃣ Lade `similarity_matrix.pkl`
    if "cosine_similarity_matrix" not in st.session_state:
        cosine_path = os.path.join(dataset_dir, "similarity_matrix.pkl")
        with open(cosine_path, "rb") as f:
            st.session_state.cosine_similarity_matrix = pickle.load(f)

    # 5️⃣ Lade 'df_visualisation'
    if 'df_visualisation' not in st.session_state:
        st.session_state['df_visualisation'] = visualisation_data_cleaning.visual_data()



    print("✅ Alle Datensätze wurden erfolgreich geladen.")



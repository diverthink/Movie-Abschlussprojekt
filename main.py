import streamlit as st
from filter_functions import movie_filter_interface
from suggestion_prediction_rating import run_movie_suggestion_pipeline
from load_data import load_datasets

import prediction
import visualisation
import start_page


load_datasets()

# App Title
st.set_page_config(page_title="Movie it!", layout="wide")

# Sidebar Navigation
st.sidebar.title("🔽 Toolbox")
st.sidebar.info("Explore and discover movies with advanced filtering and recommendations.")

option = st.sidebar.radio("Select a feature:", [
    "🎬 Starting Page",
    "📊 Visualization & Statistics",
    "🔍 Search for Movies",
    "⭐ Movie Recommendations",
    "🏆 Awards Prediction"
])


# Main Window
if option in [
    "📊 Visualization & Statistics",
    "🔍 Search for Movies",
    "⭐ Movie Recommendations",
    "🏆 Awards Prediction"
]:
    st.markdown("<h1 style='text-align: center;'>🎬 Movie it!  🎬</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>- Because life's too short to scroll endlessly -</h1>", unsafe_allow_html=True)


# Dynamic Content Area
if option == "🎬 Starting Page":
    start_page.start_page()

elif option == "📊 Visualization & Statistics":
    st.markdown("---")
    st.markdown(
        f"""
        <div style="background-color: #1b1f3a ; padding:12px; border-radius:10px; text-align:center;">
            <h2 style="color: #ffffff ; margin: 0;">📊 Visualization & Statistics 📊</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")
    st.info("""**Visualise our Movie Inventory**.  
                Choose your ingredients and see what spicy graphs and figures come out of it.  
                That means, getting an overview over approx. 6400 movies in the database consisting of the 100-200 highest grossing movies of each year from 1960-2025.  
                Choose Filters, select the chart type, select the axes, and dive deep into the pool of movie data.""")

    st.markdown("---")
    visualisation.visualise_it()

elif option == "🔍 Search for Movies":
    st.markdown("---")
    st.markdown(
        f"""
        <div style="background-color: #1b1f3a ; padding:12px; border-radius:10px; text-align:center;">
            <h2 style="color: #ffffff ; margin: 0;">🔍 Search for Movies 🔍</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")
    st.info("**Are you looking for a movie and some information? Use:** \n * Option 1 (*search for titles by key word*) or, \n * Option 2 (*search for titles by individual criteria*) \n\n **and I'll show you specifc movie details!** *(e.g. rating, actors, duration...)*")
    st.markdown("---")
    movie_filter_interface()

elif option == "⭐ Movie Recommendations":
    st.markdown("---")
    st.markdown(
        f"""
        <div style="background-color: #1b1f3a ; padding:12px; border-radius:10px; text-align:center;">
            <h2 style="color: #ffffff ; margin: 0;">⭐ Movie Recommendations ⭐ </h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")
    st.info("**Get personalized movie recommendations based on your taste! Simply tell me which films you know, rate them along with some suggestions, and I'll find movies you might love - automatically!**")
    st.markdown("---")
    run_movie_suggestion_pipeline()

elif option == "🏆 Awards Prediction":
    st.markdown("---")
    st.markdown(
        f"""
        <div style="background-color: #1b1f3a ; padding:12px; border-radius:10px; text-align:center;">
            <h2 style="color: #ffffff ; margin: 0;">🏆 Awards Prediction 🏆</h2>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.write("")
    st.info("""**Check if your movie is an outstanding one!**  
                    Do you have an idea for a movie or do you have an existing film and want it checked if it is an award or even Oscar nomination candidate?  
                    Get it checked here!  
                    * To get a prediction for 2025 (last update 14.2.2025) movies, please select Oscars and automatic method.  
                    * Note: Automatic might take a while to load and could eventually fail, if you are using a docker image.""")
    st.markdown("---")
    prediction.startProcess()

# Footer
st.sidebar.markdown("---")
st.sidebar.text("""🆓 Final project developed  
                for Data Science Institute""")

st.sidebar.markdown("---")
st.sidebar.markdown("""🎥 **Credits**""")
st.sidebar.link_button("Original Kaggle dataset by Raed Addala", "https://www.kaggle.com/datasets/raedaddala/imdb-movies-from-1960-to-2023")
st.sidebar.link_button("Base code for data scraping by Raed Addala", "https://github.com/RaedAddala/Scraping-IMDB/releases")
st.sidebar.link_button("All data was scraped from the IMDb website.", "https://www.imdb.com/de/?ref_=nv_home")
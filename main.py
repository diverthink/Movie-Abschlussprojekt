import streamlit as st
from filter_functions import movie_filter_interface

# App Title
st.set_page_config(page_title="Movie it!", layout="wide")

# Sidebar Navigation
st.sidebar.title("🎬 Welcome to Movie it!")
option = st.sidebar.radio("Select a feature:", [
    "Movie Filter",
    "Movie Suggestion",
    "Movie Rater",
    "Oscar Prediction (optional)"
])

# Main Window
st.title("Movie it! - Because life's too short to scroll endlessly.")
st.write("Explore and discover movies with advanced filtering and recommendations.")

# Dynamic Content Area
if option == "Movie Filter":
    st.subheader("🔍 Movie Filter")
    movie_filter_interface()

elif option == "Movie Suggestion":
    st.subheader("🤖 Movie Suggestion")
    st.write("A recommendation system that improves as you rate more movies.")

elif option == "Movie Rater":
    st.subheader("⭐ Movie Rater")
    st.write("Predict how much you might like a specific movie based on your past ratings.")

elif option == "Oscar Prediction (optional)":
    st.subheader("🏆 Oscar Prediction")
    st.write("(Experimental) Predict whether a movie has the potential to win an Oscar!")

# Footer
st.sidebar.markdown("---")
st.sidebar.text("Developed by your Data Science team.")

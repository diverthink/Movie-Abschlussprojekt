import streamlit as st

def start_page():
    side_col1, header_col, side_col2 = st.columns([0.1,0.8,0.1], vertical_alignment='center')
    header_col.image('banner/movie_it.jpg', use_container_width=True)
    header_col.markdown("<h3 style='text-align: center;'>- Because life's too short to scroll endlessly -</h1>", unsafe_allow_html=True)
    header_col.markdown("<h5 style='text-align: center;'>What can you discover here?</h1>", unsafe_allow_html=True)

    st.divider()
    col0_1, col0_2, col0_3, col0_4 = st.columns(4)
    col0_1.subheader('Visualisation')
    col0_2.subheader('Movie Search')
    col0_3.subheader('Movie Recommendation')
    col0_4.subheader('Award Prediction')


    st.divider()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("""**Visualize our Movie Inventory!**  
                *Choose your ingredients and see what spicy graphs and figures come out of it.  
                That means, getting an overview over approx. 6400 movies in the database consisting of the 100-200 highest grossing movies of each year from 1960-2025.  
                *Choose Filters, select the chart type, select the axes, and dive deep into the pool of movie data.""")

    with col2:
        st.markdown("""**Are you looking for a movie and some information? Use:**  
                    * Option 1 (*search for titles by key word*) or,  
                    * Option 2 (*search for titles by individual criteria*)  
                    **and I'll show you specifc movie details!** *(e.g. rating, actors, duration...)*""")

    with col3:
        st.markdown("""**Get personalized movie recommendations based on your taste!**  
                    Simply tell me which films you know, rate them along with some suggestions, and I'll find movies you might love - automatically!""")

    with col4:
        st.markdown("""**Check if your movie is an outstanding one!**  
                    Do you have an idea for a movie or do you have an existing film and want it checked if it is an award or even Oscar nomination candidate?  
                    Get it checked here!""")

    st.divider()
    st.info('Developed by: Florian Wegener, Jirires Mustaklem and Marc Schwab as part of the DSI Data Science Course Final Project.')
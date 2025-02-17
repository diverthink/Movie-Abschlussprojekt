import streamlit as st
import pandas as pd
import plotly.express as px
import visualisation_functions as vf

# Initialisiere die Session State Variablen
if 'data' not in st.session_state:
    st.session_state['data'] = vf.load_movie_data()
if 'visual_count' not in st.session_state:
    st.session_state['visual_count'] = 0
if 'figures' not in st.session_state:
    st.session_state['figures'] = []

# Abrufen der Daten
data = st.session_state['data']

but_new_fig = st.button('Neue Visualisierung')


### ausweisen neuer Columns, welche dann zur auswahl stehen.
cat_columns = ['Year', 'MPA_category', 'has_oscars', 'decade']
num_columns = ['Duration', 'Rating', 'Votes', 'budget', 'grossWorldWide', 'gross_US_Canada',
               'opening_weekend_Gross', 'wins', 'nominations', 'oscars', 'inflation_gross_opening', 'budget_inflation']

# Wenn der Button gedrückt wird, eine neue Figur hinzufügen
if but_new_fig:
    st.session_state['visual_count'] += 1
    fig_id = st.session_state['visual_count']
    st.session_state['figures'].append({'id': fig_id, 'params': {}, 'type': None})

# Anzeige der Figuren
for fig in st.session_state['figures']:
    with st.container():
        st.write(f"### Visualisierung {fig['id']}")
        
        plot_type = st.selectbox(f"Plot-Typ ({fig['id']})", ['Histogram', 'Scatter', 'Violin', 'Line', 'Line Comparison'], key=f"plot_type_{fig['id']}")
        
        if plot_type == 'Histogram':
            x_axis = st.selectbox(f"X-Achse ({fig['id']})", cat_columns, key=f"x_{fig['id']}")
            y_axis = st.selectbox(f"Y-Achse ({fig['id']})", [None] + num_columns, key=f"y_{fig['id']}")
            groupby = st.selectbox(f"Gruppierung ({fig['id']})", [None] + cat_columns, key=f"groupby_{fig['id']}")
            aggregation = st.selectbox(f"Aggregation ({fig['id']})", ['count', 'sum', 'avg', 'min', 'max', 'median'], key=f"agg_{fig['id']}")

            fig_plot = vf.histplot(data, x_axis, y_axis, groupby, aggregation)
        
        elif plot_type == 'Scatter':
            x_axis = st.selectbox(f"X-Achse ({fig['id']})", num_columns, key=f"x_{fig['id']}")
            y_axis = st.selectbox(f"Y-Achse ({fig['id']})", num_columns, key=f"y_{fig['id']}")
            groupby = st.selectbox(f"Gruppierung ({fig['id']})", [None] + cat_columns, key=f"groupby_{fig['id']}")
            fig_plot = vf.scatter(data, x_axis, y_axis, groupby)
        
        elif plot_type == 'Violin':
            y_axis = st.selectbox(f"Y-Achse ({fig['id']})", num_columns, key=f"y_{fig['id']}")
            x_axis = st.selectbox(f"X-Achse ({fig['id']})", [None] + cat_columns, key=f"x_{fig['id']}")
            groups = st.selectbox(f"Gruppierung ({fig['id']})", [None] + cat_columns, key=f"groups_{fig['id']}")
            points = st.selectbox(f"Punkte ({fig['id']})", ['all', 'outliers', 'suspectedoutliers', False], key=f"points_{fig['id']}")
            fig_plot = vf.violinplot(data, y_axis, x_axis, groups, points)
        
        elif plot_type == 'Line':
            x_axis = st.selectbox(f"X-Achse ({fig['id']})", cat_columns, key=f"x_{fig['id']}")
            y_axis = st.selectbox(f"Y-Achse ({fig['id']})", num_columns, key=f"y_{fig['id']}")
            aggregation = st.selectbox(f"Aggregation ({fig['id']})", ['mean', 'median', 'count', 'sum', 'max', 'min'], key=f"agg_{fig['id']}")
            fig_plot = vf.lineplot(data, x_axis, y_axis, aggregation)
        
        elif plot_type == 'Line Comparison':
            x_axis = st.selectbox(f"X-Achse ({fig['id']})", cat_columns, key=f"x_{fig['id']}")
            y_axis_1 = st.selectbox(f"Y-Achse 1 ({fig['id']})", num_columns, key=f"y1_{fig['id']}")
            y_axis_2 = st.selectbox(f"Y-Achse 2 ({fig['id']})", num_columns, key=f"y2_{fig['id']}")
            aggregation = st.selectbox(f"Aggregation ({fig['id']})", ['mean', 'median', 'count', 'sum', 'max', 'min'], key=f"agg_{fig['id']}")
            fig_plot = vf.compare_graphs(data, x_axis, y_axis_1, y_axis_2, aggregation)
        
        st.plotly_chart(fig_plot)
        
        # Button zum Löschen der Figur
        if st.button(f"Löschen ({fig['id']})", key=f"delete_{fig['id']}"):
            st.session_state['figures'] = [f for f in st.session_state['figures'] if f['id'] != fig['id']]
            st.rerun()
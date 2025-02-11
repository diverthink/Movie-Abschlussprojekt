import streamlit as st
import pandas as pd
import visualisation_functions as vf

# Initialisiere die Session State Variablen
if 'data' not in st.session_state:
    st.session_state['data'] = vf.add_decade_inflation_hasoscars()
if 'visual_count' not in st.session_state:
    st.session_state['visual_count'] = 0
if 'figures' not in st.session_state:
    st.session_state['figures'] = []

# Abrufen der Daten
data = st.session_state['data']

but_new_fig = st.button('Neue Visualisierung')

# Wenn der Button gedrückt wird, eine neue Figur hinzufügen
if but_new_fig:
    st.session_state['visual_count'] += 1
    fig_id = st.session_state['visual_count']
    st.session_state['figures'].append({'id': fig_id, 'params': {}, 'type': None})

# Anzeige der Figuren
for fig in st.session_state['figures']:
    with st.container():
        st.write(f"### Visualisierung {fig['id']}")
        
        plot_type = st.selectbox(f"Plot-Typ ({fig['id']})", ['Histogram', 'Scatter', 'Violin', 'Line', 'Compare'], key=f"plot_type_{fig['id']}")
        
        if plot_type == 'Histogram':
            x_axis = st.selectbox(f"X-Achse ({fig['id']})", data.columns, key=f"x_{fig['id']}")
            y_axis = st.selectbox(f"Y-Achse ({fig['id']})", [None] + list(data.columns), key=f"y_{fig['id']}")
            groupby = st.selectbox(f"Gruppierung ({fig['id']})", [None] + list(data.columns), key=f"groupby_{fig['id']}")
            aggregation = st.selectbox(f"Aggregation ({fig['id']})", ['count', 'sum', 'avg', 'min', 'max'], key=f"agg_{fig['id']}")
            fig_plot = vf.histplot(data, x_axis, y_axis, groupby, aggregation)
        
        elif plot_type == 'Scatter':
            x_axis = st.selectbox(f"X-Achse ({fig['id']})", data.columns, key=f"x_{fig['id']}")
            y_axis = st.selectbox(f"Y-Achse ({fig['id']})", data.columns, key=f"y_{fig['id']}")
            groupby = st.selectbox(f"Gruppierung ({fig['id']})", [None] + list(data.columns), key=f"groupby_{fig['id']}")
            fig_plot = vf.scatter(data, x_axis, y_axis, groupby)
        
        elif plot_type == 'Violin':
            y_axis = st.selectbox(f"Y-Achse ({fig['id']})", data.columns, key=f"y_{fig['id']}")
            x_axis = st.selectbox(f"X-Achse ({fig['id']})", [None] + list(data.columns), key=f"x_{fig['id']}")
            groups = st.selectbox(f"Gruppierung ({fig['id']})", [None] + list(data.columns), key=f"groups_{fig['id']}")
            points = st.selectbox(f"Punkte ({fig['id']})", ['all', 'outliers', 'suspectedoutliers', False], key=f"points_{fig['id']}")
            fig_plot = vf.violinplot(data, y_axis, x_axis, groups, points)
        
        elif plot_type == 'Line':
            x_axis = st.selectbox(f"X-Achse ({fig['id']})", data.columns, key=f"x_{fig['id']}")
            y_axis = st.selectbox(f"Y-Achse ({fig['id']})", data.columns, key=f"y_{fig['id']}")
            aggregation = st.selectbox(f"Aggregation ({fig['id']})", ['mean', 'median', 'count', 'sum'], key=f"agg_{fig['id']}")
            fig_plot = vf.lineplot(data, x_axis, y_axis, aggregation)
        
        elif plot_type == 'Compare':
            x_axis = st.selectbox(f"X-Achse ({fig['id']})", data.columns, key=f"x_{fig['id']}")
            y_axis_1 = st.selectbox(f"Y-Achse 1 ({fig['id']})", data.columns, key=f"y1_{fig['id']}")
            y_axis_2 = st.selectbox(f"Y-Achse 2 ({fig['id']})", data.columns, key=f"y2_{fig['id']}")
            aggregation = st.selectbox(f"Aggregation ({fig['id']})", ['mean', 'median', 'count', 'sum'], key=f"agg_{fig['id']}")
            fig_plot = vf.compare_graphs(data, x_axis, y_axis_1, y_axis_2, aggregation)
        
        st.plotly_chart(fig_plot)
        
        # Button zum Löschen der Figur
        if st.button(f"Löschen ({fig['id']})", key=f"delete_{fig['id']}"):
            st.session_state['figures'] = [f for f in st.session_state['figures'] if f['id'] != fig['id']]
            st.rerun()
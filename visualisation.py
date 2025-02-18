import streamlit as st
import pandas as pd
import plotly.express as px
import ast


import visualisation_functions as vf
import visual_filters as vifil

# Initialisiere die Session State Variablen
if 'data' not in st.session_state:
    st.session_state['data'] = vf.load_movie_data()

# Abrufen der Daten
data = st.session_state['data']

#but_new_fig = st.button('Neue Visualisierung')


### ausweisen neuer Columns, welche dann zur auswahl stehen.
cat_columns = ['Year', 'MPA_category', 'has_oscars', 'decade', 'stars','directors','writers', 'countries_origin', 'filming_locations', 'production_companies', 'main_genres']
num_columns = ['Duration', 'Rating', 'Votes', 'budget', 'grossWorldWide', 'gross_US_Canada',
               'opening_weekend_Gross', 'wins', 'nominations', 'oscars', 'inflation_gross_opening', 'budget_inflation']

# Wenn der Button gedrückt wird, eine neue Figur hinzufügen
#if but_new_fig:
#    st.session_state['visual_count'] += 1
#    fig_id = st.session_state['visual_count']
#    st.session_state['figures'].append({'id': fig_id, 'params': {}, 'type': None})

# Anzeige der Figuren
head_container = st.container()
with head_container:
    left_col, mid_col, right_col = st.columns([0.01, 0.98, 0.01], vertical_alignment='center')
    mid_col.header(f":curry: Cook Spicy Graphs and Figures :curry:", )
    mid_col.write(":fork_and_knife: Your own Movie-Data-Visualisation")

   
    expander_filter = st.expander('Do you want some Filter to your Stew? :stew:')
    with expander_filter:
        if 'filtered_data' not in st.session_state:
            st.session_state['filtered_data'] = vifil.filter_options(data)
        st.session_state['filtered_data'] = vifil.filter_options(data)

        st.session_state['use_filtered'] = st.toggle('Apply Filters')

        if st.session_state['use_filtered']:
            data = st.session_state['filtered_data']
        else:
            data = st.session_state['data']

        

col1, col2 = st.columns([0.2,0.8])
with col1:
    plot_type = st.selectbox(f":bar_chart: Plot-Type", ['Histogram', 'Scatter', 'Violin', 'Line', 'Line Comparison'])

    if plot_type == 'Histogram':
        x_axis = st.selectbox(f":straight_ruler: X-Axis", cat_columns)
        aggregation = st.selectbox(f" :computer: Aggregation", ['count', 'sum', 'avg', 'min', 'max', 'median'])
        if aggregation == 'count':
            y_axis = st.selectbox(f":pencil2: Y-Axis", [None])
        else:
            y_axis = st.selectbox(f":pencil2: Y-Axis",num_columns)
        groupby = st.selectbox(f":books: Group By", [None] + [cat for cat in cat_columns if cat not in ['stars','directors','writers', 'countries_origin', 'filming_locations', 'production_companies', 'main_genres']] + [x_axis])



        if x_axis in ['stars','directors','writers', 'countries_origin', 'filming_locations', 'production_companies', 'main_genres'] or groupby in ['stars','directors','writers', 'countries_origin', 'filming_locations', 'production_companies', 'main_genres']:
            exploded_data = data
            exploded_data[x_axis] = exploded_data[x_axis].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
            exploded_data = exploded_data.explode(x_axis)
            
            data = exploded_data
            if aggregation == 'count':
                grouped = exploded_data[x_axis].dropna().value_counts().nlargest(20).index
            elif aggregation == 'sum':
                grouped = exploded_data.groupby(x_axis)[y_axis].sum().nlargest(20).index
            elif aggregation == 'avg':
                grouped = exploded_data.groupby(x_axis)[y_axis].mean().nlargest(20).index
            elif aggregation == 'min':
                grouped = exploded_data.groupby(x_axis)[y_axis].min().nlargest(20).index
            elif aggregation == 'max':
                grouped = exploded_data.groupby(x_axis)[y_axis].max().nlargest(20).index
            elif aggregation == 'median':
                grouped = exploded_data.groupby(x_axis)[y_axis].median().nlargest(20).index

            data = exploded_data[exploded_data[x_axis].isin(grouped)]

        fig_plot = vf.histplot(data, x_axis, y_axis, groupby, aggregation)

    elif plot_type == 'Scatter':
        x_axis = st.selectbox(f":straight_ruler: X-Axis", num_columns)
        y_axis = st.selectbox(f":pencil2: Y-Axis", num_columns)
        groupby = st.selectbox(f":books: Group By", [None] + [cat for cat in cat_columns if cat not in ['stars','directors','writers', 'countries_origin', 'filming_locations', 'production_companies', 'main_genres']])

        fig_plot = vf.scatter(data, x_axis, y_axis, groupby)

    elif plot_type == 'Violin':
        y_axis = st.selectbox(f":pencil2: Y-Axis", num_columns)
        x_axis = st.selectbox(f":straight_ruler: X-Axis", [None] + cat_columns)
        groups = st.selectbox(f":books: Group By", [None] + cat_columns)
        points = st.selectbox(f":round_pushpin: Outlier", ['all', 'outliers', 'suspectedoutliers', False])


        if x_axis in ['stars','directors','writers', 'countries_origin', 'filming_locations', 'production_companies', 'main_genres'] or groups in ['stars','directors','writers', 'countries_origin', 'filming_locations', 'production_companies', 'main_genres']:


            exploded_data = data
            exploded_data[x_axis] = exploded_data[x_axis].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
            exploded_data = exploded_data.explode(x_axis)

            chosen_options = st.multiselect('Choose option to display', options=exploded_data[x_axis].unique())

            data = exploded_data[exploded_data[x_axis].isin(chosen_options)]

        fig_plot = vf.violinplot(data, y_axis, x_axis, groups, points)

    elif plot_type == 'Line':
        x_axis = st.selectbox(f":straight_ruler: X-Axis", cat_columns)
        y_axis = st.selectbox(f":pencil2: Y-Axis", num_columns)
        aggregation = st.selectbox(f" :computer: Aggregation", ['mean', 'median', 'count', 'sum', 'max', 'min'])
        fig_plot = vf.lineplot(data, x_axis, y_axis, aggregation)

    elif plot_type == 'Line Comparison':
        x_axis = st.selectbox(f":straight_ruler: X-Axis", cat_columns)
        y_axis_1 = st.selectbox(f":pencil2: Y-Axis 1", num_columns)
        y_axis_2 = st.selectbox(f":pencil2: Y-Axis 2", num_columns)
        aggregation = st.selectbox(f" :computer: Aggregation", ['mean', 'median', 'count', 'sum', 'max', 'min'])
        fig_plot = vf.compare_graphs(data, x_axis, y_axis_1, y_axis_2, aggregation)

with col2:
    st.plotly_chart(fig_plot)

# Button zum Löschen der Figur
#if st.button(f"Löschen", key=f"delete_{fig['id']}"):
    #st.session_state['figures'] = [f for f in st.session_state['figures'] if f['id'] != fig['id']]
    #st.rerun()
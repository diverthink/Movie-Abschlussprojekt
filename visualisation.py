import streamlit as st
import pandas as pd
import plotly.express as px
import ast
import seaborn as sns
import matplotlib.pyplot as plt


import visualisation_functions as vf
import visual_filters as vifil
#import visualisation_data_cleaning




### Initialisiere die Session State Variablen
#if 'data' not in st.session_state:
#    st.session_state['data'] = vf.load_movie_data()

#if 'data' not in st.session_state:
#    st.session_state['data'] = visualisation_data_cleaning.visual_data()
def visualise_it():

    # Abrufen der Daten
    # 1️⃣ Überprüfen, ob der DataFrame existiert
    if 'df_visualisation' not in st.session_state:
        st.error("Dataset `df_visualisation` not found in session state. Please check if it was loaded properly.")
        return
    else:
        data = st.session_state['df_visualisation']

    #but_new_fig = st.button('Neue Visualisierung')


    ### ausweisen neuer Columns, welche dann zur auswahl stehen.
    cat_columns = ['Year', 'MPA', 'Nominated for Oscar', 'Decade', 'Stars','Directors','Writers', 'Origin Countries', 'Filming Locations', 'Production Companies', 'Genres']
    num_columns = ['Duration', 'Rating', 'Votes', 'Budget', 'World Wide Gross', 'North America Gross',
                   'Opening Weekend Gross', 'Award Wins', 'Award Nominations', 'Oscar Nominations', 'Inflation Adjusted Opening Gross', 'Inflation Adjusted Budget']

    # Wenn der Button gedrückt wird, eine neue Figur hinzufügen
    #if but_new_fig:
    #    st.session_state['visual_count'] += 1
    #    fig_id = st.session_state['visual_count']
    #    st.session_state['figures'].append({'id': fig_id, 'params': {}, 'type': None})

    # Anzeige der Figuren
    head_container = st.container()
    with head_container:
        left_col, mid_col, right_col = st.columns([0.25, 0.5, 0.25], vertical_alignment='center')
        mid_col.subheader("🍿 Grab some Popcorn and have fun with Plots🍿")

    expander_infos = st.expander('General Dataset Information')
    with expander_infos:
        infos = vf.essential_infos(data)
        info_columns = [collef, colmid] = st.columns(2)

        with collef:
            st.markdown("### 🎬 General Info")
            st.markdown(f"**Total Titles:** `{infos['Title_count']}`")
            st.markdown(f"**With Oscars:** `{infos['With_Oscars']}`")
            st.markdown(f"**Mean Duration:** `{infos['Duration']} min`")
            st.markdown(f"**Mean Rating:** `{infos['Rating']}` ⭐")
            st.markdown(f"**Mean Votes:** `{infos['Votes']:,}`")  # Tausender-Trennzeichen
            st.markdown(f"**Mean Budget:** `${infos['Budget']:,}`")

            st.divider()  # Trennlinie für bessere Übersicht

            st.markdown("### 💰 Box Office")
            st.markdown(f"**Mean World Wide Gross:** `${infos['World Wide Gross']:,}`")
            st.markdown(f"**Mean US & Canada Gross:** `${infos['North America Gross']:,}`")
            st.markdown(f"**Mean Gross Opening Weekend:** `${infos['Opening Weekend Gross']:,}`")

            st.divider()

            st.markdown("### 🎟 Inflation Adjusted")
            st.markdown(f"**Inflation-adjusted Opening Gross:** `${infos['Inflation Adjusted Opening Gross']:,}`")
            st.markdown(f"**Inflation-adjusted Budget:** `${infos['Inflation Adjusted Budget']:,}`")

            st.divider()

            st.markdown("### 🏆 Awards")

            st.markdown(f"**Mean Wins:** `{infos['Award Wins']}`")
            st.markdown(f"**Mean Nominations:** `{infos['Award Nominations']}`")
            st.markdown(f"**Mean Oscars:** `{infos['Oscar Nominations']}` 🏆")

        with colmid:

            st.markdown("### 📅 Time Period")
            st.markdown(f"**Number of Years:** `{infos['Year']}`")
            st.markdown(f"**Number of Decades:** `{infos['Decade']}`")

            st.divider()

            st.markdown("### 🎭 People & Production")
            st.markdown(f"**MPA Categories:** `{infos['MPA']}`")
            st.markdown(f"**Total Directors:** `{infos['Directors']}`")
            st.markdown(f"**Total Writers:** `{infos['Writers']}`")
            st.markdown(f"**Total Actors/Stars:** `{infos['Stars']}`")

            st.divider()

            st.markdown("### 🌍 Locations & Languages")
            st.markdown(f"**Total Countries:** `{infos['Origin Countries']}`")
            st.markdown(f"**Total Filming Locations:** `{infos['Filming Locations']}`")
            st.markdown(f"**Number of Languages:** `{infos['Languages']}`")

            st.divider()

            st.markdown("### 🎭 Genres")
            st.markdown(f"**Number of Genres:** `{infos['Genres']}`")

            

            st.markdown("### 🧮 Correlations")
            with st.popover("Show Correlation Matrix", use_container_width=True):
                cor_matrix = data[[col for col in data if data[col].dtype in ['int64', 'float64'] and col != 'release_date']].corr()
                
                fig, ax = plt.subplots(figsize=(10, 8))
                sns.heatmap(cor_matrix, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5, ax=ax)
                ax.set_title("Correlation Matrix")

                
                st.pyplot(fig)


    
    expander_filter = st.expander('Do you want some Filter to your Movies?🌶️')
    with expander_filter:
        if 'filtered_data' not in st.session_state:
            st.session_state['filtered_data'] = pd.DataFrame()
        st.session_state['filtered_data'] = vifil.filter_options(data)
        st.session_state['use_filtered'] = st.toggle('Apply Filters')
        if st.session_state['use_filtered']:
            data = st.session_state['filtered_data']
        else:
            data = st.session_state['df_visualisation']



    col1, col2 = st.columns([0.2,0.8])
    with col1:
        plot_type = st.selectbox(f":bar_chart: Plot-Type", ['Titles','Histogram', 'Scatter', 'Violin', 'Line', 'Line Comparison'])


        if plot_type == 'Titles':
            x_axis = 'Title'
            y_axis = st.selectbox(f":pencil2: Y-Axis",num_columns)
            best_worst = st.selectbox('👍👎 Highest or Lowest?', ['Highest', 'Lowest'])
            
            if best_worst == 'Lowest':
                sorted = data.sort_values(by=y_axis, ascending=True)
            else:
                sorted = data.sort_values(by=y_axis, ascending=False)

            top_20 = sorted.head(20)

            fig_plot = vf.show_best_films(top_20, x_axis, y_axis)

        if plot_type == 'Histogram':
            x_axis = st.selectbox(f":straight_ruler: X-Axis", cat_columns)
            aggregation = st.selectbox(f" :computer: Aggregation", ['count', 'sum', 'avg', 'min', 'max', 'median'])
            if aggregation == 'count':
                y_axis = st.selectbox(f":pencil2: Y-Axis", [None])
            else:
                y_axis = st.selectbox(f":pencil2: Y-Axis",num_columns)
            groupby = st.selectbox(f":books: Group By", [None] + [cat for cat in cat_columns if cat not in ['Stars','Directors','Writers', 'Origin Countries', 'Filming Locations', 'Production Companies', 'Genres']] + [x_axis])



            if x_axis in ['Stars','Directors','Writers', 'Origin Countries', 'Filming Locations', 'Production Companies', 'Genres'] or groupby in ['Stars','Directors','Writers', 'Origin Countries', 'Filming Locations', 'Production  Companies', 'Genres']:
                exploded_data = data
                exploded_data[x_axis] = exploded_data[x_axis].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
                exploded_data = exploded_data.explode(x_axis)

                data = exploded_data
                if aggregation == 'count':
                    grouped = exploded_data[x_axis].dropna().value_counts().nlargest(20).index
                elif aggregation == 'sum':
                    grouped = exploded_data.groupby(x_axis)[y_axis].sum().nlargest(20).index

                if aggregation in ['avg', 'min', 'max', 'median']:
                    entry_threshold = st.number_input('Include only entries above that many appearances:',min_value=1, max_value=1000)
                    valid_entries = exploded_data[x_axis].value_counts()
                    valid_entries = valid_entries[valid_entries >= entry_threshold].index
                    filtered_data = exploded_data[exploded_data[x_axis].isin(valid_entries)]
                    exploded_data = filtered_data

                    if aggregation == 'avg':
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
            groupby = st.selectbox(f":books: Group By", [None] + [cat for cat in cat_columns if cat not in ['Stars','Directors','Writers', 'Origin Countries', 'Filming Locations', 'Production Companies', 'Genres']])

            fig_plot = vf.scatter(data, x_axis, y_axis, groupby)
            if data[x_axis].dtype in ['int64', 'float64'] and data[y_axis].dtype in ['int64', 'float64']:
                correlation = data[x_axis].corr(data[y_axis])

        elif plot_type == 'Violin':
            y_axis = st.selectbox(f":pencil2: Y-Axis", num_columns)
            x_axis = st.selectbox(f":straight_ruler: X-Axis", [None] + cat_columns)
            groups = st.selectbox(f":books: Group By", [None] + cat_columns)
            points = st.selectbox(f":round_pushpin: Outlier", ['outliers','all', 'suspectedoutliers', False])

            try:
                if x_axis in ['Stars','Directors','Writers', 'Origin Countries', 'Filming Locations', 'Production Companies', 'Genres', 'Year'] or groups in ['Stars','Directors','Writers', 'Origin Countries', 'Filming Locations',   'Production   Companies', 'Genres', 'Year']:


                    exploded_data = data
                    exploded_data[x_axis] = exploded_data[x_axis].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
                    exploded_data = exploded_data.explode(x_axis)

                    chosen_options = st.multiselect('Choose option to display', options=exploded_data[x_axis].unique())

                    data = exploded_data[exploded_data[x_axis].isin(chosen_options)]


                fig_plot = vf.violinplot(data, y_axis, x_axis, groups, points)

            except Exception as e:
                col2.write(f"""Something went wrong. Can not display this combination.  
                         Error Type: {type(e).__name__}  
                        Error: {e}
                        """)


        elif plot_type == 'Line':
            x_axis = st.selectbox(f":straight_ruler: X-Axis", cat_columns)
            y_axis = st.selectbox(f":pencil2: Y-Axis", num_columns)
            aggregation = st.selectbox(f" :computer: Aggregation", ['mean', 'median', 'count', 'sum', 'max', 'min'])
            groups = st.selectbox(f":books: Group By", [None] + cat_columns)

            if x_axis in ['Stars','Directors','Writers', 'Origin Countries', 'Filming Locations', 'Production Companies', 'Genres']:

                exploded_data = data
                exploded_data[x_axis] = exploded_data[x_axis].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
                exploded_data = exploded_data.explode(x_axis)

                chosen_options = st.multiselect('Choose option to display', options=exploded_data[x_axis].unique())

                data = exploded_data[exploded_data[x_axis].isin(chosen_options)]

            if groups != None:
                exploded_data = data
                exploded_data[groups] = exploded_data[groups].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
                exploded_data = exploded_data.explode(groups)

                chosen_options = st.multiselect('Choose option to display', options=exploded_data[groups].unique())

                data = exploded_data[exploded_data[groups].isin(chosen_options)]
                fig_plot = vf.multiple_lineplot(data, x_axis, y_axis, aggregation, groups)
                
            else:    
                fig_plot = vf.lineplot(data, x_axis, y_axis, aggregation)

        elif plot_type == 'Line Comparison':
            x_axis = st.selectbox(f":straight_ruler: X-Axis", ['Year'])
            y_axis_1 = st.selectbox(f":pencil2: Y-Axis 1", num_columns)
            y_axis_2 = st.selectbox(f":pencil2: Y-Axis 2", [col for col in num_columns if col != y_axis_1])
            aggregation = st.selectbox(f" :computer: Aggregation", ['mean', 'median', 'count', 'sum'])



            fig_plot = vf.compare_graphs(data, x_axis, y_axis_1, y_axis_2, aggregation)

    with col2:
        try:
            st.plotly_chart(fig_plot)

        except Exception as e:
            st.write("Something went wrong")
            st.write(f"""Can not display plot.  
                         Error Type: {type(e).__name__}  
                        Error: {e}
                        """)
        if plot_type == 'Scatter':
            st.write(f'Correlation: {correlation:.2f}')
    # Button zum Löschen der Figur
    #if st.button(f"Löschen", key=f"delete_{fig['id']}"):
        #st.session_state['figures'] = [f for f in st.session_state['figures'] if f['id'] != fig['id']]
        #st.rerun()
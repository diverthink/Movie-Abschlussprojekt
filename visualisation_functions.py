import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os



def load_movie_data(path=None):
    """Lädt den bereinigten Film-DataFrame aus einer CSV-Datei."""
    if path is None:
        # Dynamischer Pfad relativ zum Verzeichnis der Datei
        script_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(script_dir, "Datasets", "df_new_movies_cleaned.csv")
    
    return pd.read_csv(path)


def histplot(df, x_axis='Year', y_axis=None, groupby=None, aggregationtype=None):
    '''
    Erstellt ein Histogram/Barplot mit den gegebenen Daten. Moegliche Werte fuer aggregationtype = ['count', 'sum', 'avg', 'min', 'max', 'median', 'max', 'min']
    groupby = kategorische column
    '''

    if aggregationtype == 'median':
            median_data = df.groupby(x_axis)[y_axis].median().reset_index()
            fig = px.bar(median_data, x=x_axis, y=y_axis, text_auto=True)
    else:
        fig = px.histogram(data_frame=df, x=x_axis, y=y_axis, color=groupby, histfunc=aggregationtype, text_auto=True)
    #if y_axis:
    #    fig = px.histogram(data_frame=df, x=x_axis, y=y_axis, text_auto=True)
#
    #elif groupby:
    #    fig = px.histogram(data_frame=df, x=x_axis, color=groupby, text_auto=True)
    #    
    #else:
    #    fig = px.histogram(data_frame=df, x=x_axis, text_auto=True)

    fig.update_traces(textfont_size=12, textangle=0, cliponaxis = False)
    
    return fig


def scatter(df, x_axis, y_axis, groupby=None):
    '''Erstellt einen Scatterplot mit den gegebenen Daten.'''

    fig = px.scatter(data_frame=df, x=x_axis, y=y_axis, color=groupby, hover_name='Title', hover_data=['Year', 'Duration', 'Rating', 'wins', 'nominations', 'oscars', 'MPA_category', 'main_genres', 'directors', 'writers', 'stars', 'opening_weekend_Gross'])

    #fig.update_traces(textfont_size=12, textangle=0, cliponaxis = False)
    return fig


def violinplot(df, y_axis, x_axis = None, groups=None, points='all'):

    '''
    Erstellt ein Violinplot mit den gegebenen Daten.

    Moegliche Werte fuer points:
    "all" → Zeigt alle Datenpunkte als Jitter-Punkte ausserhalb der Violine an.
    "outliers" → Zeigt nur Ausreißer (Datenpunkte außerhalb des Interquartilbereichs) an.
    "suspectedoutliers" → Zeigt Punkte an, die als potenzielle Ausreißer gelten.
    "False" oder False → Zeigt keine Punkte an.
    '''

    fig = px.violin(df, y=y_axis, x=x_axis, color=groups, box=True, points=points, hover_data=['Title', 'Year', 'Duration', 'Rating', 'wins', 'nominations', 'oscars', 'MPA_category', 'main_genres', 'directors', 'writers', 'stars'])
    

    return fig

def lineplot(data, x_axis, y_axis, aggregation_type):

    '''
    Erstellt ein Liniendiagramm mit den angegebenen aggregierten Spalten.
    aggregation_type = ['count', 'sum', 'mean', 'min', 'max', 'median']
    '''

    if aggregation_type == 'mean':
        aggregated = data.groupby(x_axis, as_index=False)[y_axis].mean()

    elif aggregation_type == 'count':
        aggregated = data.groupby(x_axis, as_index=False)[y_axis].count()

    elif aggregation_type == 'median':
        aggregated = data.groupby(x_axis, as_index=False)[y_axis].median()

    elif aggregation_type == 'sum':
        aggregated = data.groupby(x_axis, as_index=False)[y_axis].sum()

    elif aggregation_type == 'min':
        aggregated = data.groupby(x_axis, as_index=False)[y_axis].min()

    elif aggregation_type == 'max':
        aggregated = data.groupby(x_axis, as_index=False)[y_axis].max()
    
    
    if data[x_axis].dtype == 'int64' or data[x_axis].dtype == 'float64':
        aggregated = aggregated.sort_values(by=x_axis, ascending=True)
    
    fig = px.line(aggregated, x=x_axis, y=y_axis, markers=True)
    fig.update_layout(xaxis_title=x_axis, yaxis_title=y_axis)
    
    return fig



def compare_graphs(data: pd.DataFrame, x_axis: str, y_axis_1: str, y_axis_2: str, aggregate_type='median'):

    '''
    Erstellt ein Liniendiagramm in dem zwei aggregierte Werte auf verschiedenen Skalen miteinander verglichen werden.
    Moegliche aggregate_type = ['count', 'sum', 'mean', 'min', 'max', 'median', 'max', 'min']
    Bitte beachten, die aggregierung ist fuer die Vergleichbarkeit bei beiden Columns gleich.
    '''

    # Ergebnisse pro Jahr berechnen
    if aggregate_type == 'median':
        aggregated_data = data.groupby(x_axis, as_index=False)[[y_axis_1, y_axis_2]].median()
    elif aggregate_type == 'mean':
        aggregated_data = data.groupby(x_axis, as_index=False)[[y_axis_1, y_axis_2]].mean()
    elif aggregate_type == 'sum':
        aggregated_data = data.groupby(x_axis, as_index=False)[[y_axis_1, y_axis_2]].sum()
    elif aggregate_type == 'count':
        aggregated_data = data.groupby(x_axis, as_index=False)[[y_axis_1, y_axis_2]].count()

    elif aggregate_type == 'min':
        aggregated_data = data.groupby(x_axis, as_index=False)[y_axis_1, y_axis_2].min()

    elif aggregate_type == 'max':
        aggregated_data = data.groupby(x_axis, as_index=False)[y_axis_1, y_axis_2].max()

    # Erstelle den Plot mit den errechneten Werten
    fig_test = go.Figure()

    fig_test.add_trace(go.Scatter(x=aggregated_data[x_axis], y=aggregated_data[y_axis_1], 
                                  mode="lines", name=f"{aggregate_type} {y_axis_1}", line=dict(dash="dash"), yaxis="y1"))

    fig_test.add_trace(go.Scatter(x=aggregated_data[x_axis], y=aggregated_data[y_axis_2], 
                                  mode="lines", name=f"{aggregate_type} {y_axis_2}", line=dict(dash="dot"), yaxis="y2"))

    # Titel & Achsenbeschriftung setzen
    fig_test.update_layout(title=f"{aggregate_type.capitalize()} {y_axis_1.capitalize()} vs. {aggregate_type.capitalize()} {y_axis_2.capitalize()} per {x_axis.capitalize()}",
                           xaxis_title=f"{x_axis}",
                           yaxis=dict(title=f"{y_axis_1.capitalize()}", side="left"),
                           yaxis2=dict(title=f"{y_axis_2.capitalize()}", overlaying="y", side="right", showgrid=False),
                           legend_title="Kategorie")

    return fig_test
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os


import filter_functions


def _assign_decade(year):
    '''Assigns a decade to the film based on the release year.'''
    decades = {'60s': range(1960, 1970),
               '70s': range(1970, 1980),
               '80s': range(1980, 1990),
               '90s': range(1990, 2000),
               '00s': range(2000, 2010),
               '2010s': range(2010, 2020),
               '2020s': range(2020, 2030)}

    for decade, years in decades.items():
        if year in years:
            return decade

    return 'Unknown'



def _has_oscars(x):
    if x == 0:
        return 0
    else:
        return 1


def _inflation(year, gross, base_year):
    '''Enthaelt US-Inflationsdaten von 1960-2024 und gibt den inflationsausgeglichenen Betrag zum Vergleichsjahr zurueck.'''
    cpi_data = {
        1960: 29.55, 1961: 29.9, 1962: 30.15, 1963: 30.65, 1964: 31.05, 
        1965: 31.45, 1966: 32.2, 1967: 33.15, 1968: 34.0, 1969: 35.05, 
        1970: 38.0, 1971: 40.2, 1972: 41.4, 1973: 43.3, 1974: 46.2, 
        1975: 52.3, 1976: 56.4, 1977: 60.4, 1978: 63.4, 1979: 69.2, 
        1980: 80.6, 1981: 90.2, 1982: 94.4, 1983: 99.1, 1984: 102.5, 
        1985: 106.2, 1986: 109.4, 1987: 112.6, 1988: 116.0, 1989: 121.5, 
        1990: 130.7, 1991: 135.7, 1992: 139.7, 1993: 143.2, 1994: 146.0, 
        1995: 151.6, 1996: 154.6, 1997: 160.0, 1998: 162.0, 1999: 165.0, 
        2000: 171.3, 2001: 175.8, 2002: 179.9, 2003: 183.5, 2004: 188.2, 
        2005: 192.8, 2006: 199.1, 2007: 203.2, 2008: 214.0, 2009: 215.1, 
        2010: 218.0, 2011: 221.6, 2012: 229.1, 2013: 232.8, 2014: 235.4, 
        2015: 236.8, 2016: 238.5, 2017: 243.2, 2018: 249.0, 2019: 254.4, 
        2020: 259.0, 2021: 267.8, 2022: 286.2, 2023: 303.5, 2024: 312.0  # 2024 als Referenz
    }

    return (gross / cpi_data[year]) * cpi_data[base_year]


def add_decade_inflation_hasoscars():

    '''Fuegt neue Spalten hinzu. Die Jahre werden Dekaden zugeordnet. Eine Spalte has_oscars sagt aus, dass der Film fuer einen Oscar nominiert wurde. Spalten mit Kosten und oder Einspielergebnissen werden durch inflationsbereinigte Spalten ergaenzt. Dadurch koennen diese Waehrungsdaten vergleichbar gemacht werden.'''

    def load_movie_data(path=None):
        """Lädt den bereinigten Film-DataFrame aus einer CSV-Datei."""
        if path is None:
            # Dynamischer Pfad relativ zum Verzeichnis der Datei
            script_dir = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(script_dir, "Datasets", "df_movie_for_streamlit.csv")
        return pd.read_csv(path)
    
    data = load_movie_data()

    data['decade'] = data['Year'].apply(_assign_decade)

    data['has_oscars'] = data['oscars'].apply(_has_oscars)


    data['opening_weekend_inflation'] = data.apply(lambda row: _inflation(row['Year'], row['opening_weekend_Gross'], 2024), axis=1)

    data['gross_US_Canada_inflation'] = data.apply(lambda row: _inflation(row['Year'], row['gross_US_Canada'], 2024), axis=1)

    data['gross_world_wide_inflation'] = data.apply(lambda row: _inflation(row['Year'], row['grossWorldWide'], 2024), axis=1)
    
    data['budget_inflation'] = data.apply(lambda row: _inflation(row['Year'], row['budget'], 2024), axis=1)

    return data


def histplot(df, x_axis, y_axis=None, groupby=None, aggregationtype=None):
    '''
    Erstellt ein Histogram/Barplot mit den gegebenen Daten. Moegliche Werte fuer aggregationtype = ['count', 'sum', 'avg', 'min', 'max']
    groupby = kategorische column
    '''

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

    fig = px.scatter(data_frame=df, x=x_axis, y=y_axis, color=groupby, hover_name='Title', hover_data=['Title', 'Year', 'Duration', 'MPA', 'Rating', 'Votes', 'budget', 'grossWorldWide', 'opening_weekend_Gross', 'wins', 'nominations', 'oscars', 'opening_weekend_inflation'])

    #fig.update_traces(textfont_size=12, textangle=0, cliponaxis = False)
    return fig


def violinplot(df, y_axis, x_axis = None, groups=None, points='all'):

    '''
    Erstellt ein Violinplot mit den gegebenen Daten.

    Moegliche Werte fuer points:
    "all" → Zeigt alle Datenpunkte als Jitter-Punkte innerhalb der Violine an.
    "outliers" → Zeigt nur Ausreißer (Datenpunkte außerhalb des Interquartilbereichs) an.
    "suspectedoutliers" → Zeigt Punkte an, die als potenzielle Ausreißer gelten.
    "False" oder False → Zeigt keine Punkte an.
    '''

    fig = px.violin(df, y=y_axis, x=x_axis, color=groups, box=True, points=points, hover_data=df.columns)
    

    return fig

def lineplot(data, x_axis, y_axis, aggregation_type):

    '''
    Erstellt ein Liniendiagramm mit den angegebenen aggregierten Spalten.
    aggregation_type = ['mean', 'median', 'count', 'sum']
    '''

    if aggregation_type == 'mean':
        aggregated = data.groupby(x_axis, as_index=False)[y_axis].mean()

    elif aggregation_type == 'count':
        aggregated = data.groupby(x_axis, as_index=False)[y_axis].count()

    elif aggregation_type == 'median':
        aggregated = data.groupby(x_axis, as_index=False)[y_axis].median()

    elif aggregation_type == 'sum':
        aggregated = data.groupby(x_axis, as_index=False)[y_axis].sum()
    
    if data[x_axis].dtype == 'int64' or data[x_axis].dtype == 'float64':
        aggregated = aggregated.sort_values(by=x_axis, ascending=True)
    
    fig = px.line(aggregated, x=x_axis, y=y_axis, markers=True)
    fig.update_layout(xaxis_title=x_axis, yaxis_title=y_axis)
    
    return fig



def compare_graphs(data: pd.DataFrame, x_axis: str, y_axis_1: str, y_axis_2: str, aggregate_type='median'):

    '''
    Erstellt ein Liniendiagramm in dem zwei aggregierte Werte auf verschiedenen Skalen miteinander verglichen werden.
    Moegliche aggregate_type = ['mean', 'median', 'count', 'sum']
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
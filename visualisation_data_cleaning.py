import pandas as pd
import os
import ast
import numpy as np

def concatenate_data():
    all_data = []
    script_dir = os.getcwd()  # Pfad zum Skript

    for year in range(1960, 2025):
        data_path = os.path.join(script_dir, 'Data', f'{year}', f'merged_movies_data_{year}.csv')

        if os.path.exists(data_path):
            print(f"Lese Datei: {data_path}")  # Debugging-Ausgabe
            df = pd.read_csv(data_path)
            all_data.append(df)
        else:
            print(f"❌ Datei nicht gefunden: {data_path}")  # Debugging-Ausgabe

    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        print(final_df.head(5))
        return final_df
    else:
        print("⚠️ Keine Dateien gefunden!")
        return pd.DataFrame()


def get_id(link):
    part = link.split("title/")[1].split("/")[0]
    return part

#def duration_to_minutes(duration):
#    
#    if pd.isna(duration):
#        return 0
#
#
#    # Initialisiere Stunden und Minuten
#    hours, minutes = 0, 0
#
#    # Wenn 'h' im String ist, extrahiere die Stunden
#    if 'h' in duration:
#        hours = int(duration.split('h')[0].strip())
#
#    # Wenn 'm' im String ist, extrahiere die Minuten
#    if 'm' in duration:
#        # Split an 'h' und nimm den rechten Teil, falls vorhanden
#        minutes_part = duration.split('h')[-1]
#        minutes = int(minutes_part.replace('m', '').strip())
#
#    return hours * 60 + minutes

#def correct_votes(votes):
#    if pd.isna(votes):
#        return votes
#
#    if 'K' in votes:
#        # Entferne 'K' und multipliziere den Wert mit 1000
#        votes_correct = float(votes.replace('K', '')) * 1000
#    # Falls 'M' im Wert enthalten ist
#    elif 'M' in votes:
#        # Entferne 'M' und multipliziere den Wert mit 1000000
#        votes_correct = float(votes.replace('M', '')) * 1000000
#    else:
#        # Falls keine der beiden Einheiten vorhanden ist, wird der Wert als Ganzzahl übernommen
#        votes_correct = int(votes)
#    
#    return int(votes_correct)

## 3. Listen-Spalten sauber formatieren
#def list_columns_format(df):
#    
#    list_columns = ['writers', 'stars', 'genres', 'countries_origin',
#                    'filming_locations', 'production_companies']
#    for col in list_columns:
#        df[col] = df[col].apply(lambda x: eval(x) if isinstance(x, str) else x)
#    
#    return df

def mpa_mapping(final_df):
    # Mapping der MPA-Kategorien
    mpa_categories = {
        "All Ages (+0)": ['G', 'TV-G', 'TV-Y', 'TV-Y7', 'K-A', 'Approved'],
        "Parental Guidance (+13)": ['PG', 'PG-13', 'M/PG', 'TV-PG', 'TV-13', 'TV-14'],
        "Mature Audiences (+18)": ['R', 'MA-17', 'TV-MA', 'NC-17', 'X'],
        "Not Rated/Other": ['Not Rated', 'Unrated', 'Passed', 'GP']
    }

    # Mapping umkehren für schnelles Zuordnen
    mpa_mapping = {}
    for category, labels in mpa_categories.items():
        for label in labels:
            mpa_mapping[label] = category

    # Spalte in allgemeine Kategorien umwandeln
    final_df['MPA_category'] = final_df['MPA'].map(mpa_mapping)

    # Fehlende Werte in `MPA_category` mit "Unknown" auffüllen
    final_df['MPA_category'].fillna("Unknown", inplace=True)

    # Alte `MPA`-Spalte entfernen
    final_df.drop(columns=['MPA'], inplace=True)

    return final_df


def replace_na_with_median(df, columns):
    for column in columns:
        # Group by 'Year' und berechne den Median pro Jahr
        df[column] = df.groupby('Year')[column].transform(lambda x: x.fillna(x.median()))
    
    return df

def inflation(year, gross, base_year):

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


def has_oscars(x):
    if x == 0:
        return 0
    else:
        return 1
    


def assign_decade(year):

    decades = {'1960s': range(1960, 1970),
               '1970s': range(1970, 1980),
               '1980s': range(1980, 1990),
               '1990s': range(1990, 2000),
               '2000s': range(2000, 2010),
               '2010s': range(2010, 2020),
               '2020s': range(2020, 2030)}

    for decade, years in decades.items():
        if year in years:
            return decade

    return 'Unknown'


genre_categories = {
    "Action": [
        'Action', 'Action Epic', 'B-Action', 'Car Action', 'Gun Fu', 
        'Martial Arts', 'One-Person Army Action', 'Kung Fu', 
        'Samurai', 'Sword & Sandal', 'Swashbuckler', 'Buddy Cop', 
        'Spy'
    ],
    "Adventure": [
        'Adventure', 'Adventure Epic', 'Animal Adventure', 'Desert Adventure', 
        'Dinosaur Adventure', 'Globetrotting Adventure', 'Jungle Adventure', 
        'Mountain Adventure', 'Sea Adventure', 'Space Sci-Fi', 'Urban Adventure', 
        'Quest', 'Survival', 'Road Trip'
    ],
    "Horror": [
        'Horror', 'B-Horror', 'Monster Horror', 'Psychological Horror', 
        'Slasher Horror', 'Supernatural Horror', 'Teen Horror', 
        'Vampire Horror', 'Werewolf Horror', 'Zombie Horror', 
        'Splatter Horror', 'Found Footage Horror', 'Folk Horror', 
        'Giallo', 'Kaiju', 'Witch Horror', 'Body Horror'
    ],
    "Thriller": [
        'Thriller', 'Conspiracy Thriller', 'Political Thriller', 'Erotic Thriller', 
        'Psychological Thriller', 'Serial Killer', 'Heist', 'Crime', 'Cop Drama', 
        'Drug Crime', 'Gangster', 'Police Procedural', 'Legal Thriller', 
        'Suspense Mystery'
    ],
    "Science-Fiction": [
        'Sci-Fi', 'Sci-Fi Epic', 'Dystopian Sci-Fi', 'Cyber Thriller', 
        'Cyberpunk', 'Steampunk', 'Alien Invasion', 'Artificial Intelligence', 
        'Time Travel', 'Mecha', 'Superhero'
    ],
    "Fantasy": [
        'Fantasy', 'Dark Fantasy', 'Fantasy Epic', 'Sword & Sorcery', 
        'Supernatural Fantasy', 'Fairy Tale', 'Isekai', 'Slice of Life', 
        'Teen Fantasy'
    ],
    "Comedy": [
        'Comedy', 'Dark Comedy', 'Farce', 'High-Concept Comedy', 'Quirky Comedy', 
        'Raunchy Comedy', 'Romantic Comedy', 'Screwball Comedy', 'Slapstick', 
        'Stoner Comedy', 'Teen Comedy', 'Buddy Comedy', 'Parody', 'Satire', 
        'Sketch Comedy', 'Mockumentary', 'Sitcom'
    ],
    "Drama": [
        'Drama', 'Costume Drama', 'Cop Drama', 'Crime', 'Docudrama', 'Family', 
        'Historical Epic', 'Legal Drama', 'Medical Drama', 'Period Drama', 
        'Political Drama', 'Prison Drama', 'Psychological Drama', 'Showbiz Drama', 
        'Teen Drama', 'Tragedy', 'Workplace Drama', 'Financial Drama', 
        'Korean Drama', 'Biography', 'Dark Romance'
    ],
    "Romantic": [
        'Romance', 'Feel-Good Romance', 'Holiday Romance', 'Teen Romance', 
        'Tragic Romance', 'Steamy Romance', 'Romantic Epic'
    ],
    "Music & Dance": [
        'Musical', 'Classic Musical', 'Pop Musical', 'Rock Musical', 
        'Concert', 'Music', 'Jukebox Musical', 'Music Documentary'
    ],
    "Sport": [
        'Baseball', 'Basketball', 'Boxing', 'Extreme Sport', 'Football', 
        'Motorsport', 'Soccer', 'Sport', 'Sports Documentary', 'Water Sport'
    ],
    "Crime": [
        'True Crime', 'Heist', 'Drug Crime', 'Gangster', 'Hard-boiled Detective', 
        'Bumbling Detective', 'Cozy Mystery'
    ],
    "Documentary": [
        'Documentary', 'Crime Documentary', 'Food Documentary', 
        'Military Documentary', 'Nature Documentary', 
        'Political Documentary', 'Science & Technology Documentary', 
        'Travel Documentary', 'Faith & Spirituality Documentary', 'History Documentary', 
        'Game Show', 'News', 'Reality TV', 'Talk Show'
    ],
    "Western": [
        'Western', 'Contemporary Western', 'Classical Western', 
        'Spaghetti Western', 'Western Epic'
    ],
    "Animation": [
        'Animation', 'Anime', 'Hand-Drawn Animation', 'Stop Motion Animation', 
        'Adult Animation', 'Computer Animation'
    ],
    "Children & Family": [
        'Family', 'Holiday Family', 'Teen Adventure', 'Coming-of-Age', 
        'Holiday', 'Holiday Animation', 'Holiday Comedy'
    ],
    "Historical": [
        'Historical Epic', 'History', 'Period Drama'
    ],
    "War": [
        'War', 'War Epic'
    ],
    "Mystery": [
        'Mystery', 'Whodunnit'
    ],
    "Others": [
        'Epic', 'Stand-Up', 'Iyashikei', 'Josei', 'Seinen', 'Shōjo', 
        'Shōnen', 'Soap Opera'
    ]
}

def map_genres_to_categories(genres, mapping):
    if isinstance(genres, list):  # Sicherstellen, dass es sich um eine Liste handelt
        categories = {category for genre in genres for category, subgenres in mapping.items() if genre in subgenres}
        return list(categories) if categories else ["Unknown"]
    return ["Unknown"]


## Funktion zur Zuordnung von Genres zu mehreren Hauptkategorien
#def assign_main_genres(genre_list, genre_categories):
#    main_genres = []  # Liste für alle Hauptkategorien des Films
#    # Für jedes Genre im Film prüfen, ob es in einer der Hauptkategorien vorhanden ist
#    for category, subgenres in genre_categories.items():
#        if any(genre in subgenres for genre in genre_list):
#            main_genres.append(category)  # Hinzufügen der passenden Kategorie zur Liste
#    # Falls keine Hauptkategorie zugeordnet wurde, in 'Sonstiges' hinzufügen
#    if not main_genres:
#        main_genres.append('Unknown')
#    return main_genres


def extract_title(title):
    stripped_title = title.split('. ')[1]
    return stripped_title



## clean_dataframe Would replace Duration, Votes, and strings


def clean_dataframe(df):
    # 1. Duration umrechnen
    def duration_to_minutes(duration):
        if isinstance(duration, str):
            hours = int(duration.split('h')[0]) if 'h' in duration else 0
            minutes = int(duration.split('m')[0].split()[-1]) if 'm' in duration else 0
            return hours * 60 + minutes
        return np.nan  # Rückgabe von NaN statt None

    df['Duration'] = df['Duration'].apply(duration_to_minutes)

    # 2. Votes bereinigen
    def votes_to_int(votes):
        if isinstance(votes, str):
            if 'K' in votes:
                return int(float(votes.replace('K', '')) * 1e3)
            elif 'M' in votes:
                return int(float(votes.replace('M', '')) * 1e6)
            else:
                return int(votes)
        return np.nan

    df['Votes'] = df['Votes'].apply(votes_to_int)

    # 3. Sicheres Parsen von Listen-Spalten
    list_columns = ['writers', 'directors', 'stars', 'genres', 'countries_origin',
                    'filming_locations', 'production_companies', 'Languages']
    for col in list_columns:
        df[col] = df[col].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)

    # 4. Strings explizit als string speichern
    string_columns = ['id', 'Title', 'Movie Link', 'MPA']
    for col in string_columns:
        df[col] = df[col].astype('string')

    return df



def visual_data():

    final_df = concatenate_data()

    final_df['id'] = final_df['Movie Link'].apply(get_id)

    final_df = clean_dataframe(final_df)

    final_df = mpa_mapping(final_df)

    columns_to_replace = ['budget', 'grossWorldWide', 'gross_US_Canada', 'opening_weekend_Gross']
    final_df = replace_na_with_median(final_df, columns_to_replace)

    final_df['inflation_gross_opening'] = final_df.apply(lambda row: inflation(row['Year'], row['opening_weekend_Gross'], 2024), axis=1)
    final_df['budget_inflation'] = final_df.apply(lambda row: inflation(row['Year'], row['budget'], 2024), axis=1)


    final_df['has_oscars'] = final_df['oscars'].apply(has_oscars)

    # Neue Spalte fuer Jahrzente
    final_df['decade'] = final_df['Year'].apply(assign_decade)

    # Anwenden der Funktion auf jedes Genre
    final_df['main_genres'] = final_df['genres'].apply(lambda x: map_genres_to_categories(x, genre_categories))
    #final_df['main_genres'] = final_df['genres'].apply(lambda x: assign_main_genres(x, genre_categories))

    #drop die alte genre spalte
    final_df = final_df.drop('genres', axis=1)

    final_df['Title'] = final_df['Title'].apply(extract_title)


    ### Umbenennen der Spalten fuer bessere Lesbarkeit
    column_mapping = {
    'Title': 'Title',
    'Movie Link': 'Movie Link',
    'Year': 'Year',
    'Duration': 'Duration',
    'Rating': 'Rating',
    'Votes': 'Votes',
    'Description': 'Description',
    'budget': 'Budget',
    'grossWorldWide': 'World Wide Gross',
    'gross_US_Canada': 'North America Gross',
    'opening_weekend_Gross': 'Opening Weekend Gross',
    'directors': 'Directors',
    'writers': 'Writers',
    'stars': 'Stars',
    'countries_origin': 'Origin Countries',
    'filming_locations': 'Filming Locations',
    'production_companies': 'Production Companies',
    'Languages': 'Languages',
    'wins': 'Award Wins',
    'nominations': 'Award Nominations',
    'oscars': 'Oscar Nominations',
    'release_date': 'release_date',
    'id': 'id',
    'MPA_category': 'MPA',
    'inflation_gross_opening': 'Inflation Adjusted Opening Gross',
    'budget_inflation': 'Inflation Adjusted Budget',
    'has_oscars': 'Nominated for Oscar',
    'decade': 'Decade',
    'main_genres': 'Genres'
}

    final_df = final_df.rename(columns=column_mapping)
    # df als csv abspeichern
    final_df.to_csv(os.path.join('Datasets', 'df_visualisation_data_cleaned.csv'))

    return final_df

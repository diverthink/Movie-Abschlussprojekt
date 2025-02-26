# Modulimport

import os
import pandas as pd
import numpy as np
import ast
from sklearn.preprocessing import MultiLabelBinarizer, OneHotEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix
import pickle



print("")
print("🔢🔢🔢 Bitte etwas Geduld. Es werden nun alle relevanten Datasets erstellt und gespeichert. Dies kann wenige Minuten dauern. 🚨🚨🚨Bitte warten bis in der Konsole folgendes steht:")
print("")
print("Alle Schritte erfolgreich abgeschlossen. Bitte main.py starten (streamlit run main.py)")

# CSV-Datei laden (Original-Datensatz von Kaggle)
df_movies = pd.read_csv('Datasets/kaggle_original_dataset.csv')

# DataFrame bereinigen in einer Funktion (wurde vorher alles in einem .ipynb getested)
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

df_movie_filter = clean_dataframe(df_movies)

# Relevante Spalten auswählen
df_movie_filter = df_movie_filter[['Title', 'Year', 'Votes', 'Duration', 'Rating', 'genres', 'stars', 'directors', 'MPA', 'production_companies', 'writers', 'Movie Link', 'countries_origin', 'Languages']].copy()


# Fehlende Werte in MPA-Spalte direkt mit "Not Rated" ersetzen
df_movie_filter['MPA'] = df_movie_filter['MPA'].fillna("Not Rated")

# MPA-Kategorien festlegen und Anwenden, werden sonst zu viele für das Encoding und macht auch kein Sinn
mpa_categories = {
    "All Ages (+0)": ['G', 'TV-G', 'TV-Y', 'TV-Y7', 'K-A', 'Approved'],
    "Parental Guidance (+13)": ['PG', 'PG-13', 'M/PG', 'TV-PG', 'TV-13', 'TV-14'],
    "Mature Audiences (+18)": ['R', 'MA-17', 'TV-MA', 'NC-17', 'X'],
    "Not Rated/Unknown": ['Not Rated', 'Unrated', 'Passed', 'GP']
}

# Mapping umkehren
mpa_mapping = {label: category for category, labels in mpa_categories.items() for label in labels}

# MPA-Kategorisierung
df_movie_filter['MPA_category'] = df_movie_filter['MPA'].map(mpa_mapping)


# Alte MPA-Spalte entfernen
df_movie_filter.drop(columns=['MPA'], inplace=True)

# Spaltennamen klein schreiben, damit es Einheitlich wird...
df_movie_filter.columns = df_movie_filter.columns.str.lower()

# Ähnlich wie bei MPA Kategorien, dass ganze für das Genre. Alle unique genres wurden sich vorher ausgeben lassen und darauf basierend die "Main"-genres gebildet
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


# Genres zu Hauptkategorien zuordnen
def map_genres_to_categories(genres, mapping):
    if isinstance(genres, list):  # Sicherstellen, dass es sich um eine Liste handelt
        categories = {category for genre in genres for category, subgenres in mapping.items() if genre in subgenres}
        return list(categories) if categories else ["Unknown"]
    return ["Unknown"]

df_movie_filter['genres'] = df_movie_filter['genres'].apply(lambda x: map_genres_to_categories(x, genre_categories))

df_movie_filter.to_csv('Datasets/df_movie_filter.csv')

print("")
print("✅ Dataset 1/3 wurde als 'df_movie_filter.csv' gespeichert! Als nächstes startet das Encoding, bitte nicht Abbrechen ...")

df_movie_pre_encoding = df_movie_filter.copy()
df_movie_pre_encoding.dropna(inplace=True)
df_movie_pre_encoding = df_movie_pre_encoding[df_movie_pre_encoding['votes'] >= 100]
df_movie_pre_encoding.reset_index(drop=True, inplace=True)  # Index neu setzen



# Für das Encoden wurde Top-K Ansatz gewäjlt, weil sonst einfach eine Tabrelle > 80k Spalten raus gekommen wäre.
top_k = {
    'directors': 500,       # Top 500 Regisseure
    'writers': 500,        # Top 1000 Autoren
    'stars': 3000,          # Top 1000 Schauspieler
    'genres': None,         # Alle Genres (keine Reduktion nötig)
    'countries_origin': 50, # Top 20 Länder
    'languages': 20         # Top 20 Sprachen
}


# 1. Multi-Label-Spalten (genres, countries_origin, languages)
multi_label_cols = ['genres', 'countries_origin', 'languages']
for col in multi_label_cols:
    mlb = MultiLabelBinarizer()
    if top_k[col]:  # Top-K Filtern
        top_values = df_movie_pre_encoding[col].explode().value_counts().index[:top_k[col]]
        df_movie_pre_encoding[col] = df_movie_pre_encoding[col].apply(lambda x: [v for v in x if v in top_values])

    # Multi-Hot-Encoding
    encoded = pd.DataFrame(mlb.fit_transform(df_movie_pre_encoding[col]), columns=mlb.classes_)
    df_movie_pre_encoding = pd.concat([df_movie_pre_encoding, encoded], axis=1)
    df_movie_pre_encoding.drop(columns=[col], inplace=True)


# 2. Textbasierte Spalten mit TF-IDF (directors, writers, stars, production_companies)
text_cols = ['directors', 'writers', 'stars', 'production_companies']
for col in text_cols:
    # Listen in Strings umwandeln, wobei die Namen durch Kommas getrennt werden
    df_movie_pre_encoding[col] = df_movie_pre_encoding[col].apply(lambda x: ','.join(x))
    
    # TF-IDF anwenden, wobei vollständige Namen als Einheit behandelt werden
    tfidf = TfidfVectorizer(max_features=top_k.get(col, 100), token_pattern=r'[^,]+')  # Trennung anhand von Kommas
    tfidf_matrix = tfidf.fit_transform(df_movie_pre_encoding[col])
    
    # DataFrame mit den neuen Features erstellen
    tfidf_df = pd.DataFrame(tfidf_matrix.toarray(), columns=[f"{col}_{feat}" for feat in tfidf.get_feature_names_out()])
    
    # Hinzufügen der kodierten Spalten und Löschen der Original-Spalte
    df_movie_pre_encoding = pd.concat([df_movie_pre_encoding, tfidf_df], axis=1)
    df_movie_pre_encoding.drop(columns=[col], inplace=True)


# One-Hot-Encoding für die Spalte mpa_category
ohe = OneHotEncoder(sparse_output=False, drop='first')  # Aktualisiert: sparse_output anstelle von sparse
mpa_encoded = ohe.fit_transform(df_movie_pre_encoding[['mpa_category']])
mpa_encoded_df = pd.DataFrame(mpa_encoded, columns=[f"mpa_{cat}" for cat in ohe.categories_[0][1:]])

# Kombinieren mit dem ursprünglichen DataFrame
df_movie_pre_encoding = pd.concat([df_movie_pre_encoding, mpa_encoded_df], axis=1)
df_movie_pre_encoding.drop(columns=['mpa_category'], inplace=True)


# Ausgabe der finalen Spaltenanzahl
print(f"✅ Encoding Complete. Anzahl der Spalten nach vollständigem Encoding: {df_movie_pre_encoding.shape[1]}")

df_test_similarity = df_movie_pre_encoding.copy()
df_test_similarity.to_csv("Datasets/df_test_similarity.csv", index=False)
print("")
print("✅ Dataset 2/3 wurde als 'df_test_similarity.csv' gespeichert! Es folgt die Skalierung ...")


# Numerische Spalten, die skaliert werden sollen
num_cols = ['year', 'duration', 'rating', 'votes']

# StandardScaler anwenden
scaler = StandardScaler()
df_test_similarity_scaled = df_test_similarity.copy()
df_test_similarity_scaled[num_cols] = scaler.fit_transform(df_test_similarity_scaled[num_cols])

print("")
print("✅ Numerische Spalten erfolgreich skaliert und im DataFrame 'df_test_similarity_scaled' gespeichert!")

df_test_similarity_scaled.to_csv("Datasets/df_test_similarity_scaled.csv", index=False)
print("")
print("✅ Dataset 3/3 wurde als 'df_test_similarity_sclaed.csv' gespeichert!")

print("")
print("✅ Sparse Cosine Similarity-Matrix wird erstellt, gleich geschaft...")
# Auswahl der relevanten Spalten (ohne 'title')
cols_for_similarity = df_test_similarity_scaled.select_dtypes(include=[np.number]).columns.difference(['title', 'movie link'])

# Sparse-Matrix erstellen
sparse_data = csr_matrix(df_test_similarity_scaled[cols_for_similarity].to_numpy())

# Cosine Similarity berechnen
cosine_similarity_matrix = cosine_similarity(sparse_data, dense_output=False)

# Ausgabe der Matrix (optional)
print("")
print("✅ Sparse Cosine Similarity-Matrix erfolgreich berechnet! Jetzt nur noch speichern, moment...")

# Cosine Similarity-Matrix speichern mit Protocol 4
with open("Datasets/similarity_matrix.pkl", "wb") as f:
    pickle.dump(cosine_similarity_matrix, f, protocol=4)

print("")
print("✅ Cosine Similarity-Matrix wurde erfolgreich gespeichert!")
print("")
print("✅ Alle Schritte erfolgreich abgeschlossen. Bitte main.py starten (streamlit run main.py)")
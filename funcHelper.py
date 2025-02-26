import numpy as np
import pandas as pd

#remove the leading number by title
def handle_title(s: str):
    try:
        return s[s.index('.') + 1:].strip()
    except Exception as e:
        return s
  
# converts the votes to  float
def handle_votes(s: str) -> float:
    '''
    returns the voting vales as float
    '''
    try:
        string = s.strip().upper()
        if string.__contains__('G'):
            return float(string.replace('G', '').strip())*1000000000
        if string.__contains__('M'):
            return float(string.replace('M', '').strip())*1000000
        if string.__contains__('K'):
            return float(string.replace('K', '').strip())*1000
        else:
            return float(string.strip())
    except Exception as e:
        return None
     
# converts the duration to minutes
def handle_duration(duration):
    '''
    return the film duration in minutes
    '''
    if isinstance(duration, str):
        hours = int(duration.split('h')[0]) if 'h' in duration else 0
        minutes = int(duration.split('m')[0].split()[-1]) if 'm' in duration else 0
        return hours * 60 + minutes
    return None
    
# get all existing movies categories with general terms    
def get_movies_categories() -> dict:
    '''
    returns genres from all movies 
    '''
    return {
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

def get_overview_movie_category(genre: list[str]) -> str:
    categories = get_movies_categories()

    for key, value in categories.items():
        for item in genre:
            if item in list(value):
                return key
    
    return None      

# handle oscar nominations in categories
def handle_oscar_nominations(nomination: int, multiclasses: bool = False):
    '''
    handle oscar nominations in categories
        0 => 0 
        1 => 1, 2, 3, 4, 5  
        2 => ab 6
    '''
    if multiclasses == False:
        return 0 if nomination==0 else 1
    else:
        if nomination == 0:
            return 0
        elif nomination <= 8: 
            return 1
        else:
            return 2    

# handle award winners in categories
def handle_award_winners(wins: int, multiclasses: bool = False):
    '''
    handle award wins in categories
    0 => 0 
    1 => range( 1 , 75)  
    2 => range(75 , 150)
    3 => range(150, )
    '''
    if multiclasses == False :
        return 0 if wins==0 else 1
    else:
        if wins == 0:
            return 0
        elif wins < 75: 
            return 1        
        elif wins < 150: 
            return 2
        else:
            return 3    

#handle award nominations in categories
def handle_award_nominations(nomination: int, multiclasses: bool = False):
    '''
    handle award nominations in categories
    0 => 0 
    1 => range( 1 , 75)  
    2 => range(75 , 150)
    3 => range(150, )
    '''
    if multiclasses == False :
        return 0 if nomination==0 else 1
    else:
        if nomination == 0:
            return 0
        elif nomination < 75: 
            return 1        
        elif nomination < 150: 
            return 2
        else:
            return 3        

#handle directors, autors, stars and genres list
def handle_lists(liste: list) -> set:
    '''
    handle lists and return a set of the listed data
    '''
    result = []
    liste.apply(lambda x: eval(x) if isinstance(x, str) else x)
    for item in liste:
        if isinstance(item, list):
            for o in item:
                result.append(o)
        else:
            result.append(item)
            
    return set(result)
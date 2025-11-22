import pandas as pd
import sys
import os
from imdb import Cinemagoer
import re
from unidecode import unidecode as ud
import random

imdb = Cinemagoer()

movie_db = {
    'ID': [],
    'Rank': [],
    'Decade_Rank': [],
    'Title': [],
    'Director': [],
    'Runtime': [],
    'Genre': [],
    'Year': [],
    'Decade': [],
    'Country': [],
    'Language': [],
    'Color': [],
    'Silent': [],
    'Rating': [],
    'Votes': [],
    'Cast': [],
    'Writer': [],
    'Producer': [],
    'Cinematographer': [],
    'Editor': [],
    'Composer': [],
    'Production_Company': [],
    'Plot': []
}

ids = random.sample(range(10000, 100000), 26000)

def get_csv_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'movies.csv')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'movies.csv')
    
csv_path = get_csv_path()

movies = pd.read_csv(csv_path)
movies.sort_values(["Ranking"], axis=0, ascending=[True], inplace=True)

def getID():
    try:
        return ids.pop()
    except:
        return '-'

def getDecadeRank(info):
    try:
        decade = f"{str(info['year'])[:-1]}0s"
        return movie_db['Decade'].count(decade) + 1
    except:
        return '-'
    
def getTitle(info):
    try:
        return ud(info['title'])
    except:
        return '-'

def getDirectors(info):
    try:
        directors = [ud(director['name']) for director in info['director'] if director]
        return ", ".join(directors)
    except:
        return '-'

def getRuntime(info):
    try:
        return int(re.search(r'\d+', info['runtime'][0]).group())
    except:
        return '-'
    
def getGenres(info):
    try:
        return ud(", ".join(info['genres']))
    except:
        return '-'

def getYear(info):
    try:
        return info['year']
    except:
        return '-'

def getDecade(info):
    try:
        return f"{str(info['year'])[:-1]}0s"
    except:
        return '-'

def getCountry(info):
    try:
        return ud(", ".join(info['country']))
    except:
        return '-'

def getLanguage(info):
    try:
        if info['language'][0] == 'None' and len(info['language']) > 1:
            return ud(info['language'][1])
        elif info['language'][0] == 'None' and len(info['language'] == 1):
            return '-'
        else:
            return ud(info['language'][0])
    except:
        return '-'

def getColor(info):
    try:
        for color in [color.lower() for color in info['color']]:
            if "black and white" in color or "colorized" in color:
                return 'False'
        return 'True'
    except:
        return '-'
    
def getSilent(info):
    try:
        for mix in info['sound mix']:
            if 'Silent' in mix:
                return 'True'
        return 'False'
    except:
        return '-'
    
def getRating(info):
    try:
        return info['rating']
    except:
        return '-'
    
def getVotes(info):
    try:
        return info['votes']
    except:
        return '-'

def getCast(info):
    try:
        cast = [ud(actor['name']) for actor in info['cast'] if actor]
        return ", ".join(cast)
    except:
        return '-'
    
def getWriters(info):
    try:
        writers = [ud(writer['name']) for writer in info['writer'] if writer]
        return ", ".join(writers)
    except:
        return '-'
    
def getProducers(info):
    try:
        producers = [ud(producer['name']) for producer in info['producer'] if producer]
        return ", ".join(producers)
    except:
        return '-'

def getCinematographers(info):
    try:
        cinematographers = [ud(cinematographer['name']) for cinematographer in info['cinematographer'] if cinematographer]
        return ", ".join(cinematographers)
    except:
        return '-'
    
def getEditors(info):
    try:
        editors = [ud(editor['name']) for editor in info['editor'] if editor]
        return ", ".join(editors)
    except:
        return '-'
    
def getComposers(info):
    try:
        composers = [ud(composer['name']) for composer in info['composer'] if composer]
        return ", ".join(composers)
    except:
        return '-'

def getProductionCompanies(info):
    try: 
        companies = [ud(company['name']) for company in info['production companies'] if company]
        return ", ".join(companies)
    except:
        return '-'
 
def getPlot(info):
    try:
        return ud(info['plot'][0])
    except:
        return '-'

offset = 0
row = 1
for _, movie in movies.iterrows():
    if imdbID := re.fullmatch(r'https:\/\/www.imdb.com\/title\/tt(.+)\/', str(movie['URL'])):
        info = None
        while not info:
            try:
                info = imdb.get_movie(imdbID.group(1))
            except Exception as e:
                print(f'Exception: {str(e)}, {row} / {len(movies)}')

        movie_db['ID'].append(str(getID()))
        movie_db['Rank'].append(int(movie['Ranking']) - offset)
        movie_db['Decade_Rank'].append(getDecadeRank(info))
        movie_db['Title'].append(getTitle(info))
        movie_db['Director'].append(getDirectors(info))
        movie_db['Runtime'].append(getRuntime(info))
        movie_db['Genre'].append(getGenres(info))
        movie_db['Year'].append(getYear(info))
        movie_db['Decade'].append(getDecade(info))
        movie_db['Country'].append(getCountry(info))
        movie_db['Language'].append(getLanguage(info))
        movie_db['Color'].append(getColor(info))
        movie_db['Silent'].append(getSilent(info))
        movie_db['Rating'].append(getRating(info))
        movie_db['Votes'].append(getVotes(info))
        movie_db['Cast'].append(getCast(info))
        movie_db['Writer'].append(getWriters(info))
        movie_db['Producer'].append(getProducers(info))
        movie_db['Cinematographer'].append(getCinematographers(info))
        movie_db['Editor'].append(getEditors(info))
        movie_db['Composer'].append(getComposers(info))
        movie_db['Production_Company'].append(getProductionCompanies(info))
        movie_db['Plot'].append(getPlot(info))

        movie_df = pd.DataFrame(movie_db)
        movie_df["In_Pool"] = "Y"
        movie_df.to_csv(r'C:\Users\grant\Desktop\Coding\Projects\Movie-Picker\new_movies3.csv', index=False, encoding='utf-8-sig')

        print(f'Processed row {row} / {len(movies)}')
        row += 1
    else:
        offset += 1
        print(f'Processed row {row} / {len(movies)}')
        row += 1
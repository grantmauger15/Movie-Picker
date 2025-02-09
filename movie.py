import pandas as pd
import argparse
from datetime import datetime
import re
import os
import sys
import warnings

warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

def get_csv_path():
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'movies.csv')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'movies.csv')


csv_path = get_csv_path()

parser = argparse.ArgumentParser(description='Movie management tool.')
subparsers = parser.add_subparsers(dest="command", help='Available commands')

get_parser = subparsers.add_parser("get", help='Retrieve a random movie based on filters.')
get_parser.add_argument('-r', '--ranking', type=int, help='Provide ranking requirements for your selection (e.g. 1000-, 50-100, 42).')
get_parser.add_argument('-t100', '--top100', action='store_true', help='Limit selection to movies in the top 100 of its decade.')
get_parser.add_argument('-d', '--director', type=str, help='Provide a director or a list of directors whose movies you want to select from (e.g. "Steven Spielberg", "Hitchcock").')
get_parser.add_argument('-rt', '--runtime', type=str, help='Provide movie runtime requirements for your selection (e.g. 90-120, 90+, 60-).')
get_parser.add_argument('-g', '--genre', type=str, help='Provide a genre or a list of genres to select a movie from (e.g. "Drama" or "Horror, Musical").')
get_parser.add_argument('-y', '--year', type=str, help='Provide a decade, a year range, a year, or a combination of these to select a movie from (e.g. "2010s", "2010-2018", "1994", "2010-2014, 2015").')
get_parser.add_argument('-cou', '--country', type=str, help='Provide a country or a list of countries that you want to limit your selected movies to (e.g. "United States", "France").')
get_parser.add_argument('-l', '--language', type=str, help='Provide a language or a list of languages that you want to limit your selected movies to (e.g. "English", "Spanish").')
get_parser.add_argument('-col', '--color', type=int, help='Limit selection to movies that are either black and white or in color. For black and white put 0, for color put 1.')
get_parser.add_argument('-s', '--silent', type=int, help='Limit selection to movies that are silent or non-silent. For silent put 1, for non-silent put 0.')
get_parser.add_argument('-rat', '--rating', type=str, help='Provide movie rating requirements for your selection (e.g. 7.0-7.4, 9+, 5.4-).')
get_parser.add_argument('-v', '--votes', type=str, help='Provide movie vote count requirements for your selection (e.g. 10000+, 250000-500000, 100-).')
get_parser.add_argument('-a', '--actor', type=str, help='Provide an actor or a list of actors that you want to limit your selected movies to (e.g. "James Stewart", "Zendaya, Tom Cruise").')
get_parser.add_argument('-w', '--writer', type=str, help='Provide a writer or a list of writers that you want to limit your selected movies to (e.g. "Stan Lee", "Dan Aykroyd, Ernest Lehman").')
get_parser.add_argument('-p', '--producer', type=str, help='Provide an actor or a list of actors that you want to limit your selected movies to (e.g. "Kevin Feige", "Ivan Reitman, Robert Wise").')
get_parser.add_argument('-cin', '--cinematographer', type=str, help='Provide a cinematographer or a list of cinematographers that you want to limit your selected movies to (e.g. "Matthew Libatique", "Laszlo Kovacs, Ted McCord").')
get_parser.add_argument('-e', '--editor', type=str, help='Provide an editor or a list of editors that you want to limit your selected movies to (e.g. "William Reynolds", "Dan Lebental, Sheldon Kahn").')
get_parser.add_argument('-com', '--composer', type=str, help='Provide a composer or a list of composers that you want to limit your selected movies to (e.g. "Hans Zimmer", "Danny Elfman, John Williams").')
get_parser.add_argument('-pc', '--production_company', type=str, help='Provide a production company or a list of production companies that you want to limit your selected movies to (e.g. "Marvel Studios", "Paramount Pictures, Metro-Goldwyn-Mayer").')
get_parser.add_argument('-pl', '--plot', type=str, help='Provide a string of text to match against movie plot summaries. For example, putting "ghost" will likely select ghost movies, and putting "affair" will likely select movies involving romantic affairs.')
get_parser.add_argument('-c', '--count', type=str, help='Provide a number of movies that you want to receive. If you want every movie that follows your requirements, put all.')

remove_parser = subparsers.add_parser("remove", help='Remove a movie from the pool given its ID.')
remove_parser.add_argument('movie_id', type=int, help='Remove a movie from the selection pool by providing the ID of the movie.')

list_parser = subparsers.add_parser("list", help='List the movies that have been removed from the selection pool.')

reset_parser = subparsers.add_parser("reset", help='Reset the pool of movies to select from.')

movies = pd.read_csv(csv_path)
args = parser.parse_args()

def starring(cast):
    if len(cast) > 1:
        return re.match(r'^[^,]+,?(?:[^,]+)?,?(?:[^,]+)?,?(?:[^,]+)?,?(?:[^,]+)?', cast).group()
    else:
        return '-'
    
def getRuntime(m):
    if m == '-':
        return '-'
    m = int(m)
    h = m // 60
    m = m % 60

    return f'{h}h {m}m'

if args.command == "get":
    movie_choices = movies

    if args.ranking:
        ranking_args = [arg.strip() for arg in args.ranking.split(',')]
        conditions = []

        for arg in ranking_args:
            if range := re.fullmatch(r'(\d+)-(\d+)', arg):
                start, end = range.group(1), range.group(2)
                conditions.append(f"Ranking >= {start} & Ranking <= {end}")
            elif re.fullmatch(r'\d+[\-+]', arg):
                ranking = int(arg[:-1])
                if arg[-1] == '-':
                    conditions.append(f"Ranking <= {ranking} & Ranking >= 0")
                if arg[-1] == '+':
                    conditions.append(f"Ranking >= {ranking} & Ranking >= 0")
            elif re.fullmatch(r'\d+', arg):
                conditions.append(f"Ranking == {ranking}")
            else:
                print("The ranking flag takes either ranking ranges, like 50-100 or 1000-, or ranking numbers like 42. Please try again.")
                quit()

        conditions = " | ".join(conditions)
        movie_choices['Votes'] = pd.to_numeric(movie_choices['Votes'], errors='coerce').fillna(-1)
        movie_choices['Votes'] = movie_choices['Votes'].astype(int)
        movie_choices = movie_choices.query(conditions)

    if args.top100:
        movie_choices['Decade_Rank'] = movie_choices['Decade_Rank'].astype(int)
        movie_choices = movie_choices.query('Decade_Rank <= 100')

    if args.director:
        director_args = [arg.strip() for arg in args.director.split(',')]
        conditions = []

        for arg in director_args:
            conditions.append(f"Director.str.contains('{arg}', case=False, na=False)")
            
        conditions = " | ".join(conditions)
        movie_choices = movie_choices.query(conditions)

    if args.runtime:
        runtime_args = [arg.strip() for arg in args.runtime.split(',')]
        conditions = []

        for arg in runtime_args:
            if re.fullmatch(r'\d+[\-+]', arg):
                runtime = int(arg[:-1])
                if arg[-1] == '-':
                    conditions.append(f'Runtime <= {runtime} & Runtime > 0')
                elif arg[-1] == '+':
                    conditions.append(f'Runtime >= {runtime} & Runtime > 0')
            elif range := re.fullmatch(r'(\d+)-(\d+)', arg):
                start, end = range.group(1), range.group(2)
                conditions.append(f'Runtime >= {start} & Runtime <= {end}')
            elif re.fullmatch(r'\d+', arg):
                conditions.append(f'Runtime == {arg}')
            else:
                print("The runtime flag takes either runtime ranges, like 90-120, runtimes like 95, or 60+/60- for above and below 60 minutes. Please try again.")
                quit()
        
        conditions = " | ".join(conditions)
        movie_choices['Runtime'] = pd.to_numeric(movie_choices['Runtime'], errors='coerce').fillna(-1)
        movie_choices['Runtime'] = movie_choices['Runtime'].astype(int)
        movie_choices = movie_choices.query(conditions)

    if args.genre:
        genre_args = [arg.strip() for arg in args.genre.split(',')]
        conditions = []

        for arg in genre_args:
            conditions.append(f"Genre.str.contains('{arg}', case=False, na=False)")
            
        conditions = " | ".join(conditions)
        movie_choices = movie_choices.query(conditions)

    if args.year:
        year_args = [arg.strip() for arg in args.year.split(',')]
        conditions = []

        for arg in year_args:
            if re.fullmatch(r'\d{4}s', arg):
                conditions.append(f"Decade == '{arg}'")
            elif range := re.fullmatch(r'(\d{4})-(\d{4})', arg):
                start, end = range.group(1), range.group(2)
                conditions.append(f"Year >= {start} & Year <= {end}")
            elif re.fullmatch(r'\d{4}', arg):
                conditions.append(f"Year == {arg}")
            elif re.fullmatch(r'\d{4}[\-+]', arg):
                if arg[-1] == '-':
                    conditions.append(f"Year <= {arg[:-1]} & Year >= 0")
                if arg[-1] == '+':
                    conditions.append(f"Year >= {arg[:-1]} & Year >= 0")
            else:
                print("The year flag takes either year ranges, like 1982-1995, years like 1946, or decades like 1980s. Please try again.")
                quit()
        
        conditions = " | ".join(conditions)
        movie_choices['Year'] = pd.to_numeric(movie_choices['Year'], errors='coerce').fillna(-1)
        movie_choices['Year'] = movie_choices['Year'].astype(int)
        movie_choices = movie_choices.query(conditions)
    
    if args.country:
        country_args = [arg.strip() for arg in args.country.split(',')]
        conditions = []

        for arg in country_args:
            conditions.append(f"Country.str.contains('{arg}', case=False, na=False)")
            
        conditions = " | ".join(conditions)
        movie_choices = movie_choices.query(conditions)

    if args.language:
        language_args = [arg.strip() for arg in args.language.split(',')]
        conditions = []

        for arg in language_args:
            conditions.append(f"Language.str.contains('{arg}', case=False, na=False)")
            
        conditions = " | ".join(conditions)
        movie_choices = movie_choices.query(conditions)
    
    if args.color is not None:
        if args.color == 0:
            movie_choices = movie_choices.query('Color == "False"')
        elif args.color == 1:
            movie_choices = movie_choices.query('Color == "True"')
        else:
            print("The color flag only takes 1 or 0 as arguments. Please try again.")
            quit()

    if args.silent is not None:
        if args.silent == 0:
            movie_choices = movie_choices.query('Silent == "False"')
        elif args.silent == 1:
            movie_choices = movie_choices.query('Silent == "True"')
        else:
            print("The silent flag only takes 1 or 0 as arguments. Please try again.")
            quit()

    if args.rating:
        rating_args = [arg.strip() for arg in args.rating.split(',')]
        conditions = []

        for arg in rating_args:
            if range := re.fullmatch(r'(\d\.\d)-(\d\.\d)', arg):
                start, end = range.group(1), range.group(2)
                conditions.append(f"Rating >= {start} & Rating <= {end}")
            elif re.fullmatch(r'\d(?:\.\d)?[\-+]', arg):
                rating = float(arg[:-1])
                if arg[-1] == '-':
                    conditions.append(f'Rating <= {rating} & Rating >= 0')
                elif arg[-1] == '+':
                    conditions.append(f'Rating >= {rating} & Rating >= 0')
            elif re.fullmatch(r'\d\.\d', arg):
                conditions.append(f"Rating == {arg}")
            else:
                print("The rating flag takes either rating ranges, like 7.4-8.2, ratings like 7.9, or 7.9+/7.9- for above and below 7.9. Please try again.")
                quit()
        
        conditions = " | ".join(conditions)
        movie_choices['Rating'] = pd.to_numeric(movie_choices['Rating'], errors='coerce').fillna(-1.0)
        movie_choices = movie_choices.query(conditions)

    if args.votes:
        votes_args = [arg.strip() for arg in args.votes.split(',')]
        conditions = []

        for arg in votes_args:
            if range := re.fullmatch(r'(\d+)-(\d+)', arg):
                start, end = range.group(1), range.group(2)
                conditions.append(f"Votes >= {start} & Votes <= {end}")
            elif re.fullmatch(r'\d+[\-+]', arg):
                votes = int(arg[:-1])
                if arg[-1] == '-':
                    conditions.append(f"Votes <= {votes} & Votes >= 0")
                if arg[-1] == '+':
                    conditions.append(f"Votes >= {votes} & Votes >= 0")
            elif re.fullmatch(r'\d+', arg):
                conditions.append(f"Votes == {arg}")
            else:
                print("The votes flag takes either vote ranges, like 5000-15000 or 100000+, or vote numbers like 100. Please try again.")
                quit()

        conditions = " | ".join(conditions)
        movie_choices['Votes'] = pd.to_numeric(movie_choices['Votes'], errors='coerce').fillna(-1)
        movie_choices['Votes'] = movie_choices['Votes'].astype(int)
        movie_choices = movie_choices.query(conditions)

    if args.actor:
        actor_args = [arg.strip() for arg in args.actor.split(',')]
        conditions = []

        for arg in actor_args:
            conditions.append(f"Cast.str.contains('{arg}', case=False, na=False)")
            
        conditions = " | ".join(conditions)
        movie_choices = movie_choices.query(conditions)

    if args.writer:
        writer_args = [arg.strip() for arg in args.writer.split(',')]
        conditions = []

        for arg in writer_args:
            conditions.append(f"Writer.str.contains('{arg}', case=False, na=False)")
            
        conditions = " | ".join(conditions)
        movie_choices = movie_choices.query(conditions)

    if args.producer:
        producer_args = [arg.strip() for arg in args.producer.split(',')]
        conditions = []

        for arg in producer_args:
            conditions.append(f"Producer.str.contains('{arg}', case=False, na=False)")
            
        conditions = " | ".join(conditions)
        movie_choices = movie_choices.query(conditions)

    if args.cinematographer:
        cinematographer_args = [arg.strip() for arg in args.cinematographer.split(',')]
        conditions = []

        for arg in cinematographer_args:
            conditions.append(f"Cinematographer.str.contains('{arg}', case=False, na=False)")
            
        conditions = " | ".join(conditions)
        movie_choices = movie_choices.query(conditions)

    if args.editor:
        editor_args = [arg.strip() for arg in args.editor.split(',')]
        conditions = []

        for arg in editor_args:
            conditions.append(f"Editor.str.contains('{arg}', case=False, na=False)")
            
        conditions = " | ".join(conditions)
        movie_choices = movie_choices.query(conditions)

    if args.composer:
        composer_args = [arg.strip() for arg in args.composer.split(',')]
        conditions = []

        for arg in composer_args:
            conditions.append(f"Composer.str.contains('{arg}', case=False, na=False)")
            
        conditions = " | ".join(conditions)
        movie_choices = movie_choices.query(conditions)

    if args.production_company:
        production_company_args = [arg.strip() for arg in args.production_company.split(',')]
        conditions = []

        for arg in production_company_args:
            conditions.append(f"Production_Company.str.contains('{arg}', case=False, na=False)")
            
        conditions = " | ".join(conditions)
        movie_choices = movie_choices.query(conditions)

    if args.plot:
        plot_args = [arg for arg in args.plot.split(',')]
        conditions = []

        for arg in plot_args:
            conditions.append(f"Plot.str.contains('{arg}', case=False, na=False)")
            
        conditions = " | ".join(conditions)
        movie_choices = movie_choices.query(conditions)

    movie_choices_pool = movie_choices.query('In_Pool == "Y"')
    if movie_choices_pool.empty:
        print("There are no movies that fit your requirements. Please try again.")
    else:
        movies = []
        if args.count:
            if re.fullmatch(r'\d+', args.count):
                if int(args.count) <= 0:
                    print("Either a positive integer or \"all\" must be provided for the count flag. Please try again.")
                    quit()
                elif int(args.count) > 0 and int(args.count) > movie_choices_pool.shape[0]:
                    print("Count number cannot be larger than the number of movies that fulfill requirements. Please try again.")
                    quit()
                else:
                    choices = movie_choices_pool.sample(int(args.count))
            elif args.count == 'all':
                choices = movie_choices_pool
            else:
                print("Either a positive integer or \"all\" must be provided for the count flag. Please try again.")
                quit()
        else:
            choices = movie_choices_pool.sample()

        for _, choice in choices.iterrows():
            movies.append(f"Movie: {choice['Title']} (rating: {choice['Rating']}, votes: {choice['Votes']}, rank: {choice['Rank']}) [{len(movie_choices_pool)} total]\nDirector: {choice['Director']}\nYear: {choice['Year']}\nRuntime: {getRuntime(choice['Runtime'])}\nGenre: {choice['Genre']}\nStarring: {starring(choice['Cast'])}\nLanguage: {choice['Language']}\nPlot: {choice['Plot']}\nID: {choice['ID']}")
        
        print("\033[34m-------------------------\033[0m\n" + "\n\033[31m-------------------------\033[0m\n".join(movies) + "\n\033[34m-------------------------\033[0m")

elif args.command == "remove":
    if args.movie_id in movies["ID"].values:
        if movies.loc[movies["ID"] == args.movie_id, "In_Pool"].iloc[0] == "Y":
            movies.loc[movies["ID"] == args.movie_id, ["In_Pool", "Date"]] = ["N", datetime.now()]
            movies.to_csv(csv_path, index=False)
            print(f"Movie with ID {args.movie_id} has been removed.")
        else:
            print("That movie has already been removed from the pool.")
    else:
        print(f"No movie found with ID {args.movie_id}.")

elif args.command == "reset":
    movies["In_Pool"] = "Y"
    movies.to_csv(csv_path, index=False)
    print("The pool has been reset.")

elif args.command == "list":
    removed_movies = movies.query('In_Pool == "N"')
    if not removed_movies.empty:
        removed_movies = removed_movies.sort_values(by="Date", ascending=True)
    list = []

    if not removed_movies.empty:
        for _, row in removed_movies.iterrows():
            movie = row['Title']
            year = row['Year']
            date = row['Date']
            list.append(f"{movie} ({year}) | {date}")
        print("\n".join(list))
    else:
        print("There are no movies in the list.")
else:
    parser.print_help()
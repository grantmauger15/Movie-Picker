import pandas as pd
import argparse
from datetime import datetime
import re
import os
import sys
import warnings

warnings.simplefilter(action='ignore', category=pd.errors.SettingWithCopyWarning)

def get_csv_path():
    """Get the path to movies.csv, handling both script and frozen exe contexts"""
    if getattr(sys, 'frozen', False):
        return os.path.join(os.path.dirname(sys.executable), 'movies.csv')
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'movies.csv')


csv_path = get_csv_path()

parser = argparse.ArgumentParser(description='Movie management tool.')
subparsers = parser.add_subparsers(dest="command", help='Available commands')

get_parser = subparsers.add_parser("get", help='Retrieve a random movie based on filters.')
get_parser.add_argument('-r', '--rank', type=str, help='Provide rank requirements for your selection (e.g. 1000-, 50-100, 42).')
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
get_parser.add_argument('-m', '--minimal', action='store_true', help='Limit the output to only the title and year of release.')

remove_parser = subparsers.add_parser("remove", help='Remove a movie from the pool given its ID.')
remove_parser.add_argument('movie_id', type=int, help='Remove a movie from the selection pool by providing the ID of the movie.')

list_parser = subparsers.add_parser("list", help='List the movies that have been removed from the selection pool.')

reset_parser = subparsers.add_parser("reset", help='Reset the pool of movies to select from.')

movies = pd.read_csv(csv_path)
args = parser.parse_args()


def build_text_filter_query(command, column):
    """
    Build a pandas query string for text-based filtering with AND/OR logic.
    Supports: comma for AND, semicolon for OR, ! for negation
    Example: "Nolan, Zimmer; Spielberg" = (Nolan AND Zimmer) OR Spielberg
    """
    comm = [command.split(',') for command in command.split(';')]

    for i in range(len(comm)):
        for j in range(len(comm[i])):
            c = comm[i][j].strip()

            if c.startswith('!'):
                comm[i][j] = f"~{column}.str.contains('{c[1:]}', case=False, na=False)"
            else:
                comm[i][j] = f"{column}.str.contains('{c}', case=False, na=False)"

    for i in range(len(comm)):
        comm[i] = " & ".join(comm[i])

    comm = " | ".join(comm)

    return comm


def get_top_cast_members(cast):
    """Extract up to 5 top-billed cast members from the cast string"""
    if len(cast) > 1:
        return re.match(r'^[^,]+,?(?:[^,]+)?,?(?:[^,]+)?,?(?:[^,]+)?,?(?:[^,]+)?', cast).group()
    else:
        return '-'
    

def format_runtime(minutes):
    """Convert minutes to 'Xh Ym' format"""
    if minutes == '-':
        return '-'
    minutes = int(minutes)
    hours = minutes // 60
    mins = minutes % 60
    return f'{hours}h {mins}m'


def get_rating_color(rating):
    """Get color code for rating"""
    try:
        rating = float(rating)
        if rating >= 8.0:
            return '\033[92m'  # Green
        elif rating >= 7.0:
            return '\033[93m'  # Yellow
        else:
            return '\033[37m'  # White
    except:
        return '\033[37m'


def get_rank_color(rank):
    """Get color code for rank"""
    try:
        rank = int(rank)
        if rank <= 100:
            return '\033[92m'  # Green
        elif rank <= 500:
            return '\033[93m'  # Yellow
        else:
            return '\033[37m'  # White
    except:
        return '\033[37m'


def format_votes(votes):
    """Format vote count with thousands separator"""
    try:
        votes = int(votes)
        return f'{votes:,}'
    except:
        return votes


def get_rank_badge(rank):
    """Get badge for top-ranked movies"""
    try:
        rank = int(rank)
        if rank <= 10:
            return ' \033[1;93m★\033[0m'
        elif rank <= 50:
            return ' \033[93m★\033[0m'
        elif rank <= 100:
            return ' \033[90m★\033[0m'
        else:
            return ''
    except:
        return ''


def format_movie_output(choice, minimal=False, pool_size=0, is_last=False):
    """Format a movie's information for display"""
    if minimal:
        return f"{choice['Title']} \033[90m({choice['Year']})\033[0m"
    else:
        rating_color = get_rating_color(choice['Rating'])
        rank_color = get_rank_color(choice['Rank'])
        rank_badge = get_rank_badge(choice['Rank'])
        votes_formatted = format_votes(choice['Votes'])
        
        bottom_separator = f"\n\033[90m{'─' * 60}\033[0m" if is_last else ""
        
        return (f"\n\033[90m{'─' * 60}\033[0m\n"
                f"\033[90mMovie:\033[0m \033[1m{choice['Title']}\033[0m \033[90m({choice['Year']})\033[0m{rank_badge} ({rating_color}{choice['Rating']}\033[0m, {votes_formatted} votes, Rank {rank_color}#{choice['Rank']}\033[0m) [{pool_size} total]\n"
                f"\033[90mDirector:\033[0m {choice['Director']}\n"
                f"\033[90mGenre:\033[0m {choice['Genre']}\n"
                f"\033[90mRuntime:\033[0m {format_runtime(choice['Runtime'])}\n"
                f"\033[90mStarring:\033[0m {get_top_cast_members(choice['Cast'])}\n"
                f"\033[90mPlot:\033[0m {choice['Plot']}\n"
                f"\033[90mID:\033[0m {choice['ID']}"
                f"{bottom_separator}")


def parse_numeric_range(arg_string, column_name, allow_decimal=False):
    """
    Parse numeric range arguments and return a pandas query string.
    Supports: ranges (100-200), at-least (100+), at-most (100-), exact (100)
    Returns: (query_string, error_message) - error_message is None on success
    """
    args = [arg.strip() for arg in arg_string.split(',')]
    conditions = []
    
    if allow_decimal:
        range_pattern = r'(\d+(?:\.\d+)?)-(\d+(?:\.\d+)?)'
        single_pattern = r'\d+(?:\.\d+)?'
        modifier_pattern = r'\d+(?:\.\d+)?[\-+]'
    else:
        range_pattern = r'(\d+)-(\d+)'
        single_pattern = r'\d+'
        modifier_pattern = r'\d+[\-+]'
    
    for arg in args:
        if rng := re.fullmatch(range_pattern, arg):
            start, end = rng.group(1), rng.group(2)
            conditions.append(f"{column_name} >= {start} & {column_name} <= {end}")
        elif re.fullmatch(modifier_pattern, arg):
            value = float(arg[:-1]) if allow_decimal else int(arg[:-1])
            if arg[-1] == '-':
                conditions.append(f"{column_name} <= {value} & {column_name} >= 0")
            elif arg[-1] == '+':
                conditions.append(f"{column_name} >= {value} & {column_name} >= 0")
        elif re.fullmatch(single_pattern, arg):
            conditions.append(f"{column_name} == {arg}")
        else:
            return None, f"Invalid {column_name.lower()} format: '{arg}'"
    
    return " | ".join(conditions), None


def parse_year_range(arg_string):
    """
    Parse year arguments supporting decades, ranges, exact years, and modifiers.
    Returns: (query_string, error_message) - error_message is None on success
    """
    year_args = [arg.strip() for arg in arg_string.split(',')]
    conditions = []

    for arg in year_args:
        if re.fullmatch(r'\d{4}s', arg):  # e.g., "1980s"
            conditions.append(f"Decade == '{arg}'")
        elif rng := re.fullmatch(r'(\d{4})-(\d{4})', arg):  # e.g., "1980-1989"
            start, end = rng.group(1), rng.group(2)
            conditions.append(f"Year >= {start} & Year <= {end}")
        elif re.fullmatch(r'\d{4}[\-+]', arg):  # e.g., "2000+", "1999-"
            year_val = arg[:-1]
            if arg[-1] == '-':
                conditions.append(f"Year <= {year_val}")
            elif arg[-1] == '+':
                conditions.append(f"Year >= {year_val}")
        elif re.fullmatch(r'\d{4}', arg):  # e.g., "1994"
            conditions.append(f"Year == {arg}")
        else:
            return None, f"Invalid year format: '{arg}'"
    
    return " | ".join(conditions), None


# Main command logic
if args.command == "get":
    movie_choices = movies
    
    # Apply rank filter
    if args.rank:
        conditions, error = parse_numeric_range(args.rank, 'Rank')
        if error:
            print(f"{error}\nValid formats: 50-100 (range), 1000- (up to), 42+ (at least), 42 (exact)")
            quit()
        movie_choices['Rank'] = pd.to_numeric(movie_choices['Rank'], errors='coerce').fillna(-1).astype(int)
        movie_choices = movie_choices.query(conditions)

    # Apply top 100 of decade filter
    if args.top100:
        movie_choices['Decade_Rank'] = pd.to_numeric(movie_choices['Decade_Rank'], errors='coerce').fillna(-1).astype(int)
        movie_choices = movie_choices.query('Decade_Rank <= 100 & Decade_Rank > 0')

    # Apply director filter
    if args.director:
        movie_choices = movie_choices.query(build_text_filter_query(args.director, "Director"))

    # Apply runtime filter
    if args.runtime:
        conditions, error = parse_numeric_range(args.runtime, 'Runtime')
        if error:
            print(f"{error}\nValid formats: 90-120 (range), 60- (up to), 90+ (at least), 95 (exact)")
            quit()
        movie_choices['Runtime'] = pd.to_numeric(movie_choices['Runtime'], errors='coerce').fillna(-1).astype(int)
        movie_choices = movie_choices.query(conditions)

    # Apply genre filter
    if args.genre:
        movie_choices = movie_choices.query(build_text_filter_query(args.genre, "Genre"))

    # Apply year filter
    if args.year:
        conditions, error = parse_year_range(args.year)
        if error:
            print(f"{error}\nValid formats: 1980s (decade), 1980-1989 (range), 1994 (exact), 2000+ (after)")
            quit()
        movie_choices['Year'] = pd.to_numeric(movie_choices['Year'], errors='coerce').fillna(-1).astype(int)
        movie_choices = movie_choices.query(conditions)
    
    # Apply country filter
    if args.country:
        movie_choices = movie_choices.query(build_text_filter_query(args.country, "Country"))

    # Apply language filter
    if args.language:
        movie_choices = movie_choices.query(build_text_filter_query(args.language, "Language"))
    
    # Apply color filter
    if args.color is not None:
        if args.color == 0:
            movie_choices = movie_choices.query('Color == "FALSE"')
        elif args.color == 1:
            movie_choices = movie_choices.query('Color == "TRUE"')
        else:
            print("The color flag only takes 1 (color) or 0 (black & white). Please try again.")
            quit()

    # Apply silent filter
    if args.silent is not None:
        if args.silent == 0:
            movie_choices = movie_choices.query('Silent == "FALSE"')
        elif args.silent == 1:
            movie_choices = movie_choices.query('Silent == "TRUE"')
        else:
            print("The silent flag only takes 1 (silent) or 0 (non-silent). Please try again.")
            quit()

    # Apply rating filter
    if args.rating:
        conditions, error = parse_numeric_range(args.rating, 'Rating', allow_decimal=True)
        if error:
            print(f"{error}\nValid formats: 7.0-8.0 (range), 7.5- (up to), 7.9+ (at least), 7.9 (exact)")
            quit()
        movie_choices['Rating'] = pd.to_numeric(movie_choices['Rating'], errors='coerce').fillna(-1.0)
        movie_choices = movie_choices.query(conditions)

    # Apply votes filter
    if args.votes:
        conditions, error = parse_numeric_range(args.votes, 'Votes')
        if error:
            print(f"{error}\nValid formats: 5000-15000 (range), 100- (up to), 100000+ (at least), 100 (exact)")
            quit()
        movie_choices['Votes'] = pd.to_numeric(movie_choices['Votes'], errors='coerce').fillna(-1).astype(int)
        movie_choices = movie_choices.query(conditions)

    # Apply actor filter
    if args.actor:
        movie_choices = movie_choices.query(build_text_filter_query(args.actor, "Cast"))

    # Apply writer filter
    if args.writer:
        movie_choices = movie_choices.query(build_text_filter_query(args.writer, "Writer"))

    # Apply producer filter
    if args.producer:
        movie_choices = movie_choices.query(build_text_filter_query(args.producer, "Producer"))

    # Apply cinematographer filter
    if args.cinematographer:
        movie_choices = movie_choices.query(build_text_filter_query(args.cinematographer, "Cinematographer"))

    # Apply editor filter
    if args.editor:
        movie_choices = movie_choices.query(build_text_filter_query(args.editor, "Editor"))

    # Apply composer filter
    if args.composer:
        movie_choices = movie_choices.query(build_text_filter_query(args.composer, "Composer"))

    # Apply production company filter
    if args.production_company:
        movie_choices = movie_choices.query(build_text_filter_query(args.production_company, "Production_Company"))

    # Apply plot filter
    if args.plot:
        movie_choices = movie_choices.query(build_text_filter_query(args.plot, "Plot"))

    # Filter to only movies in the pool
    movie_choices_pool = movie_choices.query('In_Pool == "Y"')
    
    if movie_choices_pool.empty:
        print("No movies match your criteria.")
    else:
        # Handle count argument
        if args.count:
            if re.fullmatch(r'\d+', args.count):
                count = int(args.count)
                if count <= 0:
                    print("Either a positive integer or \"all\" must be provided for the count flag. Please try again.")
                    quit()
                elif count > movie_choices_pool.shape[0]:
                    print(f"Count ({count}) cannot be larger than available movies ({movie_choices_pool.shape[0]}). Please try again.")
                    quit()
                else:
                    choices = movie_choices_pool.sample(count)
            elif args.count == 'all':
                choices = movie_choices_pool
            else:
                print("Either a positive integer or \"all\" must be provided for the count flag. Please try again.")
                quit()
        else:
            choices = movie_choices_pool.sample()

        # Format and display results
        choices_list = list(choices.iterrows())
        for idx, (_, choice) in enumerate(choices_list):
            is_last = (idx == len(choices_list) - 1)
            print(format_movie_output(choice, minimal=args.minimal, pool_size=len(movie_choices_pool), is_last=is_last))
        
        print()  # Single blank line at end

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
        removed_list = []
        for _, row in removed_movies.iterrows():
            movie = row['Title']
            year = row['Year']
            date = row['Date']
            removed_list.append(f"{movie} ({year} | {date}")
        print("\n".join(removed_list))
    else:
        print("There are no movies in the list.")
        
else:
    parser.print_help()
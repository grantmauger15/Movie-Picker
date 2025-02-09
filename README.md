## Movie Picker CLI Tool
A simple command-line tool (CLI) to randomly pick movies based on a variety of filters from a local movie database.

## Features
- Retrieve a random movie with the option to use critical ranking, director, runtime, genre, year, language, rating, cast, and much more as a filter.
- Mark movies as listened to by removing them from the pool of movies that can be selected.
- List all movies that are removed from the selection pool.
## Installation
### 1) Download the repository using CMD
```powershell
git clone "https://github.com/grantmauger15/Movie-Picker.git"
cd Movie-Picker
```
### 2) Run install.bat
```powershell
install.bat
```

#### You can now access the tool by using the "movie" command in your preferred command line interface.
## Usage
Once installed, the tool can be used from anywhere in your terminal.
### Basic Commands
```bash
movie get -r 1000- -d "hitchcock" -y 1960-1965,1950- -rt 120+
```
- The above command will fetch a movie directed by Alfred Hitchcock between 1960 and 1965, or from 1950 and before. Movie runtime must also be at least 2 hours.
- The movie must also be in the top 1000 most critically acclaimed movies of all time (as sourced from [this list](https://www.theyshootpictures.com/gf1000_startinglist_table.php)).
```bash
Movie: Marnie (rating: 7.1, votes: 55739, rank: 367) [2 total]
Director: Alfred Hitchcock
Year: 1964
Runtime: 2h 10m
Genre: Crime, Drama, Mystery, Romance, Thriller
Starring: Tippi Hedren, Martin Gabel, Sean Connery, Louise Latham, Diane Baker
Language: English
Plot: Mark marries Marnie although she is a habitual thief and has serious psychological problems, and tries to help her confront and resolve them.
ID: 50492
```
- This is one possible output of the command stated above.
```bash
movie get -t100 -g "mystery" -a "orson welles" -l "english" -pl "rosebud"
```
- The above command fetches a mystery movie in English with Orson Welles as part of the cast.
- The movie must also be ranked in the top 100 movies of its decade, and the plot summary must include the word "rosebud" in it.
```bash
movie get
```
- All of the flags are optional, so if you simply want to randomly select any of the 24,547 possible movies, use this command.
```bash
movie get -c 5
```
- The above command does the same as the one before, except it picks 5 movies instead of only 1. If you want all movies that meet your criteria, do -c all.
```bash
movie remove 65880
```
- The above command removes a movie (the one with ID 65880) from the pool of possible movies that can be selected using "movie get".
- This command allows users to mark movies they've already watched and do not want the tool to recommend again.
```bash
movie list
```
- This command will list all movies that were removed using the "movie remove" command. The date and time of removal will also be shown for each movie.
```bash
Marnie (1964) | 2025-02-09 14:25:12.850030
Citizen Kane (1941) | 2025-02-09 14:25:27.393905
Singin' in the Rain (1952) | 2025-02-09 14:25:41.197356
```
- The above is one possible output of the "movie list" command.
```bash
movie reset
```
- This command will cause all movies to once again be selectable via the "movie get" command.
```bash
movie -h
```
- The -h flag can be applied to any command or subcommand to get more help with using the tool or learning more of the possible flags.
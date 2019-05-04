All cleaned data are in data/movies_clean.db
data/movies_clean is a cleaned version of the kaggle dataset and it contains many tables including twitter and youtube data.

Tables in movies_clean:
movie_actor links each movie with respective actors
movie_company (IGNORE)
movie_country (IGNORE)
movie_genre links each movie with respective genres
movie_keyword (IGNORE)
movies has many meta informations about a movie
movies_twitter links movie to twitter information
youtube_clean links movie to youtube information
youtube (IGNORE)
test_train contains the regression models, run the file to see the resuts.txt

YoutubeScraper and TwitterScraper were used to get the youtube/twitter data

db_cleaner contains all functions used to clean the database.

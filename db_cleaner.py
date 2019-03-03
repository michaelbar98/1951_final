import sqlite3
from sqlite3 import Error
class Parser():

    def __init__(self, sqlfile = "data/movies_clean.db"):
        conn = self.create_connection(sqlfile)
        self.conn = conn
        self.c = conn.cursor()

    def create_connection(self, db_file):
        """ create a database connection to a SQLite database """
        try:
            conn = sqlite3.connect(db_file)
            print(sqlite3.version)
            return conn;
        except Error as e:
            print(e)
        finally:
            pass
        return

    def get_clean_table(self):
        all_info = '''select * from temp'''
        for row in self.c.execute(all_info):
            print(row)

    def create_tables(self):
        movie_genre_create ='''
            CREATE TABLE if not exists movie_genre (
	movieID INTEGER not null,
	genreID INTEGER not null, 
	genreName TEXT not null,
    FOREIGN KEY(movieID) REFERENCES movies(id)
	)'''

        self.c.execute(movie_genre_create)
        self.conn.commit()



if __name__ == "__main__":
    parser = Parser()
    parser.create_tables()
    parser.get_clean_table()

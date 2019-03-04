import sqlite3
from sqlite3 import Error
import json
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



    def insert_meta_info(self, movies_meta):
        for movieID in movies_meta.keys():
            meta = movies_meta[movieID]
            for table in meta.keys():
                info = meta[table]
                if len(info) != 0:   
                    print("table: ", table, " : " , info)


    def get_clean_table(self):
        create_new_table = '''CREATE TABLE if not exists "movies" (
            "budget"	INTEGER,
            "id"	INTEGER,
            "original_language"	TEXT,
            "original_title"	TEXT,
            "overview"	TEXT,
            "popularity"	REAL,
            "release_date"	DATE,
            "revenue"	INTEGER,
            "runtime"	INTEGER,
            "status"	TEXT,
            "title"	TEXT,
            "vote_average"	REAL,
            "vote_count"	INTEGER)'''

        self.c.execute(create_new_table)
        self.conn.commit()
        all_info = '''select * from temp'''
        out = []
        movies_meta = {}

        for row in self.c.execute(all_info):
            try:
                curr = []
                curr.append(row[0])
                curr.append(row[3])
                curr += row[5:9]
                curr += row[11:14]
                curr += row[15:17]
                curr += row[18:]
                curr[0] = int(curr[0])
                curr[1] = int(curr[1])
                curr[5] = float(curr[5])
                curr[7] = int(curr[7])
                curr[8] = int(curr[8])
                curr[-2] = float(curr[-2])
                curr[-1] = int(curr[-1])
                out.append(curr)
                key_words = json.loads(row[4])
                genres = json.loads(row[1])
                movies_meta[curr[1]] = {"genres": genres, "key_words": key_words}



            except Exception as e:
                continue




        insert = '''
        INSERT INTO movies(
        budget, id, original_language,original_title,overview,popularity,release_date,revenue,runtime,
        status,title,vote_average,vote_count)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
        

        '''
        self.c.executemany(insert, out)
        self.conn.commit()

        self.insert_meta_info(movies_meta)


        '''
        1-genre
        4 - keywords
        9 - production compnies
        10 - prod countries
        14 - spoken language
        '''

    def getDicFromJson(self, mjson = '''[{"id": 28, "name": "Action"}, {"id": 12, "name": "Adventure"}, {"id": 14, "name": "Fantasy"}, {"id": 878, "name": "Science Fiction"}]'''):
        out = {}
        j = json.loads(mjson)
        print(mjson)
        for item in j:

            print(item.keys())
        #for item in json.split("}"):
            #print(item)
        #print(j)



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
    #parser.create_tables()
    parser.get_clean_table()
    #parser.getDicFromJson()

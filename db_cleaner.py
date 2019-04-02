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
            return conn;
        except Error as e:
            print(e)
        finally:

            pass
        return

    def get_insert_statement(self, table_name):
        if table_name == "genres":
            return '''INSERT INTO movie_genre(movieID, genreID, genreName) VALUES (?,?,?)'''
        elif table_name == "key_words":
            return '''INSERT INTO movie_keyword(movieID, keywordID, keyword) VALUES (?,?,?)'''
        elif table_name == "countries":
            return '''INSERT INTO movie_country(movieID,countryID, country_name) VALUES (?,?,?)'''
        elif table_name == "companies":
            return '''INSERT INTO movie_company(movieID, company_name,companyID) VALUES (?,?,?)'''
        elif table_name == "movie_actor":
            return '''INSERT INTO movie_actor(movieID, actorID,actorName) VALUES (?,?,?)'''




    def insert_meta_info(self, movies_meta):
        to_be_inserted = {}
        for movieID in movies_meta.keys():
            meta = movies_meta[movieID]
            for table in meta.keys():
                if table not in to_be_inserted:
                    to_be_inserted[table] = []
                info = meta[table]
                if len(info) != 0:
                    for item in info:
                        row = [movieID]
                        for thing in item:
                            row.append(item[thing])
                        to_be_inserted[table].append(row)

        for table in to_be_inserted:
            self.c.executemany(self.get_insert_statement(table),to_be_inserted[table])
            self.conn.commit()


    def get_clean_table(self):
        self.drop_table("movies")
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
        old_db = self.create_connection("data/movies.db")
        all_info = '''select * from movies where DATE(release_Date) > DATE("2000-01-01")'''
        out = []
        movies_meta = {}


        for row in old_db.cursor().execute(all_info):
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
                '''   1-genre
                      4 - keywords
                      9 - production compnies
                      10 - prod countries
                      14 - spoken language
                '''
                genres = json.loads(row[1])
                key_words = json.loads(row[4])
                companies = json.loads(row[9])
                countries = json.loads(row[10])
                movies_meta[curr[1]] = {"genres": genres, "key_words": key_words,"companies": companies, "countries": countries}





            except Exception as e:
                print("ERROR AT ", row)
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

    def drop_table(self, table_name):
        drop = "drop table " + table_name
        self.c.execute(drop)
        self.conn.commit()


    def create_tables(self):
        self.drop_table("movie_genre")
        self.drop_table("movie_keyword")
        self.drop_table("movie_company")
        self.drop_table("movie_country")
        self.drop_table("movie_actor")

        movie_actor_create = '''
                    CREATE TABLE if not exists movie_actor (
        	movieID INTEGER not null,
        	actorID INTEGER not null, 
        	actorName TEXT not null,
            FOREIGN KEY(movieID) REFERENCES movies(id)
        	)'''

        movie_genre_create ='''
            CREATE TABLE if not exists movie_genre (
	movieID INTEGER not null,
	genreID INTEGER not null, 
	genreName TEXT not null,
    FOREIGN KEY(movieID) REFERENCES movies(id)
	)'''

        movie_keyword_create = '''
                    CREATE TABLE if not exists movie_keyword (
        	movieID INTEGER not null,
        	keywordID INTEGER not null, 
        	keyword TEXT not null,
            FOREIGN KEY(movieID) REFERENCES movies(id)
        	)'''

        movie_company_create = '''
                            CREATE TABLE if not exists movie_company (
                	movieID INTEGER not null,
                	companyID INTEGER not null, 
                	company_name TEXT not null,
                    FOREIGN KEY(movieID) REFERENCES movies(id)
                	)'''

        movie_country_create = '''
                            CREATE TABLE if not exists movie_country (
                	movieID INTEGER not null,
                	countryID VARCHAR(10) not null,
                	country_name TEXT not null,
                    FOREIGN KEY(movieID) REFERENCES movies(id)
                	)'''

        self.c.execute(movie_genre_create)
        self.c.execute(movie_keyword_create)
        self.c.execute(movie_company_create)
        self.c.execute(movie_country_create)
        self.c.execute(movie_actor_create)

        self.conn.commit()

    def clean_credits(self):
        conn = self.create_connection("data/credits.db")
        curs = conn.cursor()
        to_be_inserted = []
        for credit in curs.execute('''select * from credits'''):
            movie_id = credit[0]
            cast = json.loads(credit[2])
            for item in cast:
                actor_id = item['id']
                actor_name = item['name']
                out = [movie_id, actor_id, actor_name]
                to_be_inserted.append(out)
        self.c.executemany(self.get_insert_statement("movie_actor"),to_be_inserted)
        self.conn.commit()
        curs.close()
        conn.close()

    def close_connection(self):
        self.c.close()
        self.conn.close()


    def get_list_of_movies(self):
        q = '''select original_title from movies'''
        out = self.c.execute(q)
        return out





if __name__ == "__main__":
    parser = Parser()
    #parser.create_tables()
    #parser.get_clean_table()
    #parser.clean_credits()
    #parser.close_connection()
    parser.get_list_of_movies()

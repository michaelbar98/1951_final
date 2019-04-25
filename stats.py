import sqlite3
from sqlite3 import Error
import json
import csv
import numpy as np



class Stats():

    def __init__(self, sqlfile = "data/movies_clean.db"):
        conn = self.create_connection(sqlfile)
        self.conn = conn
        self.c = conn.cursor()
        self.score_movies()


    def close_connection(self):
        self.c.close()
        self.conn.close()

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

    def actor_score(self):
        sql = '''with ids as (select movieID from movie_actor where actorID = ?) select avg(m.revenue_now) from ids, movies as m where m.id = ids.movieID'''
        actors = self.c.execute('''select distinct actorID from movie_actor''')
        ids = list(actors)
        to_be_inserted = []
        iter = 0
        for actor in ids:

            if(iter%1000 == 0):
                print(iter)
            iter += 1
            out = self.c.execute(sql, actor)
            bool = False
            for item in out:
                assert not bool
                bool = True
                to_be_inserted.append([item[0],actor[0]])
        print("halfway")
        iter = 0

        for insert in to_be_inserted:
            if (iter % 1000 == 0):
                print(iter)
            iter+=1
            self.c.execute('''UPDATE movie_actor SET actor_score = ? WHERE actorID = ?''',insert)
        self.conn.commit()


    def score_movies(self):
        movies = self.c.execute('''select distinct id, revenue from movies WHERE revenue>0''')

        movIds = list(movies)

        for k in movIds:

            sql = "select DISTINCT actorID, actor_score FROM movie_actor WHERE movieId=?"
            output = self.c.execute(sql, [k[0]])

            listOutput = list(output)
            print(listOutput)

            newList = []

            for x in listOutput:
                sql1 = "select count(movieID) from movie_actor WHERE actorID = ?"
                out = self.c.execute(sql1, [x[0]])

                countMovies = list(out)[0]

                if countMovies[0] > 1:

                    totalActorScore = float(countMovies[0]) * float(x[1])
                    adjustedActorScore = float((totalActorScore-k[1])/(countMovies[0]-1))
                    newList.append(adjustedActorScore)
                else:
                    newList.append(0.0)

            npArray = np.array(newList)
            avg = np.mean(npArray)

            self.c.execute('''UPDATE movies SET cast_score = ? WHERE id = ?''', [avg, k[0]])
        self.conn.commit()




'''
        credits = self.c.execute('''
#select ma.*, m.revenue_now from movie_actor as ma, movies  as m where m.id = ma.movieID


''')
        id_to_list = {}
        for row in credits:
            actorID = row[1]
            revenue = row[2]
            if actorID in id_to_list:
                id_to_list[actorID].append(revenue)
            else:
                id_to_list[actorID] = [revenue]'''







if __name__ == "__main__":
    stats = Stats()



import sqlite3
class ActorNLP():

    def __init__(self, sqlfile = "data/movies_clean.db"):
        conn = self.create_connection(sqlfile)
        self.conn = conn
        self.c = conn.cursor()

    def read_data(self):



def main():
    a = ActorNLP()

if __name__ == '__main__':
    main()

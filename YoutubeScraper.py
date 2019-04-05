from bs4 import BeautifulSoup as bs
import requests
import db_cleaner
from time import sleep
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import csv


class YoutubeScraper():

    def __init__(self):
        self.numScrape = 3

    def getStatsOnAllMovies(self, movieNames):
        final = len(movieNames)
        print("there are ", final, " movies")
        csv = open('youtube_scrapper.csv', "w")
        columnTitleRow = "name, views1, likes1, dislikes1, views2, likes2, dislikes2, views3, likes3, dislikes3\n"
        csv.write(columnTitleRow)
        movieDict = {}
        start = 0
        for name in movieNames:
            start += 1
            if start %350 ==0:
                print("+10%!")
            out = name
            info = self.getStatsFromTrailer(name)
            for trailer in info:
                out += ',' + trailer['views'].split(' ')[0].replace(',', '')
                out += ',' + trailer['likes'].replace(',', '')
                out += ',' + trailer['dislikes'].replace(',', '')
            out += '\n'
            csv.write(out)
            movieDict[name] = info

        csv.close()
        return movieDict

    def getStatsFromTrailer(self, movieName):
        movieName = movieName.replace(" ", "+")
        base = "https://www.youtube.com/results?search_query="
        qstring = base + movieName + "+trailer"

        r = requests.get(qstring)
        page = r.text
        soup = bs(page, 'html.parser')

        vids = soup.findAll(attrs={'class': 'yt-uix-tile-link'})
        count = 0

        hrefs = []
        statistics = []

        for v in vids:
            if count < self.numScrape:
                if v['href'].startswith("/"):
                    hrefs.append(v['href'])
                    count = count + 1
            else:
                break

        base2 = "http://www.youtube.com"

        for link in hrefs:

            r2 = requests.get(base2 + link)
            page1 = r2.text
            soup1 = bs(page1, 'html.parser')

            viewCount = soup1.find("div", attrs={'class': 'watch-view-count'})
            likesCount = soup1.find("button", attrs={'class': 'like-button-renderer-like-button'})
            dislikesCount = soup1.find("button", attrs={'class': 'like-button-renderer-dislike-button'})

            if viewCount is not None:
                if likesCount != None and dislikesCount != None:
                    result = {"views": viewCount.text, "likes": likesCount.text, "dislikes": dislikesCount.text}
                else:
                    result = {"views": viewCount.text, "likes": "-1", "dislikes": "-1"}
            else:
                if likesCount != None and dislikesCount != None:
                    result = {"views": "-1 views", "likes": likesCount.text, "dislikes": dislikesCount.text}
                else:
                    result = {"views": "-1 views", "likes": "-1", "dislikes": "-1"}

            statistics.append(result)

        return statistics



if __name__ == "__main__":

    db = db_cleaner.Parser()

    movies = db.get_list_of_movies()
    ys = YoutubeScraper()

    result = ys.getStatsOnAllMovies(movies)



    #for key, value in result.items():
        #print(key, value)



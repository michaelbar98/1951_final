from bs4 import BeautifulSoup as bs
import requests
from time import sleep
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
import db_cleaner

class YoutubeScraper():

    def __init__(self):
        self.numScrape = 3

    def getStatsOnAllMovies(self, movieNames):
        movieDict = {}
        for name in movieNames:
            movieDict[name] = self.getStatsFromTrailer(name)
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
            # ratio = -1.0
            # if likesCount.text != "" and dislikesCount.text != "":
            #     ratio = float(likesCount.text.replace(",", "")) / float(dislikesCount.text.replace(",", ""))

            if viewCount is not None:
                # result = {"views": viewCount.text, "likes": likesCount.text, "dislikes": dislikesCount.text,
                #           "LDratio": ratio}

                if likesCount != None and dislikesCount != None:
                    result = {"views": viewCount.text, "likes": likesCount.text, "dislikes": dislikesCount.text}
                else:
                    result = {"views": viewCount.text, "likes": None, "dislikes": None}
            else:
                #result = {"views": None, "likes": likesCount.text, "dislikes": dislikesCount.text, "LDratio": ratio}
                if likesCount != None and dislikesCount != None:
                    result = {"views": None, "likes": likesCount.text, "dislikes": dislikesCount.text}
                else:
                    result = {"views": None, "likes": None, "dislikes": None}

            statistics.append(result)

        return statistics

if __name__ == "__main__":
    db = db_cleaner.Parser()

    movies = db.get_list_of_movies()
    ys = YoutubeScraper()

    result = ys.getStatsOnAllMovies(movies)

    start = 0
    final = len(movies)

    quarter = final/4

    for key, value in result():
        print(key, value)




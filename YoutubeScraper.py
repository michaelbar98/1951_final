from bs4 import BeautifulSoup as bs
import requests
from time import sleep
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from db_cleaner import Parser

class YoutubeScraper():

    def __init__(self, movieNames):
        self.numScrape = 5
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
            ratio = float(likesCount.text.replace(",", "")) / float(dislikesCount.text.replace(",", ""))

            if viewCount is not None:
                result = {"views": viewCount.text, "likes": likesCount.text, "dislikes": dislikesCount.text,
                          "LDratio": ratio}
            else:
                result = {"views": None, "likes": likesCount.text, "dislikes": dislikesCount.text, "LDratio": ratio}
            statistics.append(result)

        return statistics

if __name__ == "__main__":
    db = Parser()
    movies = db.get_list_of_movies()
    ys = YoutubeScraper(movies)
    end = len(movies)
    print ("total of ", end, " movies")
    start = 0;
    for key, value in ys.items():

        print(key, value)
        start += 1


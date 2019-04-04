import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium as se
import sys
import sqlite3

'''
    Reference:
    Scrapping Infinitely scrolling websites Using Pthon Selenium. August 22, 2015
    By Raghavendra
    Link:
    http://raghavendra990.github.io/2015/08/22/scrapping-using-selenium.html
'''

order_dict = {"K": 1000.0, "M": 1e6, "B": 1e9}

def interpret_str(s):
    try:
        return int(s)
    except:
        order = s[-1]
        value = float(s[:-1])
        return int(value * order_dict[order])

def query_by_hashtag(hashtag, nscroll = 3, ntrunc = 1000):
    '''
    hashtag: (type = string) concatenated movie title without punctuations or 
             space for query
    nscroll: (type = int) the number of times browser will automatically 
             scroll down for new feeds
    ntrunc:  (type = int) the maximum number of tweets that will be 
             analyzed in this query
    '''
    browser = webdriver.Firefox()
    url = 'https://twitter.com/search?l=&q=%23' + hashtag + '&src=typd'
    browser.get(url)
    # scroll down for nscroll times and sleep for 3 seconds between scrolls to 
    # allow data loading
    for i in range(nscroll):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    count = browser.find_elements_by_class_name('stream-item-footer')
    if len(count) > ntrunc:
        count = count[:ntrunc]
    summ = []

    table = {"Hashtag": hashtag, "Count": len(count), "Like": 0, "Retweet": 0}
    for item in count:
        text = item.text
        array = text.split()
        res = []
        if array[-1] == "Like":
            res += ["Like", 0]
        else:
            likes = interpret_str(array[-1])
            res += ["Like", likes]
            table["Like"] += likes
        if array[1] == "Retweet" and array[2] == "Like":
            res += ["Retweet", 0]
        elif array[1] == "Retweet" and array[2] != "Like":
            retweets = interpret_str(array[2])
            res += ["Retweet", retweets]
            table["Retweet"] += retweets
        elif array[2] == "Retweet" and array[3] == "Like":
            res += ["Retweet", 0]
        elif array[2] == "Retweet" and array[3] != "Like":
            retweets = interpret_str(array[3])
            res += ["Retweet", retweets]
            table["Retweet"] += retweets
        summ.append(res)
    browser.stop_client()
    browser.close()
    return table

def query_by_title(title, nscroll = 3, ntrunc = 1000):
    '''
    title:   (type = string) the raw movie title for query
    nscroll: (type = int) the number of times browser will automatically 
             scroll down for new feeds
    ntrunc:  (type = int) the maximum number of tweets that will be 
             analyzed in this query
    '''
    hashtag = ''.join(s for s in title if s.isalnum())
    table = query_by_hashtag(hashtag, nscroll, ntrunc)
    return table

def main():
    conn = sqlite3.connect('data/movies_clean.db')
    c = conn.cursor()
    c.execute('SELECT original_title FROM movies;')
    titles = c.fetchall()
    for title in titles:
        # title = 'Signed, Sealed, Delivered'
        nscroll = 10
        ntrunc = 1000
        table = query_by_title(title, nscroll, ntrunc)
    print(table)

if __name__ == "__main__":
    main()

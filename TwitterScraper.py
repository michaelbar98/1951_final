import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import selenium as se
import sys

order_dict = {"K": 1000.0, "M": 1e6, "B": 1e9}

def interpret_str(s):
    try:
        return int(s)
    except:
        order = s[-1]
        value = float(s[:-1])
        return int(value * order_dict[order])

def query_movie(query):
    browser = webdriver.Firefox()
    url = 'https://twitter.com/search?l=&q=%23' + query + '&src=typd'
    browser.get(url)
    # scroll down for 100 times and sleep for 3 seconds between scrolls to 
    # allow data loading
    nscroll = 3

    for i in range(nscroll):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    count = browser.find_elements_by_class_name('stream-item-footer')
    ntrunc = 1000
    if len(count) > ntrunc:
        count = count[:ntrunc]
    summ = []

    table = {"Title": query, "Count": len(count), "Like": 0, "Retweet": 0}
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

def main():
    query = 'kungfupanda'
    table = query_movie(query)
    print(table)

if __name__ == "__main__":
    main()


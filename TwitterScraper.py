import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
'''
    Reference:
    Scrapping Infinitely scrolling websites Using Pthon Selenium. August 22, 2015
    By Raghavendra

    Link:
    http://raghavendra990.github.io/2015/08/22/scrapping-using-selenium.html
'''
def main():
    browser = webdriver.Firefox()
    query = 'kungfupanda'
    url = 'https://twitter.com/search?l=&q=%23' + query + '&src=typd'
    browser.get(url)
    # scroll down for 100 times and sleep for 3 seconds between scrolls to 
    # allow data loading
    nscroll = 2

    for i in range(nscroll):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)

    count = browser.find_elements_by_class_name('stream-item-footer')
    # just analyze the top 1000 tweets

    ntrunc = 1000
    if len(count) > ntrunc:
        count = count[:ntrunc]
    summ = []
    for item in count:
        text = item.text
        array = text.split()
        res = []
        if array[-1] == "Like":
            res += ["Like", 0]
        else:
            res += ["Like", int(array[-1])]
        if array[1] == "Retweet" and array[2] == "Like":
            res += ["Retweet", 0]
        elif array[1] == "Retweet" and array[2] != "Like":
            res += ["Retweet", int(array[2])]
        elif array[2] == "Retweet" and array[3] == "Like":
            res += ["Retweet", 0]
        elif array[2] == "Retweet" and array[3] != "Like":
            res += ["Retweet", int(array[3])]
        summ.append(res)
    for item in summ:
        print(item)

if __name__ == "__main__":
    main()

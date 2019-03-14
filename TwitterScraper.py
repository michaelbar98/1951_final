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
    nscroll = 100

    for i in range(nscroll):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)
    
    tweets = browser.find_elements_by_class_name('tweet-text')
    for tweet in tweets:
        print(tweet.text)
    print(len(tweets))

if __name__ == "__main__":
    main()

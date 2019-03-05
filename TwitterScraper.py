import time
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
'''
    Reference:

    Twitter scraper tutorial with Python: Requests, BeautifulSoup, and Selenium — Part 1 and Part 2
    by Randy Daw-Ran Liou

    Link:
    https://medium.com/@dawran6/twitter-scraper-tutorial-with-python-requests-beautifulsoup-and-selenium-part-1-8e76d62ffd68
    https://medium.com/@dawran6/twitter-scraper-tutorial-with-python-requests-beautifulsoup-and-selenium-part-2-b38d849b07fe
'''
def main():
    browser = webdriver.Firefox()
    query = 'kungfupanda'
    url = 'https://twitter.com/search?l=&q=%23' + query + '&src=typd'
    browser.get(url)
    time.sleep(1)

    body = browser.find_element_by_tag_name('body')

    nscroll = 20
    for _ in range(nscroll):
        body.send_keys(Keys.PAGE_DOWN)
        time.sleep(0.5)
    tweets = browser.find_elements_by_class_name('tweet-text')
    print(len(tweets))

if __name__ == "__main__":
    main()

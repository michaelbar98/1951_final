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

def query_by_title(title, nscroll = 3, ntrunc = 1000):
    '''
    hashtag: (type = string) concatenated movie title without punctuations or 
             space for query
    nscroll: (type = int) the number of times browser will automatically 
             scroll down for new feeds
    ntrunc:  (type = int) the maximum number of tweets that will be 
             analyzed in this query
    '''
    hashtag = ''.join(s for s in title if s.isalnum())
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

    table = {"Title": title, "Count": len(count), "Like": 0, "Retweet": 0}
    for item in count:
        text = item.text
        array = text.split()
        if len(array) == 0:
            continue
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

def save_db(tables):
    # Create a table named movies_twitter in movies_twitter.db to 
    # store the twitter related data
    conn = sqlite3.connect('movies_twitter.db')
    c = conn.cursor()
    # Delete tables if they exist
    c.execute('DROP TABLE IF EXISTS "movies_twitter";')
    # Create tables in the database and add data to it. REMEMBER TO COMMIT
    c.execute('CREATE TABLE movies_twitter(title str not null,\
            count int,\
            like int,\
            retweet int)')
    conn.commit()
    for table in tables:
        title, like = table['Title'], table['Like']
        retweet, count = table['Retweet'], table['Count']
        c.execute('INSERT INTO movies_twitter VALUEs (?, ?, ?, ?)', (title,\
                count,\
                like,\
                retweet))
    conn.commit()

def main():
    conn = sqlite3.connect('data/movies_clean.db')
    c = conn.cursor()
    c.execute('SELECT original_title FROM movies;')
    titles = c.fetchall()
    nscroll = 5
    ntrunc = 2000
    tables = []

    count, dump = 0, 100
    ntitles = len(titles)
    ndump = int(ntitles / dump)
    for count in range(ndump+1):
        print('Saving dump file', count)
        with open('movies_twitter'+str(count)+'.txt', 'w') as out:
            out.write('Title,Count,Like,Retweet\n')
            start = count*dump
            end = min(ntitles, (count+1)*dump)
            for title in titles[start:end]:
                print("Searching ", title[0])
                try:
                    table = query_by_title(title[0], nscroll, ntrunc)
                    tables.append(table)
                    out.write(','.join([str(table[x]) for x in table]))
                    out.write('\n')
                except:
                    continue
    save_db(tables)
    print('Database saved.')

if __name__ == "__main__":
    main()

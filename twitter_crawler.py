import tweepy
import csv
import pandas as pd
''
Reference:
https://gist.github.com/vickyqian/f70e9ab3910c7c290d9d715491cde44c'
'''
def main():
    '''
    consumer_key = ''
    consumer_secret = ''
    access_token = ''
    access_token_secret = ''
    '''
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth,wait_on_rate_limit=True)
    # Open/Create a file to append data
    csvFile = open('movie.csv', 'a')
    #Use csv Writer
    csvWriter = csv.writer(csvFile)

    for tweet in tweepy.Cursor(api.search,q="#kungfupanda",
                           lang="en",
                           since="2017-04-03").items():
        print (tweet.created_at, tweet.text)
        csvWriter.writerow([tweet.created_at, tweet.text.encode('utf-8')])

if __name__ == "__main__":
    main()

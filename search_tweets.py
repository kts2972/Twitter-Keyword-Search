import csv
import re
import matplotlib.pyplot as plt
import tweepy
import json
from textblob import TextBlob

consumer_key = "38MiiO8wOLCFtBLVW5TlxN2Na"
consumer_secret = "Mt30yASeMjc47Nmdsc7mFT5k1SsJZJDl2hlAe8k81OukN0hWfi"
access_token = "712652612525490177-PP0eFx73jd5pZaRjOhO3W22aSlFIUcG"
access_token_secret = "y08aWZxKWqbFumJ6vckQq19BFPe9OXvPhDnJdRnj1mf8h"

TWEETS_MAX = 200


class SearchTweets:

    def __init__(self, apiObj):
        self.api = apiObj

    # end __init__

    def get_tweets(self):
        global TWEETS_MAX

        outfile = input('Output filename? (collected_tweets.json) ').strip()

        if outfile == "":
            outfile = "collected_tweets.json"
            print("Using default filename collected_tweets.json")
        # end if

        query = input("Enter the #hashtag or keyword(s) you want to search for: ").strip()
        try:
            max_tweets = int(
                input("How many tweets would you like to search for (max " + str(TWEETS_MAX) + "): ").strip())
        except ValueError:
            max_tweets = TWEETS_MAX

        # Make sure max_tweets is within bounds
        if max_tweets <= 0:
            max_tweets = TWEETS_MAX
        # end if

        if max_tweets > 200:
            max_tweets = TWEETS_MAX
        # end if

        rtype = input("Result type (mixed, recent, popular) [mixed]: ").strip().lower()
        if len(rtype) == 0:
            rtype = 'mixed'
        # end if

        if rtype not in ['mixed', 'recent', 'popular']:
            print("Defaulting to 'mixed'")
            rtype = 'mixed'

        entities = True
        inc_entities = input("Include entities node (Y/N)? [Y] ").strip().upper()
        if inc_entities not in ['Y', 'N']:
            print("Entities node included")
        else:
            if inc_entities == 'N':
                entities = False
                print("Entities node not included")
            # end if
        # end if

        results = tweepy.Cursor(self.api.search, q=query, result_type=rtype, include_entities=entities).items(
            max_tweets)
        num_tweets = 0
        with open(outfile, 'w', encoding='utf-8') as f:
            # Write one result per line so multiple JSON objects
            # can be read back in from a file and converted or
            # analyzed
            for tweet in results:
                f.write(json.dumps(tweet._json, indent=None) + "\n")
                num_tweets = num_tweets + 1
            # end for
        # end with
        print('Processed {} tweets to {}'.format(num_tweets, outfile))


class MyListener(tweepy.StreamListener):

    def __init__(self, outputfile, tweet_limit=TWEETS_MAX):
        self.outputfile = outputfile
        self.tweet_limit = tweet_limit
        self.num_collected = 0

    # end __init__

    def on_connect(self):
        self.outfile = open(self.outputfile, 'w')

    # end on_connect

    def on_disconnect(self):
        self.outfile.close()

    # end on_disconnect

    def on_status(self, status):
        print("Status: " + status.text)

    # end on_status

    def on_data(self, raw_data):
        # print("on_data: " + raw_data)
        print("Got tweet #" + str(self.num_collected))
        self.outfile.write(raw_data.strip() + "\n")
        self.num_collected = self.num_collected + 1
        if self.num_collected == self.tweet_limit:
            print("Tweet limit " + str(self.tweet_limit) + " hit. Tweets written to " + self.outputfile)
            return False
        else:
            return True

    def on_error(self, status_code):
        if status_code == 420:
            print("Status 420!")
            return False
        return True


# end class

class Listener:
    def __init__(self, authObj):
        self.auth = authObj

    # end __init__

    def run(self):
        global TWEETS_MAX

        outfile = input('Output filename? (collected_tweets.json) ').strip()

        if len(outfile) == 0:
            outfile = "collected_tweets.json"
            print("Using default filename collected_tweets.json")
        # end if

        try:
            num_to_collect = int(input("Number of tweets to collect [" + str(TWEETS_MAX) + "]: "))
        except ValueError:
            num_to_collect = TWEETS_MAX
        # end try

        if num_to_collect <= 0:
            num_to_collect = TWEETS_MAX
        # end if

        if num_to_collect > TWEETS_MAX:
            num_to_collect = TWEETS_MAX
        # end if

        terms = input("Keywords, separated by comma: ").strip()

        if len(terms) == 0:
            print("You must enter at least 1 keyword")
            return
        # end if

        search_terms = [f.strip() for f in terms.split(",")]

        try:
            timeout_secs = int(input("Timeout, in seconds [60]: "))
        except ValueError:
            timeout_secs = 60
            print("Defaulting to 60 seconds")

        api = tweepy.API(self.auth, timeout=timeout_secs, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
        my_listener = MyListener(outfile, num_to_collect)
        stream = tweepy.Stream(api.auth, listener=my_listener, is_async=False)
        stream.filter(track=search_terms)
    # end run


# end class


class SentimentAnaysis:

    def __init__(self, apiObj):
        self.api = apiObj
        self.tweets = []
        self.tweetText = []

    def cleanTweet(self, tweet):
        # Remove Links, Special Characters etc from tweet
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t]) | (\w +:\ / \ / \S +)", " ", tweet).split())

    def percentage(self, part, whole):
        temp = 100 * float(part) / float(whole)
        return format(temp, '.2f')

    def plotPieChart(self, positive, negative, neutral, terms, num_to_collect):
        labels = ['Positive [' + str(positive) + '%]', 'Neutral [' + str(neutral) + '%]',
                  'Negative [' + str(negative) + '%]']
        sizes = [positive, neutral, negative]
        colors = ['yellowgreen', 'gold', 'red']
        patches, texts = plt.pie(sizes, colors=colors, startangle=90)
        plt.legend(patches, labels, loc="best")
        plt.title('How people are reacting on ' + terms +
                  ' by analyzing ' + str(num_to_collect) + ' Tweets.')
        plt.axis('equal')
        plt.tight_layout()
        plt.show()

    def analyzer(self):
        global TWEETS_MAX
        try:
            num_to_collect = int(input("Number of tweets to collect [" + str(TWEETS_MAX) + "]: "))
        except ValueError:
            num_to_collect = TWEETS_MAX
            # end try

        if num_to_collect <= 0:
            num_to_collect = TWEETS_MAX
            # end if

        if num_to_collect > TWEETS_MAX:
            num_to_collect = TWEETS_MAX
            # end if

        terms = input("Keywords, separated by comma: ").strip()

        if len(terms) == 0:
            print("You must enter at least 1 keyword")
            return
        # end if
        # searching for tweets

        self.tweets = tweepy.Cursor(api.search, q=terms, lang="en").items(num_to_collect)

        csvFile = open('analysis.json', 'w', encoding='utf-8')

        csvWriter = csv.writer(csvFile)

        # creating some variables to store info
        polarity = 0
        positive = 0
        negative = 0
        neutral = 0

        # iterating through tweets fetched
        for tweet in self.tweets:
            # Append to temp so that we can store in csv later. I use encode UTF-8
            self.tweetText.append(self.cleanTweet(tweet.text).encode('utf-8'))
            analysis = TextBlob(tweet.text)
            # print(analysis.sentiment)  # print tweet's polarity
            polarity += analysis.sentiment.polarity  # adding up polarities

            if analysis.sentiment.polarity == 0:  # adding reaction
                neutral += 1
            elif analysis.sentiment.polarity > 0.0:
                positive += 1
            else:
                negative += 1

        csvWriter.writerow(self.tweetText)
        csvFile.close()

        # finding average of how people are reacting
        positive = self.percentage(positive, num_to_collect)
        negative = self.percentage(negative, num_to_collect)
        neutral = self.percentage(neutral, num_to_collect)

        # finding average reaction
        polarity = polarity / num_to_collect

        outfile = "analysis.json"

        results = tweepy.Cursor(self.api.search, q=terms).items(num_to_collect)
        num_tweets = 0
        with open(outfile, 'w', encoding='utf-8') as f:
            # Write one result per line so multiple JSON objects
            # can be read back in from a file and converted or
            # analyzed
            for tweet in results:
                f.write(json.dumps(tweet._json, indent=None) + "\n")
                num_tweets = num_tweets + 1
        # printing out data
        print("Your analysis is saved to analysis.json")
        print("How people are reacting on " + terms +
              " by analyzing " + str(num_to_collect) + " tweets.")
        print()
        print("General Report: ")

        if (polarity == 0):
            print("Neutral")
        elif polarity > 0.0:
            print("Positive")
        else:
            print("Negative")

        print()
        print("Detailed Report: ")
        print(str(positive) + "% positive")
        print(str(negative) + "% negative")
        print(str(neutral) + "% neutral")

        self.plotPieChart(positive, negative, neutral, terms, num_to_collect)


if __name__ == '__main__':
    selected = False
    while (selected == False):
        option = input("(S)earch Twitter, (L)isten to a livestream, (A)nalyze Twitter[S/L/A]? ").upper().strip()
        if len(option) > 0 and option in ['L', 'S', 'A']:
            selected = True
        # end if
    # end while

    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    if option == 'S':
        # Search
        search = SearchTweets(api)
        search.get_tweets()
    elif option == 'L':
        # Livestream
        listener = Listener(auth)
        listener.run()
    elif option == 'A':
        sa = SentimentAnaysis(api)
        sa.analyzer()

        # end if
import csv
import json
from html.parser import HTMLParser  # for stripping out the source HTML tags


class TagStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.reset()
        self.data = []

    # end __init__

    def handle_data(self, d):
        self.data.append(d)

    # end handle_data

    def get_data(self):
        return ''.join(self.data)
    # end get_data


# end class

# Converts a file with JSON objects to CSV
# from Twitter. Assumes there is 1 JSON object
# per line!
def convert_json_file(inputfile, outputfile):
    infile = open(inputfile, 'r')
    outfile = open(outputfile, 'w', encoding="utf-8", newline='')
    output = csv.writer(outfile, quoting=csv.QUOTE_NONNUMERIC)

    # Write headers on first row
    headers = ["user_name", "screen_name", "tweet", "tweet_lang", "source", "user_follower_count",
               "user_friends_count", "tweet_retweets", "tweet_favorites"]
    output.writerow(headers)

    with open(inputfile) as infile:
        for obj in infile:
            tweet = json.loads(obj)
            stripper = TagStripper()
            stripper.feed(tweet['source'])
            tweet['source'] = stripper.get_data()
            out_dict = [tweet['user']['name'], tweet['user']['screen_name'],
                        tweet['text'], tweet['lang'], tweet['source'], tweet['user']['followers_count'],
                        tweet['user']['friends_count'], tweet['retweet_count'], tweet['favorite_count']]
            output.writerow(out_dict)

    infile.close()
    outfile.close()


# end convert_json_file

if __name__ == '__main__':
    inputfile = input("JSON input file to convert [collected_tweets.json]: ").strip()
    if len(inputfile) == 0:
        inputfile = 'collected_tweets.json'
    # end if

    outputfile = input("CSV output file [tweets.csv]: ").strip()
    if len(outputfile) == 0:
        outputfile = 'tweets.csv'
    # end if

    convert_json_file(inputfile, outputfile)
import sys
import json


def parse_sent_file(sent_file):
    scores = {}  # initialize an empty dictionary
    for line in sent_file:
        term, score = line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
        scores[term] = int(score)  # Convert the score to an integer.
    return scores


def normalise_tweet(txt):
    return unicode(txt).lower().replace(u'\n', u' ')


def print_tweet_sentiment(tweet_file, sentiment_map):
    for line in tweet_file:
        tweet = json.loads(line)
        if u'created_at' in tweet:
            tweet_words = filter(lambda x: x != u'', normalise_tweet(tweet[u'text']).split(u' '))
            sentiment = 0
            for word in tweet_words:
                if word in sentiment_map:
                    sentiment += sentiment_map[word]

            print sentiment
        else:
            print 0


def main():
    sent_file = open(sys.argv[1])
    tweet_file = open(sys.argv[2])
    sentiment_map = parse_sent_file(sent_file)
    print_tweet_sentiment(tweet_file, sentiment_map)


if __name__ == '__main__':
    main()

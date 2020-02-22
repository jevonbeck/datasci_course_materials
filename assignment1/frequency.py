import sys
import json


def normalise_tweet(txt):
    return unicode(txt).lower().replace(u'\n', u' ')


def print_term_frequency(tweet_file):
    term_map = {}
    for line in tweet_file:
        tweet = json.loads(line)
        if u'created_at' in tweet:
            tweet_words = filter(lambda x: x != u'', normalise_tweet(tweet[u'text']).split(u' '))
            for word in tweet_words:
                if word in term_map:
                    term_map[word] += 1
                else:
                    term_map[word] = 1

    term_count = 0
    for key in term_map:
        term_count += term_map[key]

    for key in term_map:
        print key + u' ' + str(float(term_map[key]) / term_count)


def main():
    tweet_file = open(sys.argv[1])
    print_term_frequency(tweet_file)


if __name__ == '__main__':
    main()

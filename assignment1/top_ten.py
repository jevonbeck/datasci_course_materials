import sys
import json


def compute_hashtag_counts(tweet_file):
    hashtag_map = {}
    for line in tweet_file:
        tweet = json.loads(line)
        if u'created_at' in tweet and len(tweet[u'entities'][u'hashtags']) > 0:
            hashtags = tweet[u'entities'][u'hashtags']
            for tag in hashtags:
                tag_text = tag[u'text']
                if tag_text in hashtag_map:
                    hashtag_map[tag_text] += 1
                else:
                    hashtag_map[tag_text] = 1
    return hashtag_map


def print_top_hashtags(tweet_file):
    hashtag_map = compute_hashtag_counts(tweet_file)
    res = sorted(hashtag_map.items(), cmp=lambda a, b: b[1] - a[1])  # sort map items in descending order

    for elem in res[0:10]:
        print unicode(elem[0]) + u' ' + unicode(elem[1])


def main():
    tweet_file = open(sys.argv[1])
    print_top_hashtags(tweet_file)


if __name__ == '__main__':
    main()

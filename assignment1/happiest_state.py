import sys
import json


states_map = {
    'Alaska':                   'AK',
    'Alabama':                  'AL',
    'Arkansas':                 'AR',
    'American Samoa':           'AS',
    'Arizona':                  'AZ',
    'California':               'CA',
    'Colorado':                 'CO',
    'Connecticut':              'CT',
    'District of Columbia':     'DC',
    'Delaware':                 'DE',
    'Florida':                  'FL',
    'Georgia':                  'GA',
    'Guam':                     'GU',
    'Hawaii':                   'HI',
    'Iowa':                     'IA',
    'Idaho':                    'ID',
    'Illinois':                 'IL',
    'Indiana':                  'IN',
    'Kansas':                   'KS',
    'Kentucky':                 'KY',
    'Louisiana':                'LA',
    'Massachusetts':            'MA',
    'Maryland':                 'MD',
    'Maine':                    'ME',
    'Michigan':                 'MI',
    'Minnesota':                'MN',
    'Missouri':                 'MO',
    'Northern Mariana Islands': 'MP',
    'Mississippi':              'MS',
    'Montana':                  'MT',
    'National':                 'NA',
    'North Carolina':           'NC',
    'North Dakota':             'ND',
    'Nebraska':                 'NE',
    'New Hampshire':            'NH',
    'New Jersey':               'NJ',
    'New Mexico':               'NM',
    'Nevada':                   'NV',
    'New York':                 'NY',
    'Ohio':                     'OH',
    'Oklahoma':                 'OK',
    'Oregon':                   'OR',
    'Pennsylvania':             'PA',
    'Puerto Rico':              'PR',
    'Rhode Island':             'RI',
    'South Carolina':           'SC',
    'South Dakota':             'SD',
    'Tennessee':                'TN',
    'Texas':                    'TX',
    'Utah':                     'UT',
    'Virginia':                 'VA',
    'Virgin Islands':           'VI',
    'Vermont':                  'VT',
    'Washington':               'WA',
    'Wisconsin':                'WI',
    'West Virginia':            'WV',
    'Wyoming':                  'WY'
}
states_array = states_map.values()


def is_valid_state_abbr(abbr):
    return abbr in states_array


def parse_sent_file(sent_file):
    scores = {}  # initialize an empty dictionary
    for line in sent_file:
        term, score = line.split("\t")  # The file is tab-delimited. "\t" means "tab character"
        scores[term] = int(score)  # Convert the score to an integer.
    return scores


def normalise_tweet(txt):
    return unicode(txt).lower().replace(u'\n', u' ')


def compute_tweet_sentiment(tweet_text, sentiment_map):
    tweet_words = filter(lambda x: x != u'', normalise_tweet(tweet_text).split(u' '))

    sentiment = 0
    for word in tweet_words:
        if word in sentiment_map:
            sentiment += sentiment_map[word]
    return sentiment


def compute_tweet_state(tweet, state_name_map):
    tweet_place = tweet[u'place']
    place_type = tweet_place[u'place_type']

    state_code = ''
    if place_type == u'city':
        state_code = tweet_place[u'full_name'].split(u', ')[1]
    elif place_type == u'admin':
        state_code = state_name_map[tweet_place[u'name']]
    else:
        print u'Unknown place_type - ' + tweet[u'place'][u'place_type']
    return state_code


def print_happiest_state(tweet_file, sentiment_map):
    state_sentiment_map = {}

    for line in tweet_file:
        tweet = json.loads(line)
        if u'created_at' in tweet and tweet[u'place'] is not None and tweet[u'place'][u'country_code'] == u'US':
            state_code = compute_tweet_state(tweet, states_map)
            if is_valid_state_abbr(state_code):
                sentiment = compute_tweet_sentiment(tweet[u'text'], sentiment_map)
                if state_code in state_sentiment_map:
                    state_sentiment_map[state_code]['sentiment'] += sentiment
                    state_sentiment_map[state_code]['count'] += 1
                else:
                    state_sentiment_map[state_code] = {'sentiment': sentiment, 'count': 1}
    max_sentiment = 0
    max_state = u''
    for key in state_sentiment_map:
        avg_sentiment = float(state_sentiment_map[key]['sentiment']) / state_sentiment_map[key]['count']
        if avg_sentiment > max_sentiment:
            max_sentiment = avg_sentiment
            max_state = key
    print max_state


def main():
    sent_file = open(sys.argv[1])
    tweet_file = open(sys.argv[2])
    sentiment_map = parse_sent_file(sent_file)
    print_happiest_state(tweet_file, sentiment_map)


if __name__ == '__main__':
    main()

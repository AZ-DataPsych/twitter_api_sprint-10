from os import getenv
import not_tweepy as tweepy
from .models import DB, User, Tweet
import spacy

# gettting enivronmental variables
key = getenv('TWITTER_API_KEY')
secret = ('TWITTER_API_KEY_SECRET')

# make connection to twitter api
TWITTER_AUTH = tweepy.OAuthHandler(key, secret)
TWITTER = tweepy.API(TWITTER_AUTH)
def add_or_update_user(username):
    
    try:
        twitter_user = TWITTER.get_user(screen_name=username)
        # if there's no user in the database create one
        # if there's a user in the database, let's have have that be our db_user
        db_user = (User.query.get(twitter_user.id) or User(id=twitter_user.id, username=username))

        DB.session.add(db_user)

        tweets = twitter_user.timeline(count=200, 
                                    exclude_replies=True, 
                                    includr_rts=False, 
                                    tweet_mode='extended',
                                    since_id=db_user.newest_tweet_id)
        
        if tweets:
            db_user.newest_tweet_id=tweets[0].id
        
        
        for tweet in tweets:
            tweet_vector = vectorize_tweet(tweet.full_text)
            db_tweet= Tweet(id=tweet.id, 
                    text=tweet.full_text[:300], 
                    vect= tweet_vector)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print(f"Erro processing {username}: {e}")
        raise e
    
    else: 
        DB.session.commit()  

nlp = spacy.load('my_model/')        

def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector


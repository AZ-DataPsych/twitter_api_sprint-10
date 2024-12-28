from os import getenv
import not_tweepy as tweepy
from .models import User, Tweet, DB
import spacy
key = getenv('TWITTER_API_KEY')
secret = getenv('TWITTER_API_SECRET_KEY')
key_token = getenv('ACCESS_TOKEN')
key_token_secret = getenv('ACCESS_TOKEN_SECRET')

auth = tweepy.OAuthHandler(key, secret)
twitter=tweepy.API(auth)

def add_or_update_user(username):
    '''take a username and pull that user's data and 
    tweets from the API if user exist in our database 
    then we will just check to see if there are 
    any new tweets that we didn't have and 
    we will add any new new twets to database '''
    try:
        twitter_user = twitter.get_user(screen_name=username)

        db_user = (User.query.get(twitter_user.id)) or User(id=twitter_user.id, username=username)

        DB.session.add(db_user)

        # Get the user's tweets in a list
        tweets = twitter_user.timeline(count=200, 
                                    eclude_replies=True,
                                    include_rts=False,
                                    tweet_mode='extended',
                                    since_id=db_user.newest_tweet_id)
        
        # update the newest_tweet id
        if tweets:
            db_user.newest_tweet_id = tweets[0].id
        
        # add all of the indivdual tweets to the database
        for tweet in tweets:
            tweet_vector= vectorize_tweet(tweet.full_text)
            db_tweet = Tweet(id=tweet.id,
                            text=tweet.full_text[:300],
                            vect=tweet_vector,
                            )#user_id=db_user.id)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print(f"Error processing {username}: {e}")
        raise e
        # save the changes to the DB
    else:    
        DB.session.commit()

nlp=spacy.load('my_model/')
def vectorize_tweet(tweet_text):
    return nlp(tweet_text).vector

from  sklearn.linear_model import LogisticRegression
import numpy as np 

from .models import User
from .twitter import vectorize_tweet

def predict_user(user0_username, user1_username, hypo_tweet_text):
    # grab the users from DB
    user0 = User.query.filter(User.username==user0_username).one()
    user1 = User.query.filter(User.username==user1_username).one()

    # get word embedding from each useer
    user0_vects = np.array([tweet.vect for tweet in user0.tweets])
    user1_vects = np.array([tweet.vect for tweet in user1.tweets])

    # vertically stack the two 2D numpy arrays to make X matrix
    X_train = np.vstack([user0_vects, user1_vects])
    # concatenate labels of 0 or 1 fro each tweet 
    zeros = np.zeros(user0_vects.shape[0])
    ones = np.ones(user1_vects.shape[0])
    y_train = np.concatenate([zeros, ones])

    # instantiate and fit a logistic regression model
    log_reg = LogisticRegression().fit(X_train, y_train)
    # vectorize hypothetical tweet text and reshape to 2D
    hypo_tweet_vect = vectorize_tweet(hypo_tweet_text).reshape(1,-1)
    
    return log_reg.predict(hypo_tweet_vect)[0]





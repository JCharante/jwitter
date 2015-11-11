from flask import Flask, render_template, redirect, url_for, request, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import uuid
import json

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(120))
    session_id = db.Column(db.String(100))
    session_time = db.Column(db.String(100))

    def __init__(self, username, password, session_id, session_time):
        self.username = username
        self.password = password
        self.session_id = session_id
        self.session_time = session_time

    def __repr__(self):
        return '<User %r>' % self.username


class Tweet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tweeter = db.Column(db.String(80))
    content = db.Column(db.String(140))
    likes = db.Column(db.Integer)
    downvotes = db.Column(db.Integer)
    time_created = db.Column(db.String(100))

    def __init__(self, tweeter, content, likes, downvotes, time_created):
        self.tweeter = tweeter
        self.content = content
        self.likes = likes
        self.downvotes = downvotes
        self.time_created = time_created

    def __repr__(self):
        return '<Tweet %i>' % self.id


class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tweeter = db.Column(db.String(80))
    tweet_id = db.Column(db.Integer)

    def __init__(self, tweeter, tweet_id):
        self.tweeter = tweeter
        self.tweet_id = tweet_id

    def __repr__(self):
        return '<Like %i>' % self.id


class Downvote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tweeter = db.Column(db.String(80))
    tweet_id = db.Column(db.Integer)

    def __init__(self, tweeter, tweet_id):
        self.tweeter = tweeter
        self.tweet_id = tweet_id

    def __repr__(self):
        return '<Downvote %i>' % self.id


class Follow(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    follower = db.Column(db.String(80))
    followed = db.Column(db.String(80))

    def __init__(self, follower, followed):
        self.follower = follower
        self.followed = followed

    def __repr__(self):
        return '<%s follows %s>' % (self.follower, self.followed)


# Returns true if session is valid, returns false if not
# It checks if the session_id is in the database, and then checks the last time it was activated
# If activated more than 20 minutes ago, it'll return False.
def valid_session(session_id):
    if session_id == "invalid":
        return False
    else:
        try:
            if db_user_info("session_id", session_id).session_id == session_id:
                original_time = datetime.strptime(db_user_info("session_id", session_id).session_time,
                                                  "%Y-%m-%d %H:%M:%S.%f")
                right_now = datetime.strptime(str(datetime.utcnow()), "%Y-%m-%d %H:%M:%S.%f")

                if original_time < right_now + timedelta(minutes=-20):
                    # print("Session too old. Last login was {} and it is now {}".format(original_time, right_now))
                    return False
                else:
                    # print("Session not too old. Last login was {} and it is now {}".format(original_time, right_now))
                    return True
            else:
                print("Error getting session id")
                return False
        except:
            try:
                print(session_id)
                print(db_user_info("session_id", session_id).session_id)
            except:
                print("No such user exists")
            return False


def make_user(username, password):
    if User.query.filter_by(username=username, password=password).first() is None:
        try:
            db.session.add(User(username, password, str(uuid.uuid4()), str(datetime.utcnow())))
            db.session.commit()
            return "User Successfully Created"
        except:
            return "Error creating User"
    else:
        return "Username taken"


def like_tweet(tweeter, tweet_id):
    db.session.add(Like(tweeter, tweet_id))
    db.session.commit()
    return "Successfully added tweet like to the database"


def new_follower(follower, followed):
    db.session.add(Follow(follower, followed))
    db.session.commit()
    return "Successfully followed person!"


def un_follow(follower, followed):
    Follow.query.filter_by(follower=follower, followed=followed).delete()
    db.session.commit()
    return "Successfully unfollowed"


def check_if_followed(follower, followed):
    try:
        if Follow.query.filter_by(follower=follower, followed=followed).first() is None:
            return False
        else:
            return True
    except:
        return False


def downvote_tweet(tweeter, tweet_id):
    db.session.add(Downvote(tweeter, tweet_id))
    db.session.commit()
    return "Successfully added tweet downvote to the database"


# Adds tweets to the database.
# Gets the username from the session_id
def make_tweet(tweeter, content):
    # Hash-tags have a link added to them here, less and equal signs are replaced with nonfunctional <> signs
    # To protect from having dangerous javascript scripts in a tweet work and to stop images.
    content = tweet_content_sanitizer(content)
    db.session.add(Tweet(tweeter, content, 0, 0, str(datetime.utcnow())))
    db.session.commit()
    return "Successfully made a tweet"


# Returns the session_id from the database to be put into a dict in the user's cookies if the
# username/password combination is right. If they're wrong it returns invalid.
def make_session(form_data):
    try:
        if db_user_info("username", form_data.get('username', '')).password == form_data.get('password'):
            user = User.query.filter_by(username=form_data.get('username', '')).first()
            # print("{}'s password is {} and has a session id of {}. Their session time is {}".format(user.username, user.password, user.session_id, user.session_time))
            user.session_time = str(datetime.utcnow())
            db.session.commit()
            # print("{}'s password is {} and has a session id of {}. Their session time is {}".format(user.username, user.password, user.session_id, user.session_time))
            return db_user_info("username", form_data.get('username')).session_id
        else:
            return "invalid"
    except:
        print("Wrong Username or Password")
        return "invalid"


# Input: Username Output: Dictionary containing information on the row containing that user's information
# Used for getting data, not for updating data
def db_user_info(type, data):
    if type == "username":
        # return json.loads(str(User.query.filter_by(username=data).first()))
        return User.query.filter_by(username=data).first()
    elif type == "session_id":
        # return json.loads(str(User.query.filter_by(session_id=data).first()))
        return User.query.filter_by(session_id=data).first()


# Returns a dict with the data from the specified cookie
def get_saved_data(key):
    data = json.loads(request.cookies.get(key, '{}'))
    return data


# Returns True if specified cookie is in the User's Browser
def cookie_exists(cookie_name):
    if cookie_name in request.cookies:
        return True
    else:
        return False


# Returns with a dictionary containing dictionaries with information about the tweets in the following format
""" {
    tweet_1: {
        'id': 123,
        'content': 'lorem ipsum',
        'likes': 0,
        'downvotes': 0,
        'time_created': time the tweet was created in the datetime.datetime.utcnow() format
    },
    tweet_2: {
        'id': 123,
        'content': 'lorem ipsum',
        'likes': 0,
        'downvotes': 0,
        'time_created': time the tweet was created in the datetime.datetime.utcnow() format
    },
"""


def get_tweets(type, data):
    number_of_tweets = 0
    response = {}
    if type == "all":
        for tweet in Tweet.query.order_by(Tweet.id.desc()).all():
            response[number_of_tweets] = {'id': tweet.id,
                                          'tweeter': tweet.tweeter,
                                          'content': tweet.content,
                                          'likes': tweet.likes,
                                          'downvotes': tweet.downvotes,
                                          'time_created': tweet.time_created
                                          }
            number_of_tweets += 1
        response = response
        return response
    elif type == "username":
        for tweet in Tweet.query.order_by(Tweet.id.desc()).filter(Tweet.tweeter == data).all():
            response[number_of_tweets] = {'id': tweet.id,
                                          'tweeter': tweet.tweeter,
                                          'content': tweet.content,
                                          'likes': tweet.likes,
                                          'downvotes': tweet.downvotes,
                                          'time_created': tweet.time_created
                                          }
            number_of_tweets += 1
        return response
    elif type == "follower_feed":
        followed_people = []
        for row in Follow.query.filter_by(follower=data).all():
            followed_people.append(row.followed)
        for tweet in Tweet.query.order_by(Tweet.id.desc()).filter((Tweet.tweeter.in_(followed_people))).all():
            response[number_of_tweets] = {'id': tweet.id,
                                          'tweeter': tweet.tweeter,
                                          'content': tweet.content,
                                          'likes': tweet.likes,
                                          'downvotes': tweet.downvotes,
                                          'time_created': tweet.time_created
                                          }
            number_of_tweets += 1
        return response


def retweet_tweet(tweet_id, tweeter):
    original_tweet = Tweet.query.filter_by(id=tweet_id).first()
    make_tweet(tweeter, original_tweet.content)
    return "Retweeted!"


def tweet_content_sanitizer(value):
    value = value.replace('<', '&lt;')
    value = value.replace('>', '&gt;')
    list_of_words = value.split(" ")
    image_extensions = ['.jpg', '.png', '.gif', '.svg']
    for wrdx in range(0, len(list_of_words)):
        try:
            word_length = len(list_of_words[wrdx])
            # If it's a hashtag
            if list_of_words[wrdx][0] == '#' and word_length > 1:
                list_of_words[wrdx] = '<a href="http://placekitten.com">' + list_of_words[wrdx] + '</a>'
            # If it's a youtube link
            elif list_of_words[wrdx][0:17] == "https://youtu.be/" and word_length > 18:
                list_of_words[wrdx] = '<a href="' + list_of_words[wrdx] + '">' + \
                                            list_of_words[wrdx] + '</a>' + \
                                            '<button class="youtube-link">Watch Video</button>'
            # If it's a picture
            elif list_of_words[wrdx][word_length - 4] == ".":
                for image_extension in image_extensions:
                    extension_length = len(image_extension)
                    if list_of_words[wrdx][word_length - extension_length:] == image_extension and word_length > 8:
                        list_of_words[wrdx] = '<a href="' + list_of_words[wrdx] + '">' + \
                                                    list_of_words[wrdx] + '</a>' + \
                                                    '<button class="picture-link">View Image</button>'
            # If it's a non-youtube/normal link
            elif (list_of_words[wrdx][0:7] == "http://" or list_of_words[wrdx][0:8] == "https://") and word_length > 8:
                list_of_words[wrdx] = '<a href="' + list_of_words[wrdx] + '">' + \
                                            list_of_words[wrdx] + '</a>'

        except:
            pass
    response = ""
    for word in list_of_words:
        response += word + ' '
    return response

@app.route('/')
def index():
    data = get_saved_data("data")
    return render_template('index.html', saves=data, cookie_exists=lambda x: cookie_exists(x),
                           valid_session=lambda x: valid_session(x))


@app.route('/login', methods=['POST'])
def login():
    response = make_response(redirect(url_for('index')))
    response.set_cookie("data", json.dumps({"session_id": make_session(dict(request.form.items()))}))
    return response


@app.route('/register')
def register():
    return render_template('register.html')


# /register has a button that submits the form information to here.
@app.route('/newaccount', methods=['POST'])
def newaccount():
    response = make_response(redirect(url_for('index')))
    username = dict(request.form.items()).get('username', '')
    password = dict(request.form.items()).get('password', '')
    make_user(username, password)
    response.set_cookie("data", json.dumps({"session_id": make_session(dict(request.form.items()))}))
    return response


@app.route('/home')
def home():
    data = get_saved_data("data")
    return render_template('home.html',
                           saves=data,
                           cookie_exists=lambda x: cookie_exists(x),
                           valid_session=lambda x: valid_session(x),
                           db_user_info=lambda x, y: db_user_info(x, y),
                           get_tweets=lambda x, y: get_tweets(x, y),
                           check_if_followed=lambda x, y: check_if_followed(x, y)
                           )


# On the home page, submitted a new tweet will send a post request to this function.
# This function uses the make_tweet function to add a new tweet
@app.route('/newtweet', methods=['POST'])
def newtweet():
    response = make_response(redirect(url_for('home')))
    data = get_saved_data("data")
    tweeter = db_user_info("session_id", data.get('session_id')).username
    make_tweet(tweeter, dict(request.form.items()).get('content', ''))
    return response


# When clicking on the number of downvotes on the home page, it will launch an ajax get command with the tweet's id.
# This function gets the tweet with the id and increments the likes on it by -1
# and then returns with the number of downvotes
@app.route('/downvote/<int:id>')
def downvote(id):
    data = get_saved_data("data")
    if valid_session(data.get('session_id')) is True:
        tweeter = db_user_info("session_id", data.get('session_id')).username
        # if the tweet is not already downvoted
        if Downvote.query.filter_by(tweeter=tweeter, tweet_id=id).first() is None:
            print("{} downvoted tweet #{}".format(tweeter, id))
            downvote_tweet(tweeter, id)
            Tweet.query.filter_by(id=id).first().downvotes += 1
            db.session.commit()
            # If the tweet is not liked
            if Like.query.filter_by(tweeter=tweeter, tweet_id=id).first() is None:
                print("{} not liked by {}".format(id, tweeter))
            # If the tweet is liked
            else:
                Like.query.filter_by(tweeter=tweeter, tweet_id=id).delete()
                Tweet.query.filter_by(id=id).first().likes -= 1
                db.session.commit()
        # If the tweet is already downvoted
        else:
            print("Error, tweet already downvoted")

        return "{} Downvotes".format(Tweet.query.filter_by(id=id).first().downvotes)
    else:
        return make_response(redirect(url_for('index')))


# When clicking on the number of likes on the home page, it will launch an ajax get command with the tweet's id.
# This function gets the tweet with the id and increments the likes on it by 1 and then returns with the number of likes
@app.route('/like/<int:id>')
def like(id):
    data = get_saved_data("data")
    if valid_session(data.get('session_id')) is True:
        tweeter = db_user_info("session_id", data.get('session_id')).username
        # If the tweet is not liked
        if Like.query.filter_by(tweeter=tweeter, tweet_id=id).first() is None:
            print("{} liked tweet #{}".format(tweeter, id))
            like_tweet(tweeter, id)
            Tweet.query.filter_by(id=id).first().likes += 1
            db.session.commit()
            # If the tweet is not downvoted
            if Downvote.query.filter_by(tweeter=tweeter, tweet_id=id).first() is None:
                print("{} not downvoted by {}".format(id, tweeter))
            # If the tweet is downvoted
            else:
                Downvote.query.filter_by(tweeter=tweeter, tweet_id=id).delete()
                Tweet.query.filter_by(id=id).first().downvotes -= 1
                db.session.commit()
        # If the tweet is already liked
        else:
            print("Error, tweet already liked")

        return "{} Likes".format(Tweet.query.filter_by(id=id).first().likes)
    else:
        return make_response(redirect(url_for('index')))


@app.route('/follow/<int:followed_tweet_id>')
def follow(followed_tweet_id):
    data = get_saved_data("data")
    if valid_session(data.get('session_id')) is True:
        follower = db_user_info("session_id", data.get('session_id')).username
        followed = Tweet.query.filter_by(id=followed_tweet_id).first().tweeter
        if check_if_followed(follower, followed) is True:
            un_follow(follower, followed)
            return "Follow"
        else:
            new_follower(follower, followed)
            return "Unfollow"
    else:
        return make_response(redirect(url_for('index')))


@app.route('/delete/<int:id>')
def delete(id):
    data = get_saved_data("data")
    if valid_session(data.get('session_id')) is True:
        tweeter = db_user_info("session_id", data.get('session_id'))
        try:
            if tweeter.username == Tweet.query.filter_by(id=id).first().tweeter:
                Tweet.query.filter_by(id=id).delete()
                Like.query.filter_by(tweet_id=id).delete()
                Downvote.query.filter_by(tweet_id=id).delete()
                db.session.commit()
                return "Tweet Deleted"
            else:
                return "You do not have auth. to delete this tweet!"
        except:
            return "Tweet not found"
    else:
        return "Invalid session!"


@app.route('/retweet/<int:id>')
def retweet(id):
    data = get_saved_data("data")
    if valid_session(data.get('session_id')) is True:
        if db_user_info("session_id", data.get('session_id')).username != Tweet.query.filter_by(id=id).first().tweeter:
            tweeter = db_user_info("session_id", data.get('session_id'))
            retweet_tweet(id, tweeter.username)
            return "Retweeted!"
        else:
            return "You can't retweet your own tweet!"
    else:
        return "Invalid Session!"


@app.route('/profile/<username>')
def user_profile(username):
    data = get_saved_data("data")
    if valid_session(data.get('session_id')) is True:
        return render_template('profile.html',
                               saves=data,
                               cookie_exists=lambda x: cookie_exists(x),
                               valid_session=lambda x: valid_session(x),
                               db_user_info=lambda x, y: db_user_info(x, y),
                               get_tweets=lambda x, y: get_tweets(x, y),
                               check_if_followed=lambda x, y: check_if_followed(x, y),
                               username=username
                               )
    else:
        return make_response(redirect(url_for('index')))

# Wipes the DB
@app.route('/hiroshima')
def hiroshima():
    Tweet.query.delete()
    Like.query.delete()
    User.query.delete()
    Downvote.query.delete()
    Follow.query.delete()
    db.session.commit()
    return "database got rekt"


app.run(debug=True, host='0.0.0.0', port=8000)

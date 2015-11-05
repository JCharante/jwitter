from flask import Flask, render_template, redirect, url_for, request, make_response
from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime, timedelta
import re
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
    #diction = db.Column(db.String(1000))

    def __init__(self, tweeter, content, likes, downvotes, time_created):
        self.tweeter = tweeter
        self.content = content
        self.likes = likes
        self.downvotes = downvotes
        self.time_created = time_created
        """self.diction = json.dumps({'id': self.id,
                    'tweeter': self.tweeter,
                    'content': self.content,
                    'likes': self.likes,
                    'downvotes': self.downvotes,
                    'time_created': self.time_created
                    })"""

    def __repr__(self):
        return '<Tweet %i>' % self.id


def valid_session(session_id):
    if session_id == "invalid":
        return False
    else:
        try:
            if db_user_info("session_id", session_id).session_id == session_id:
                original_time = datetime.strptime(db_user_info("session_id", session_id).session_time, "%Y-%m-%d %H:%M:%S.%f")
                right_now = datetime.strptime(str(datetime.utcnow()), "%Y-%m-%d %H:%M:%S.%f")

                if original_time < right_now + timedelta(minutes=-20):
                    #print("Session too old. Last login was {} and it is now {}".format(original_time, right_now))
                    return False
                else:
                    #print("Session not too old. Last login was {} and it is now {}".format(original_time, right_now))
                    return True
            else:
                print("Error getting session id")
                return False
        except:
            print("No such user exists")
            print(session_id)
            print(db_user_info("session_id", session_id).session_id)
            return False


def make_user(username, password):
    if User.query.filter_by(username=username,password=password).first() is None:
        try:
            db.session.add(User(username, password, str(uuid.uuid4()), str(datetime.utcnow())))
            db.session.commit()
            return "User Successfully Created"
        except:
            return "Error creating User"
    else:
        return "Username taken"

def make_tweet(session_id, content):
    db.session.add(Tweet(db_user_info("session_id", session_id).username, content, 0, 0, str(datetime.utcnow())))
    db.session.commit()
    return "Successfully made a tweet"


def make_session(form_data):
    try:
        if db_user_info("username", form_data.get('username', '')).password == form_data.get('password'):
            user = User.query.filter_by(username=form_data.get('username', '')).first()
            #print("{}'s password is {} and has a session id of {}. Their session time is {}".format(user.username, user.password, user.session_id, user.session_time))
            user.session_time = str(datetime.utcnow())
            db.session.commit()
            #print("{}'s password is {} and has a session id of {}. Their session time is {}".format(user.username, user.password, user.session_id, user.session_time))
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
        #return json.loads(str(User.query.filter_by(username=data).first()))
        return User.query.filter_by(username=data).first()
    elif type == "session_id":
        #return json.loads(str(User.query.filter_by(session_id=data).first()))
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
        for tweet in Tweet.query.filter(Tweet.tweeter == data).all():
            response[number_of_tweets] = {'id': tweet.id,
                                            'tweeter': tweet.tweeter,
                                            'content': tweet.content,
                                            'likes': tweet.likes,
                                            'downvotes': tweet.downvotes,
                                            'time_created': tweet.time_created
                                            }
            number_of_tweets += 1
        return response

#print(get_tweets("username", Tweet.query.filter(Tweet.tweeter == 'cows').first().tweeter))

"""
for tweet in get_tweets("username", "cows").items():
    #print("%i %s %s %i %i %s" % (tweet))
    print(tweet[1].get('content'))
"""
"""
for tweet in get_tweets("all", "nothing").items():
    print(tweet[1].get('content'))
"""

@app.route('/')
def index():
    data = get_saved_data("data")
    return render_template('index.html', saves=data, cookie_exists=lambda x: cookie_exists(x), valid_session=lambda x: valid_session(x))


@app.route('/login', methods=['POST'])
def login():
    response = make_response(redirect(url_for('index')))
    response.set_cookie("data", json.dumps({"session_id": make_session(dict(request.form.items()))}))
    return response

@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/newaccount', methods=['POST'])
def newaccount():
    response = make_response(redirect(url_for('index')))
    username = dict(request.form.items()).get('username', '')
    password = dict(request.form.items()).get('password', '')
    make_user(username, password)
    return response

@app.route('/home')
def home():
    data = get_saved_data("data")
    return render_template('home.html',
            saves=data,
            cookie_exists=lambda x: cookie_exists(x),
            valid_session=lambda x: valid_session(x),
            db_user_info=lambda x,y: db_user_info(x, y),
            get_tweets=lambda x,y: get_tweets(x, y)
    )


@app.route('/newtweet', methods=['POST'])
def newtweet():
    response = make_response(redirect(url_for('home')))
    data = get_saved_data("data")
    make_tweet(data.get('session_id'), dict(request.form.items()).get('content', ''))
    return response

app.run(debug=True, host='0.0.0.0', port=8000)
# jwitter
A twitter clone written in Python w/ Flask


# Getting started
1. Create a database (I'm using sqlite3) in the root folder of the project (same directory as test.py)
2. Setup the database like this: http://puu.sh/lcIaL/92c9a871e3.png

> You wouldn't have to manually create the db if I had used sqlalchemy rather than flask-sqlalchemy

# Current Features
* Creating and logging into account
* Creating new tweets
* Users can upvote/downvote tweets (Once per tweet per user)
* Retweeting Tweets
* Follow/Unfollow System
* Follower Feed (Only see Tweets from the people you follow)
* User Profiles (Still need to add bios.


# Known Issues
* Currently all usernames/passwords stored in the User table in the database are stored in plaintext (I know how to fix this now)

> Should have used bcrypt's hashing as seen [here](https://github.com/AI-Productions/AndOre/blob/unstable/erebus/erebus_util.py) 

* Currently redirecting users with the meta tag, which is not recommended by the W3C.

> Should have used window.replace

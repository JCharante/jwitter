# jwitter
A twitter clone written in Python w/ Flask


# Getting started
1. Create a database (I'm using sqlite3) in the root folder of the project (same directory as test.py)
2. Setup the database like this: http://puu.sh/lcIaL/92c9a871e3.png

# Current Features
* Creating and logging into account
* Creating new tweets
* Users can upvote/downvote tweets (Once per tweet per user)


# Known Issues
* Currently all usernames/passwords stored in the User table in the database are stored in plaintext
* Currently redirecting users with the meta tag, which is not recommended.  

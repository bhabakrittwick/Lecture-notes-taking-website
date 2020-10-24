#!/bin/bash
cd ~
git clone https://github.com/rittwickBhabak/Lecture-notes-taking-website.git
mv Lecture-notes-taking-website/* mysite
cd mysite
cp app.py flask_app.py
cd ~
mkvirtualenv myvirtualenv --python=/usr/bin/python3.6
pip install Flask
pip install Flask-SQLAlchemy
pip3.6 install Flask-Migrate
export FLASK_APP=flask_app
cd mysite
flask db init
flask db migrate -m "initial migration"
flask db upgrade

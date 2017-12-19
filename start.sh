#!/usr/bin/env bash

apt update
pip install flask nginx gunicorn

git clone git@github.com:gundamkeroro/nsfw_flaskAPI.git
cd nsfw_flaskAPI
cp open_nsfw /etc/nginx/sites-available/open_nsfw
sudo ln -s /etc/nginx/sites-available/open_nsfw /etc/nginx/sites-enabled
sudo nginx -t
sudo service nginx restart

gunicorn -w 8 -b 127.0.0.1:4000 NSFW:app



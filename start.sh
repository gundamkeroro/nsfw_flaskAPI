#!/usr/bin/env bash

apt update
apt-get install -y nginx
pip install -y flask gunicorn

git clone https://github.com/gundamkeroro/nsfw_flaskAPI.git
cd nsfw_flaskAPI
cp open_nsfw /etc/nginx/sites-available/open_nsfw
ln -s /etc/nginx/sites-available/open_nsfw /etc/nginx/sites-enabled
nginx -t
service nginx restart

gunicorn -w 8 -b 127.0.0.1:4000 NSFW:app



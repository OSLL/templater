#!/bin/bash

RECAPTCHA_SITE_KEY=$1
RECAPTCHA_SECRET_KEY=$2

sed -i "s/let recaptcha_site_key = .*/let recaptcha_site_key = $RECAPTCHA_SITE_KEY/" app/templater/static/js/main.js
sed -i "s/recaptcha_key = .*/recaptcha_key = $RECAPTCHA_SECRET_KEY/" app/config.ini


docker-compose build --no-cache 
docker-compose up -d

sleep 10s

docker-compose logs --no-color

#!/bin/sh
# Inject the reCAPTCHA keys from the environment into the app at container
# start. Unlike build_and_run.sh this rewrites only the copies inside the
# container, so the files in the working tree are never touched and the
# secret cannot be committed by accident. It also runs on GNU sed inside the
# image, which sidesteps the BSD sed incompatibility on macOS hosts.
set -e

if [ -n "$RECAPTCHA_SITE_KEY" ]; then
    sed -i "s|let recaptcha_site_key = .*|let recaptcha_site_key = \"$RECAPTCHA_SITE_KEY\"|" \
        /app/templater/static/js/main.js
    sed -i "s|RECAPTCHA_SITE_KEY|$RECAPTCHA_SITE_KEY|" \
        /app/templater/templates/layout.jinja2
fi

if [ -n "$RECAPTCHA_SECRET_KEY" ]; then
    sed -i "s|recaptcha_key = .*|recaptcha_key = $RECAPTCHA_SECRET_KEY|" /app/config.ini
fi

exec python3 -u runapp.py

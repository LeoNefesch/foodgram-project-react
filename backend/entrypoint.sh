#!/bin/bash
exec gunicorn --bind 0.0.0.0:$PORT_NGINX foodgram.wsgi:application
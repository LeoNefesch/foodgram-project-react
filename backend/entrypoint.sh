#!/bin/bash
exec gunicorn --bind 0:8000 foodgram.wsgi:application"
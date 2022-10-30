#!/bin/bash

domain=$1
threads=$2

python3 subfind.py $domain $threads

python3 dirbuss.py http://$domain $threads .php

python3 cralweb.py $domain

python3 webvulscan.py $domain

#python3 slack_not.py $domain

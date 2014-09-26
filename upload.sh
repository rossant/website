#!/usr/bin/env bash
if [ -n "$1" ]
	then
	cp pelicanconf.py pelicanconf_pub.py
	echo "SITEURL = 'http://cyrille.rossant.net'" | cat - pelicanconf_pub.py > /tmp/out && mv /tmp/out pelicanconf_pub.py

	pelican -s pelicanconf_pub.py
	git status
	git commit -am "$1" && git push
	cp -ar output/. ../rossant.github.io
	cd ../rossant.github.io
	git add --ignore-removal *
	git status
	git commit -am "$1" && git push
else
	echo "Please provide a commit message."
	exit 1
fi

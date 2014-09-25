#!/usr/bin/env bash
if [ -n "$1" ]
then
	pelican
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

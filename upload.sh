#!/usr/bin/env bash
cp -ar output/. ../rossant.github.io
cd ../rossant.github.io
git add --ignore-removal *
git commit -am "Update." && git push

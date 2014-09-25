#!/usr/bin/env bash
cp -avr output/. ../rossant.github.io
cd ../rossant.github.io
git commit -am "Update." && git push
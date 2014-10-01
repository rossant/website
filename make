#!/usr/bin/env python
import sys
import os
import argparse
import shutil
import subprocess
import http.server
import socketserver


def call(cmd):
	subprocess.Popen(list(cmd.split(' ')))

def conf():
	"Generate the derivate conf files."
	
	with open('pelicanconf.py', 'r') as f:
		contents = f.read()
	
	loc = "SITEURL = '/'\n" + contents
	pub = "SITEURL = 'http://cyrille.rossant.net'\n" + contents
	
	with open('pelicanconf_loc.py', 'w') as f:
		f.write(loc)
	
	with open('pelicanconf_pub.py', 'w') as f:
		f.write(pub)

def build(local=True):
	"Build the local HTML site in output."
	conf()
	which = 'loc' if local else 'pub'
	call("pelican -s=pelicanconf_%s.py" % which)

def serve():
	"Launch a local HTTP server."
	build()
	os.chdir('output')
	# subprocess.Popen(["python", "-m", "http.server"])
	call("python -m http.server")
	os.chdir('..')

def clean():
	"Clean all output and cache."
	shutil.rmtree('output')
	shutil.rmtree('cache')
	shutil.rmtree('__pycache__')

def upload():
	"""Build and push all changes online."""
	build(local=False)
	return
	call("git add content/*.md")
	call("git add content/*.ipynb")
	call("git commit -am %s")
	call("git push")
	call("cp -ar output/. ../rossant.github.io")
	call("cd ../rossant.github.io")
	call("git add --ignore-removal *")
	call('git commit -am "%s"')
	call('git push')

def kill():
	"Kill the running processes."
	call("killall python pelican")

commands = {
	None: build,
	'build': build,
	'serve': serve,
	'conf': conf,
	'clean': clean,
	'upload': upload,
	'kill': kill,
}

parser = argparse.ArgumentParser()
parser.add_argument('command', type=str, nargs='?')

args = parser.parse_args()
commands[args.command]()

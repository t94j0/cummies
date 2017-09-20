#!/usr/bin/env python

import os, stat
import json
import hashlib
import difflib
from subprocess import PIPE, Popen
from time import sleep, ctime

NEWFILE = " [File Created] "
RMFILE  = " [File Removed] "
CHFILE  = " [File Changed] "
NETMOD  = " [Net Modified] "
ss_db = None

def log(action, filename):
	if action == RMFILE:
		print("[" + ctime() + "]" + action + filename)
	elif action == NETMOD:
		print("[" + ctime() + "]" + action + filename)
	else:
		print("[" + str(ctime(os.path.getmtime(filename))) + "]" + action + filename)

def sha256_checksum(filename, block_size=65536):
	sha256 = hashlib.sha256()
	try:
		if stat.S_ISLNK(os.stat(filename).st_mode):
			return None
		elif stat.S_ISFIFO(os.stat(filename).st_mode):
			return None
		elif stat.S_ISSOCK(os.stat(filename).st_mode):
			return None
	except OSError:
		return None
	try:
		f = open(filename, 'rb')
		for block in iter(lambda: f.read(block_size), b''):
			sha256.update(block)
		return sha256.hexdigest()
	except IOError:
		print ("Could not read file:" + filename)

def dict_compare(d1, d2):
	d1_keys = set(d1.keys())
	d2_keys = set(d2.keys())
	intersect_keys = d1_keys.intersection(d2_keys)
	added = d1_keys - d2_keys
	removed = d2_keys - d1_keys
	changed = dict()
	for o in intersect_keys:
		if d1[o] != d2[o]:
			changed[o] = (d1[o], d2[o])
	return added, removed, changed

def compare(directory):
	dir_db = json.load(open(d.split("/")[-1] + ".db"))
	temp_db = discover(directory)
	added, removed, changed = dict_compare(temp_db, dir_db)
	if added:
		for new_file in added:
			log(NEWFILE, new_file)
	if removed:
		for rm_file in removed:
			log(RMFILE, rm_file)
	if changed:
		for ch_file in changed:
			log(CHFILE, ch_file)
	json.dump(temp_db, open(directory.split("/")[-1] + ".db", "w+"))

def discover(directory):
	file_dict = {}
	for root, dirs, files in os.walk(directory):
		for filename in files:
			path = os.path.join(root, filename)
			file_dict[path] = sha256_checksum(path)
	return file_dict

def ss(baseline=None):
	global ss_db
	if baseline is not None:
		proc = Popen(['ss', '-tulpn'], stdout=PIPE)
		ss_db = proc.communicate()[0]
	else:
		proc = Popen(['ss', '-tulpn'], stdout=PIPE)
		output = proc.communicate()[0]
		for line in output.split(os.linesep):
			if line not in ss_db.split(os.linesep):
				log(NETMOD, ' '.join(line.split()))
		ss_db = output


dirs = ["/home/chirality/testing", "/tmp"]

# Grab initial baselines
for d in dirs:
	files = discover(d)
	json.dump(files, open(d.split("/")[-1] + ".db", "w+"))

ss(baseline=True)

while True:
	sleep(10)
	for d in dirs:
		compare(d)
	ss()


#!/usr/bin/env python

import os, stat
import pickle
try:
    from hashlib import sha1
except ImportError:
    from sha import sha as sha1
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

def read_block(f, block_size):
	return f.read(block_size)

def sha1_checksum(filename, block_size=65536):
	sha_gen = sha1()
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
		buf = f.read(block_size)
		while len(buf) > 0:
			sha_gen.update(buf)
			buf = f.read(block_size)
		return sha_gen.hexdigest()
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

def compare_file_dict(directory):
	dir_db = pickle.load(open(d.split("/")[-1] + ".db"))
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
	pickle.dump(temp_db, open(directory.split("/")[-1] + ".db", "w+"))

def discover(directory):
	file_dict = {}
	for root, dirs, files in os.walk(directory):
		for filename in files:
			path = os.path.join(root, filename)
			file_dict[path] = sha1_checksum(path)
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
	file_dict = discover(d)
	pickle.dump(file_dict, open(d.split("/")[-1] + ".db", "w+"))

ss(baseline=True)

while True:
	sleep(10)
	for d in dirs:
		compare_file_dict(d)
	ss()


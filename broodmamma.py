#!/usr/bin/python3

import requests as req
import re as regx
import argparse
import os
import time
import itertools
from multiprocessing.dummy import Pool as ThreadPool 

''' 
	Initialization function.
	Creates parser for arguments
	required fields are: url, check, depth
	optional fields are: log
	Returns: url, (int)depth, (list)urls, check, log
'''
def init():
	print ("The spider comes...\n"
	"  / _ \\\n"
	"\\_\\(_)/_/\n"
	" _//\"\\\\_\n"
	"  /   \\\n")

	parser = argparse.ArgumentParser()
	parser.add_argument("url", help="Base URL to crawl")
	parser.add_argument("check", help="URL regex to test against when checking where to go")
	parser.add_argument("depth", help="Number of cycles to query \033[91mThis is greater than exponential, BE CAREFUL\033[0m")
	parser.add_argument("--log", help="Log the output size of queue, and visited sites. Filename based on check value", default=False, action="store_true")
	parser.add_argument("--threads", type=int, help="Number of threads to run", default=1)

	parser.add_argument("--js", help="Scan visited pages for javascript blocks and note where they exist", default=False, action="store_true")
	parser.add_argument("--php", help="Scan visited pages for php blocks and note where they exist", default=False, action="store_true")

	args = parser.parse_args()
	if args.log == True:
		input("Logging Enabled. Press any key to begin...")

	scripts = []
	if args.js:
		scripts.append('js')
	if args.php:
		scripts.append('php')
	if scripts != []:
		print("Script logging enabled. Checking for:",scripts)
	
	return args.url, int(args.depth), [args.url], args.check, args.log, args.threads, scripts

'''
	Grab all the URLs from the given webpage and parse them into a list
	Returns: list
'''
def crawler(base, check, scripts):
	# print("Parsing URLs found in:", base)
	r = req.get(base)
	subs = [(u.start(),u.end()) for u in regx.finditer('http(|s)\:\/\/[a-zA-Z0-9-\.\/\?\=\;,]+(?=\")', r.text)]
	urls = []
	for pair in subs:
		u = r.text[pair[0]:pair[1]]
		if checkParse(u, check):
			urls.append(u)

	if scripts != []:
		detected = checkScript(r.text, scripts)
		if detected != []:
			for d in detected:
				print("Found",d[0],"script in",base)
	return urls

'''
	Check if the parsed URL should be checked and checks if given regex matches URL
	Returns: bool
'''
def checkParse(urls, check):
	if regx.search(check, urls):
		return True
	return False

'''
	Check for certain types of scripts found on the crawled pages and log them
	Returns: list of arrays
'''
def checkScript(page, scripts):
	found = []
	for s in scripts:
		if s == 'js':
			subs = [(u.start(),u.end()) for u in regx.finditer('\<script.*\<\/script\>', page, regx.DOTALL)]
			for pair in subs:
				c = page[pair[0]:pair[1]]
				found.append([s,c])

		if s == 'php':
			subs = [(u.start(),u.end()) for u in regx.finditer('\<\?php.*\?\>', page, regx.DOTALL)]
			for pair in subs:
				c = page[pair[0]:pair[1]]
				found.append([s,c])
	return found

'''
	Main function to do the things
'''
if __name__ == "__main__":
	base, depth, queue, check, log, threads, scripts = init()

	msg = "Base: " + base + " | Depth: " + str(depth)  + " | Queue: " + str(queue) + " | Threads: " + str(threads) + "\n"

	# open file for logging	
	if log:
		log_file = check+'-'+str(int(time.time()))
		f = open(log_file, "w")
		f.write(msg)
	
	visited = []

	# make sure we dont spider forever, and ever, and ever....
	for d in range(0, depth):
		temp_urls = []

		# nothing else to do, this never seems to get hit so it seems useless
		if len(queue) == 0:
			exit("Exiting: Queue empty")
	
		# make threads do WORK! This portion does the scan for URLs alone
		with ThreadPool(threads) as pool:
			results = pool.starmap(crawler, zip(queue, itertools.repeat(check), itertools.repeat(scripts)))
		temp_urls = itertools.chain(*results)
		visited += queue
		queue = []

		# check if the urls are already visited or in the current queue. if not, add them to the queue
		for i in temp_urls:
			if i not in visited and i not in queue:
				# print("Appended", i)
				queue.append(i)
		
		# print("Queue",queue)
		# print("Visited", visited)
		msg = "-"*20+"\n" + "Queue size: " + str(len(queue)) + "\nVisited size: " + str(len(visited)) + "\n"+"-"*20+"\n"

		print(msg)

		if log:
			f.write(msg)
			f.write("\n".join(visited)+"\n")

	# close logging file
	if log:
		f.close()

	exit("Exiting: Depth reached")

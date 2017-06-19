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
	parser.add_argument("--log", help="Log the output size of queue, and visited sites. Filename based on check value", action="store_true")
	args = parser.parse_args()
	if args.log:
		raw_input("Logging Enabled. Press any key to begin...")
		log = True
	else:
		log = False

	return args.url, int(args.depth), [args.url], args.check, log


'''
	Grab all the URLs from the given webpage and parse them into a list
	Returns: list
'''
def getURLs(base, check):
	# print("Parsing URLs found in:", base)
	r = req.get(base)
	subs = [(u.start(),u.end()) for u in regx.finditer('http(|s)\:\/\/[a-zA-Z0-9-\.\/\?\=\;,]+(?=\")', r.text)]
	urls = []
	for pair in subs:
		u = r.text[pair[0]:pair[1]]
		if checkParse(u, check):
			urls.append(u)
	print(base + "-"*50 + ''.join(urls))
	input("Wait")
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
	Main function to do the things
'''
if __name__ == "__main__":
	base, depth, queue, check, log = init()

	msg = "Base: " + base + " | Depth: " + str(depth)  + " | Queue: " + str(queue) + "\n"

	# open file for logging	
	if log == True:
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
	
		# Remove item from queue and get all URLs from it	
#		while queue != []:
#			u = queue.pop(0)
#			visited.append(u)
#			temp_urls += getURLs(u, check)
		pool = ThreadPool(4)
		results = pool.starmap(getURLs, zip(queue, itertools.repeat(check)))[0]
		temp_urls = results

		visited += queue
		queue = []

		# check if the urls are already visited or in the current queue. if not, add them to the queue
		for i in temp_urls:
			if i not in visited and i not in queue:
				# print "Appended", i
				queue.append(i)
		
		# print("Queue",queue)
		# print("Visited", visited)
		msg = "-"*20+"\n" + "Queue size: " + str(len(queue)) + "\nVisited size: " + str(len(visited)) + "\n"+"-"*20+"\n"

		print(msg)

		if log == True:
			f.write(msg)
			f.write("\n".join(visited)+"\n")

	# close logging file
	if log == True:
		f.close()

	exit("Exiting: Depth reached")

#!/usr/bin/python3
import sys
import re

wordList = dict()
for line in open(".3000") :
	word = re.match(r"^[a-z]([-‘’`']?[a-z])*", line)
	if word :
		word = word.group(0)
		now = list()
		wordList[word] = now
	if line[0] == '【' :
		now.append(str.strip(line))
nowN = 0
totalN = len(sys.argv) - 1
for arg in sys.argv[1:] :
	nowN += 1
	if len(arg) == 0 :
		continue
	word = arg.lstrip()
	word = re.match(r"^[a-z]([-‘’`']?[a-z])*", word).group(0)
	ans = wordList[word]
	print(word, "({}/{})".format(nowN, totalN), end = '')
	sys.stdout.flush()
	input()
	for line in ans :
		print(line)
	print()

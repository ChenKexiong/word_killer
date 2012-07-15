#!/usr/bin/python3
import sys
import re
import select

wordList = dict()
failedList = list()
for line in open(".3000") :
	word = re.match(r"^[a-z]([-‘’`']?[a-z])*", line)
	if word :
		now = list()
		wordList[word.group(0)] = now
	if line[0:3] == '【考法' :
		now.append(str.strip(line))
nowN = 0
totalN = len(sys.argv) - 1
try :
	for arg in sys.argv[1:] :
		nowN += 1
		if len(arg) == 0 :
			continue
		word = arg.lstrip()
		word = re.match(r"^[a-z]([-‘’`']?[a-z])*", word).group(0)
		print(word, "({}/{})".format(nowN, totalN), end = '')
		sys.stdout.flush()
		ans = wordList[word]
		i, o, e = select.select([sys.stdin], [], [], 5)
		if i :
			input()
			idleTime = 0
		else :
			print()
			idleTime = 10
			failedList.append(word)
		for line in ans :
			print(line)
		i, o, e = select.select([sys.stdin], [], [], idleTime)
		if i :
			input()
		else :
			print()
except KeyboardInterrupt :
	print()
for word in failedList :
	print(word)

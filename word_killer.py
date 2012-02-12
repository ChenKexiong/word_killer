#!/usr/bin/env python3
import sys
import getopt
import re
import os
import random

VOICE_CMD='mplayer -really-quiet /usr/lobal/share/voice-mwc/{0}.wav &'
RE_WORD=r'[a-zA-Z](?:[a-zA-Z- ]*[a-zA-Z])?'

word_list={}
test_request=0
flags=set()
now=[]

class word:
	def __init__(self, args, dict_from):
		self.word=args[0]
		self.freq=int(args[1])
		if self.freq<1:
			self.freq=1
		self.failed_count=int(args[2])
		self.tested_count=int(args[3])
		self.dict_from=dict_from

	def merge(self, args, dict_from):
		self.freq+=args[0]
		self.failed_count+=args[1]
		self.tested_count+=args[2]
		self.dict_from=dict_from
	
	def play(self):
		global VOICE_CMD
		sys.stdout.flush()
		os.system(VOICE_CMD.format(self.word))

def parse_args():
	global test_request
	global flags

	operation_flag=False
	args=sys.argv[1:]
	try:
		optarg, args=getopt.gnu_getopt(args, 'ERT:W:v')
		for (key, value) in optarg:
			flags.add(key[1:])
			if key=='-T' or key=='-W':
				if value.isdigit():
					test_request=int(value)
				else:
					raise Exception('Invalid test request')
			if key=='-T' or key=='-W' or key=='-E' or key=='-R':
				if operation_flag:
					raise Exception('Too much operations')
				else:
					operation_flag=True

		if not operation_flag:
			raise Exception('Operation not found')

		if ('E' in flags and len(args)!=1) or len(args)<1:
			raise Exception('Too much or less arguments')
	except Exception as e:
		print(e)
		exit(1)

	return args

def read_dict(args):
	global word_list
	global RE_WORD

	pattern=re.compile(r'^\s*'+'('+RE_WORD+')'+3*(r'(?:\s+(\d+))?')+r'\s*$')
	try:
		for file_name in args:
			fin=open(file_name)
			for line in fin:
				temp=pattern.match(line)
				if temp:
					temp=temp.groups(0)
					if temp[0] in word_list.keys():
						word_list[temp[0]].merge(temp[1:], file_name)
					else:
						word_list[temp[0]]=word(temp, file_name)
				elif line != '\n':
					print('Invalid line: '+line)
			fin.close()
	except:
		print('Dict read error')
		exit(1)

def write_dict(file_name):
	try:
		fout=open(file_name, 'w')
		for item in sorted([k for k in word_list.values() if k.dict_from==file_name], key=lambda item:item.word.lower()):
			fout.write(item.word+' '+str(item.freq)+' '+str(item.failed_count)+' '+str(item.tested_count)+'\n')
		fout.close()
	except:
		print('Dict write error: ')
		exit(1)

def read_word():
	global RE_WORD
	pattern=re.compile(r'^\s*(~?)'+'('+RE_WORD+')'+r'\s*$')
	while True:
		m=pattern.match(input())
		if m:
			return (m.group(1)=='~', m.group(2))
	return ''

def read_choice():
	pattern=re.compile(r'^\s*([ynYN])\s*$')
	m=pattern.match(input())
	if m:
		return m.group(1).lower()
	return ''

def judge(res, buff):
	global flags
	res.tested_count+=1
	if 'T' in flags or 'R' in flags:
		if buff=='y':
			res.request-=1
		else:
			res.failed_count+=1
			if 'R' in flags:
				res.request+=1
	else:
		if buff==res.word:
			res.request-=1
		else:
			res.failed_count+=1

def test_init():
	global word_list
	for k in word_list.values():
		k.request=1 if 'R' in flags else test_request

def next_word():
	global now
	if len(now)==0:
		global word_list
		now=[k for k in word_list.values() if k.request>0]
		if len(now)==0:
			return 0
	return now.pop(random.randrange(0, len(now)))

if __name__=='__main__':
	args=parse_args()
	read_dict(args)

	if 'E' in flags:
		while True:
			delete, buff=read_word()
			if not delete:
				if buff in word_list.keys():
					word_list[buff].freq+=1
				else:
					word_list[buff]=word((buff, 1, 0, 0), args[0])
				print(buff+' '+str(word_list[buff].freq), end='\n\n')
				if 'v' in flags:
					word_list[buff].play()
			else:
				if buff in word_list.keys():
					del(word_list[buff])
					print('\''+buff+'\' deleted!')
				else:
					print('\''+buff+'\' not found!')
			write_dict(args[0])
	else:
		test_init()

		while True:
			res=next_word()
			if res==0:
				break
			while True:
				if 'T' in flags or 'R' in flags:				
					print(res.word, end=' ')
					print('(y/n{0})? '.format('/r' if 'v' in flags else ''), end='')
				else:
					if 'v' in flags:
						print('(r)? ', end='')
					else:
						print(res.word)
				if 'v' in flags:
					res.play()
				if 'W' in flags:
					delete, buff=read_word()
					if not ('v' in flags and buff=='r'):
						break
				else:
					buff=read_choice()
					if buff=='y' or buff=='n':
						break
			judge(res, buff)
			print()
			write_dict(res.dict_from)

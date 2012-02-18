#!/usr/bin/env python3
import sys
import getopt
import re
import os
import random

VOICE_CMD='mplayer /usr/local/share/voice-mwc/{0}.wav >/dev/null 2>/dev/null &'
RE_WORD=r'[a-zA-Z](?:[a-zA-Z-]*[a-zA-Z])?'

word_list = set()
st_list={}
test_request=0
flags=set()
now=[]

class word:
    def __init__(self, args):
        self.word=args[0]
        self.freq=int(args[1])
        self.failed_count=int(args[2])
        self.tested_count=int(args[3])
        self.request = 0

    def merge(self, args):
        self.freq+=int(args[1])
        self.failed_count+=int(args[2])
        self.tested_count+=int(args[3])
    
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
        optarg, args=getopt.gnu_getopt(args, 'RT:W:v')
        for (key, value) in optarg:
            flags.add(key[1:])
            if key=='-T' or key=='-W':
                if value.isdigit():
                    test_request=int(value)
                else:
                    raise Exception('Invalid test request')
            if key=='-T' or key=='-W' or key=='-R':
                if operation_flag:
                    raise Exception('Too many operations')
                else:
                    operation_flag=True
        if not operation_flag:
            raise Exception('Operation not found')
    except Exception as e:
        print(e)
        exit(1)
    return args

def read_dict(args):
    global st_list

    pattern = re.compile(r'^\s*'+'('+RE_WORD+')'+r'.*$')
    try:
        for filename in args:
            fin = open(filename)
            for line in fin:
                temp = pattern.match(line).groups(0)
                if not temp[0] in st_list.keys():
                    st_list[temp[0]]=word((temp[0], 0, 0, 0))
                if 'R' in flags:
                    if st_list[temp[0]].failed_count == 0 and st_list[temp[0]].tested_count >= 3:
                        pass
                    else:
                        st_list[temp[0]].request = 1
                        word_list.add(temp[0])
                elif test_request > 0:
                    st_list[temp[0]].request = test_request
                    word_list.add(temp[0])
            fin.close()
    except AttributeError as e:
        if line != '\n':
            print('Invalid line: '+line)
    except:
        print('Dict read error')
        fin.close()
        exit(1)

def read_statistics(filename):
    global st_list
    global RE_WORD

    pattern=re.compile(r'^\s*'+'('+RE_WORD+')'+3*(r'(?:\s+(\d+))?')+r'\s*$')
    try:
        fin=open(filename)
        for line in fin:
            temp=pattern.match(line)
            if temp:
                temp=temp.groups(0)
                if temp[0] in st_list.keys():
                    st_list[temp[0]].merge(temp)
                else:
                    st_list[temp[0]]=word(temp)
            elif line != '\n':
                print('Invalid line: '+line)
        fin.close()
    except IOError:
        pass
    except Exception as e:
        print('Statistics read error' + e)
        exit(1)

def write_statistics(filename):
    try:
        fout=open(filename, 'w')
        for item in sorted([k for k in st_list.values()], key=lambda item:item.word.lower()):
            fout.write(item.word+' '+str(item.freq)+' '+str(item.failed_count)+' '+str(item.tested_count)+'\n')
        fout.close()
    except:
        print('Statistics write error')
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
    global word_list
    res.tested_count+=1
    if 'T' in flags or 'R' in flags:
        if buff=='y':
            res.request-=1
            if res.request == 0:
                word_list.remove(res.word)
        else:
            res.failed_count+=1
            if 'R' in flags:
                res.request+=1
    else:
        if buff==res.word:
            res.request-=1
            if res.request == 0:
                word_list.remove(res.word)
        else:
            res.failed_count+=1

def next_word():
    global now
    if len(now)==0:
        now=[st_list[k] for k in word_list]
        if len(now)==0:
            return 0
    return now.pop(random.randrange(0, len(now)))

if __name__=='__main__':
    args=parse_args()
    read_statistics(".statistics")
    read_dict(args)

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
        write_statistics(".statistics")

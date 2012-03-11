#!/usr/bin/python3

def parse_args():
    import sys
    import getopt
    global flags
    global request

    flags = set()
    request = 1
    op = False
    args = sys.argv[1:]

    try:
        optargs, args = getopt.gnu_getopt(args, "RT")
        if len(optargs) < 1:
            raise Exception('no operation')
        if len(optargs) > 1:
            raise Exception('too many operations')
        flags.add(optargs[0][0][1:])
    except Exception as e:
        print(e)
        exit(1)
    return args

def read_dict(fname):
    global dic

    RE_WORD=r'[a-zA-Z](?:[a-zA-Z-]*[a-zA-Z])?'
    dic = []
    pattern = re.compile(r'^\s*('+RE_WORD+r')\s*(.*)\s*$')

    for line in open(fname, 'r'):
        try:
            temp = pattern.match(line).groups(0)
            dic.append(temp)
        except AttributeError as e:
            if (line != '\n'):
                print("invalid line: " + line)

def read_yn():
    pattern = re.compile(r'^\s*([ynYN])\s*$')
    m = pattern.match(input())
    if m:
        return m.group(1).lower()
    return ''

def term(sublist):
    import random
    requests = []
    now = 0
    colddown = [-4] * len(sublist)

    for i in range(len(sublist)):
        requests.append([i, request])
    while len(requests) > 0:
        while True:
            ran = random.randrange(0, len(requests))
            if now - colddown[ran] > 3:
                colddown[ran] = now
                break
        yes = ''
        while yes != 'y' and yes !='n':
            print('{0} (y/n)? '.format(sublist[requests[ran][0]][0]), end='')
            yes = read_yn()
        print(sublist[requests[ran][0]][1])
        print()
        requests[ran][1] += -1 if yes == 'y' else 1
        if requests[ran][1] == 0:
            requests.pop(ran)
        now += 1

import re
args = parse_args()
for fname in args:
    read_dict(fname)
if 'R' in flags:
    term(dic)
elif 'T' in flags:
    for i in range(0, len(dic), 10):
        term(dic[i:i + 10])

#!/usr/bin/env python
import itertools
import json
import random
import argparse
import re
import subprocess
import os
import sys
import shlex
import time
import glob
from time import localtime, strftime

def shcmd(cmd, ignore_error=False):
    print 'Doing:', cmd
    ret = subprocess.call(cmd, shell=True)
    print 'Returned', ret, cmd
    if ignore_error == False and ret != 0:
        exit(ret)
    return ret

def run_and_get_output(cmd):
    output = []
    cmd = shlex.split(cmd)
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    p.wait()

    return p.stdout.readlines()

class cd:
    """Context manager for changing the current working directory"""
    def __init__(self, newPath):
        self.newPath = newPath

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)

def ParameterCombinations(parameter_dict):
    """
    Get all the cominbation of the values from each key
    http://tinyurl.com/nnglcs9
    Input: parameter_dict={
                    p0:[x, y, z, ..],
                    p1:[a, b, c, ..],
                    ...}
    Output: [
             {p0:x, p1:a, ..},
             {..},
             ...
            ]
    """
    d = parameter_dict
    return [dict(zip(d, v)) for v in itertools.product(*d.values())]

#########################################################
# Git helper
# you can use to get hash of the code, which you can put
# to your results
def git_latest_hash():
    cmd = ['git', 'log', '--pretty=format:"%h"', '-n', '1']
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE)
    proc.wait()
    hash = proc.communicate()[0]
    hash = hash.strip('"')
    print hash
    return hash

def git_commit(msg='auto commit'):
    shcmd('git commit -am "{msg}"'.format(msg=msg),
            ignore_error=True)

########################################################
# table = [
#           {'col1':data, 'col2':data, ..},
#           {'col1':data, 'col2':data, ..},
#           ...
#         ]
def table_to_file(table, filepath, adddic=None):
    'save table to a file with additional columns'
    with open(filepath, 'w') as f:
        colnames = table[0].keys()
        if adddic != None:
            colnames += adddic.keys()
        colnamestr = ';'.join(colnames) + '\n'
        f.write(colnamestr)
        for row in table:
            if adddic != None:
                rowcopy = dict(row.items() + adddic.items())
            else:
                rowcopy = row
            rowstr = [rowcopy[k] for k in colnames]
            rowstr = [str(x) for x in rowstr]
            rowstr = ';'.join(rowstr) + '\n'
            f.write(rowstr)


def run001():
    shcmd("rm -fr /tmp/p*", ignore_error=True)
    shcmd("python main.py -i wl.json -o myworkload.txt")
    # shcmd("mpirun -mca btl ^openib -np 1 player myworkload.txt")
    lines = run_and_get_output("mpirun -np 1 player myworkload.txt")
    print lines

def load_json(fpath):
    decoded = json.load(open(fpath, 'r'))
    return decoded

def dump_json(obj, fpath):
    "obj is usually a dictionary"
    json.dump(obj, open(fpath, 'w'), indent=4)


def hbotest():
    hashes = ["x['offset']", "random.random()", "-x['offset']"]

    for i,h in enumerate(hashes):
        conf = load_json('testhbo.json')
        conf['singles']['single3']['offsetorderhash'] = h
        print conf
        dump_json(conf, str(i)+'.json')

        # workloadfile = 'testhbo.workload'
        # shcmd("rm -fr /scratch/p*", ignore_error=True)
        # shcmd("python main.py -i testhbo.json -o {f}".format(f=workloadfile))
        # lines = run_and_get_output("mpirun -mca btl ^openib -np 1 player {f}".format(f=workloadfile))
        # print lines

def main():
    #function you want to call
    run001()
    # hbotest()

def _main():
    parser = argparse.ArgumentParser(
            description="This file hold command stream." \
            'Example: python Makefile.py doexp1 '
            )
    parser.add_argument('-t', '--target', action='store')
    args = parser.parse_args()

    if args.target == None:
        main()
    else:
        # WARNING! Using argument will make it less reproducible
        # because you have to remember what argument you used!
        targets = args.target.split(';')
        for target in targets:
            eval(target)

if __name__ == '__main__':
    _main()

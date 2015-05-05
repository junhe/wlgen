import json
import argparse
import producer
import random
import numpy as np
import Queue
import os

def load_json(fpath):
    decoded = json.load(open(fpath, 'r'))
    return decoded

def apply_single_model_01(conf, prod, fpath):
    if conf["mode"] != 1:
        print 'wrong mode'
        exit(1)

    optype = conf["type"]

    prod.addUniOp2('open', 0, fpath)
    for item in conf["list"]:
        prod.addReadOrWrite2(op=optype, pid=0, path=fpath,
                off=item["off"], len=item["size"])
    prod.addUniOp2('close', 0, fpath)

    # prod.display()

def get_lognorm_list(mu, sigma, n, factor):
    l = [int(random.lognormvariate(mu, sigma)*factor)
            for i in range(n)]
    return l

def apply_single_model_02(conf, prod, fpath):
    if conf["mode"] != 2:
        print 'wrong mode'
        exit(1)

    n_access = conf["n_access"]
    optype = conf["type"]

    off_mu = conf["offsetdist"]["mu"]
    off_sigma = conf["offsetdist"]["sigma"]
    offsets = get_lognorm_list(off_mu, off_sigma, n_access, 1000)

    size_mu = conf["sizedist"]["mu"]
    size_sigma = conf["sizedist"]["sigma"]
    sizes = get_lognorm_list(size_mu, size_sigma, n_access, 1000)

    # sort offset from small to large
    offsets.sort()

    # sort the sizes
    sizes.sort(key = lambda x: eval(conf["sizeorderhash"]))

    # form offset, size pairs
    pairs = [ {'offset':off, 'size':size} for off, size in zip(offsets, sizes)]

    # sort pairs by offsetorder hash
    pairs.sort(key = lambda x: eval(conf["offsetorderhash"]))

    prod.addUniOp2('open', 0, fpath)
    for pair in pairs:
        # print pair
        prod.addReadOrWrite2(op=optype, pid=0, path=fpath,
                off=pair["offset"], len=pair["size"])
    prod.addUniOp2('close', 0, fpath)

    # prod.display()

def apply_single_model_03(conf, prod, fpath):
    if conf["mode"] != 3:
        print 'wrong mode'
        exit(1)

    n_access = conf["n_access"]
    optype = conf["type"]

    size_mu = conf["sizedist"]["mu"]
    size_sigma = conf["sizedist"]["sigma"]
    sizes = get_lognorm_list(size_mu, size_sigma, n_access, 1000)

    # sort the sizes
    sizes.sort(key = lambda x: eval(conf["sizeorderhash"]))

    # generate offsets
    offsets = list(np.cumsum(sizes))
    offsets.insert(0, 0)
    offsets = offsets[0:-1]

    # form offset, size pairs
    pairs = [ {'offset':off, 'size':size} for off, size in zip(offsets, sizes)]

    # sort pairs by offsetorder hash
    pairs.sort(key = lambda x: eval(conf["offsetorderhash"]))

    prod.addUniOp2('open', 0, fpath)
    for pair in pairs:
        # print pair
        prod.addReadOrWrite2(op=optype, pid=0, path=fpath,
                off=pair["offset"], len=pair["size"])
    prod.addUniOp2('close', 0, fpath)

    # prod.display()

def create_namespace_breadthfirst(conf, prod, singles_conf):
    depth = conf['shape']['depth']
    fanout = conf['shape']['fanout']
    rootdir = conf['rootdir']

    q = Queue.Queue()

    q.put(rootdir) # put the root in

    while not q.empty():
        item = q.get()

        # create the actual directory here
        #print 'creating', item
        prod.addDirOp2('mkdir', 0, item)

        # create files
        singlepat = conf['singlepattern']
        nfile = conf['filesperdir']
        create_files_in_dir(item, nfile, singlepat, singles_conf, prod)
        # print 'after creating files'

        # put children of item to the queue
        if len(item.strip('/').split('/')) \
            - len(rootdir.strip('/').split('/')) < depth:
            for i in range(fanout):
                newitem = os.path.join(item, str(i))
                # print 'adding', newitem, 'to q'
                q.put(newitem)

    # prod.display()

def create_namespace_depthfirst(conf, prod, singles_conf):
    depth = conf['shape']['depth']
    fanout = conf['shape']['fanout']
    rootdir = conf['rootdir']

    s = []

    s.append(rootdir) # append() = push()

    while len(s) > 0:
        dentry = s.pop()

        # create dentry
        prod.addDirOp2('mkdir', 0, dentry)

        # create files
        singlepat = conf['singlepattern']
        nfile = conf['filesperdir']
        create_files_in_dir(dentry, nfile, singlepat, singles_conf, prod)

        # put children of item to the queue
        if len(dentry.strip('/').split('/')) \
            - len(rootdir.strip('/').split('/')) < depth:
            for i in reversed(range(fanout)):
                newitem = os.path.join(dentry, str(i))
                #print 'adding', newitem, 'to q'
                s.append(newitem)

    # prod.display()

def create_namespace_random(conf, prod, singles_conf):
    depth = conf['shape']['depth']
    fanout = conf['shape']['fanout']
    rootdir = conf['rootdir']

    s = []
    s.append(rootdir) # append() = push()

    while len(s) > 0:
        # randomly get one, all the items in the list s can
        # be immediately created
        dentry = random.sample(s, 1)[0]
        s.remove(dentry)

        # create dentry
        prod.addDirOp2('mkdir', 0, dentry)

        # create files
        singlepat = conf['singlepattern']
        nfile = conf['filesperdir']
        create_files_in_dir(dentry, nfile, singlepat, singles_conf, prod)

        # put children of item to the queue
        if len(dentry.strip('/').split('/')) \
            - len(rootdir.strip('/').split('/')) < depth:
            for i in reversed(range(fanout)):
                newitem = os.path.join(dentry, str(i))
                #print 'adding', newitem, 'to q'
                s.append(newitem)

    # prod.display()

def create_files_in_dir(dirpath, nfile, singlepat, singles_conf, prod):
    for i in range(nfile):
        fpath = os.path.join(dirpath, 'file.'+singlepat+'.'+str(i))
        singleconf = singles_conf[singlepat]
        if singleconf['mode'] == 1:
            apply_single_model_01(singleconf, prod, fpath)
        elif singleconf['mode'] == 2:
            apply_single_model_02(singleconf, prod, fpath)
        elif singleconf['mode'] == 3:
            apply_single_model_03(singleconf, prod, fpath)

def build_workload(global_conf):
    seq = global_conf['creationsequence']
    prod = producer.Producer(rootdir="/tmp/",
            tofile="/tmp/producedfile.txt")

    for spaceid in seq:
        create_namespace(spaceid, prod, global_conf)

def create_namespace(namespace_id, prod, global_conf):
    namespace_conf= global_conf['namespaces'][namespace_id]
    singles_conf = global_conf['singles']

    if namespace_conf['pattern'] == 'breadthfirst':
        create_namespace_breadthfirst(namespace_conf, prod, singles_conf)
    elif namespace_conf['pattern'] == 'depthfirst':
        create_namespace_depthfirst(namespace_conf, prod, singles_conf)
    elif namespace_conf['pattern'] == 'random':
        create_namespace_random(namespace_conf, prod, singles_conf)

def main():
    parser = argparse.ArgumentParser(
            description="this is a WLGEN parser. It takes a WLGEN code and produce "\
                        "workload description file"
            )
    parser.add_argument('-i', '--input', action='store')
    parser.add_argument('-o', '--output', action='store')
    args = parser.parse_args()

    if args.input == None or args.output == None:
        print parser.print_help()
        exit(1)

    global_conf = load_json(args.input)
    seq = global_conf['creationsequence']

    prod = producer.Producer(rootdir="/tmp/",
            tofile=args.output)

    for spaceid in seq:
        create_namespace(spaceid, prod, global_conf)

    prod.saveWorkloadToFile()

if __name__ == '__main__':
    main()


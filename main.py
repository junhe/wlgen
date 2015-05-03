import json
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

    for item in conf["list"]:
        print item
        prod.addReadOrWrite2(op=optype, pid=0, path=fpath,
                off=item["off"], len=item["size"])

    prod.display()

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

    for pair in pairs:
        print pair
        prod.addReadOrWrite2(op=optype, pid=0, path=fpath,
                off=pair["offset"], len=pair["size"])

    prod.display()

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

    for pair in pairs:
        print pair
        prod.addReadOrWrite2(op=optype, pid=0, path=fpath,
                off=pair["offset"], len=pair["size"])

    prod.display()

def create_namespace_breadthfirst(conf, prod):
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

        # put children of item to the queue
        if len(item.strip('/').split('/')) < depth:
            for i in range(fanout):
                newitem = os.path.join(item, str(i))
                #print 'adding', newitem, 'to q'
                q.put(newitem)

    prod.display()

def create_namespace_depthfirst(conf, prod):
    depth = conf['shape']['depth']
    fanout = conf['shape']['fanout']
    rootdir = conf['rootdir']

    s = []

    s.append(rootdir) # append() = push()

    while len(s) > 0:
        dentry = s.pop()

        # create dentry
        prod.addDirOp2('mkdir', 0, dentry)

        # put children of item to the queue
        if len(dentry.strip('/').split('/')) < depth:
            for i in reversed(range(fanout)):
                newitem = os.path.join(dentry, str(i))
                #print 'adding', newitem, 'to q'
                s.append(newitem)

    prod.display()

def create_namespace_random(conf, prod):
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

        # put children of item to the queue
        if len(dentry.strip('/').split('/')) < depth:
            for i in reversed(range(fanout)):
                newitem = os.path.join(dentry, str(i))
                #print 'adding', newitem, 'to q'
                s.append(newitem)

    prod.display()

def main():
    prod = producer.Producer(rootdir="/tmp/",
            tofile="/tmp/producedfile.txt")

    global_conf = load_json('wl.json')
    # apply_single_model_01(global_conf["singles"]["single1"], prod)
    #apply_single_model_02(global_conf["singles"]["single2"], prod, 'mypath')
    #apply_single_model_03(global_conf["singles"]["single3"], prod, 'mypath')
    #create_namespace_depthfirst(global_conf['namespaces']['namespace1'], prod)
    create_namespace_random(global_conf['namespaces']['namespace1'], prod)


if __name__ == '__main__':
    main()


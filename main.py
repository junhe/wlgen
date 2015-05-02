import json
import producer



def load_json(fpath):
    decoded = json.load(open(fpath, 'r'))
    #print decoded
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

def apply_single_model_02(conf, prod, fpath):
    if conf["mode"] != 2:
        print 'wrong mode'
        exit(1)

    n_access = conf["n_access"]
    optype = conf["type"]

    off_mu = conf["offsetdist"]["mu"]
    off_sigma = conf["offsetdist"]["sigma"]
    offsets = [random.lognormvariate(off_mu, off_sigma) for i in range(n_access)]

    size_mu = conf["sizedist"]["mu"]
    size_sigma = conf["sizedist"]["sigma"]
    sizes = [random.lognormvariate(size_mu, size_sigma) for i in range(n_access)]

def main():
    prod = producer.Producer(rootdir="/tmp/",
            tofile="/tmp/producedfile.txt")

    global_conf = load_json('./tutorial/wl.json')
    apply_single_model_01(global_conf["single"], prod)

if __name__ == '__main__':
    main()




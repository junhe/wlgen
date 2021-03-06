import os
import itertools
import re

class Producer:
    """
    """
    def __init__ (self, np=1, startOff=0, nwrites_per_file=1, nfile_per_dir=1,
              ndir_per_pid=1, wsize=1, wstride=1, rootdir="", tofile="",
              fsync_per_write=False, fsync_before_close=True):
        self.setParameters(
              np, startOff, nwrites_per_file, nfile_per_dir, ndir_per_pid,
              wsize, wstride, rootdir, tofile, fsync_per_write, fsync_before_close)
        self.workload = ""

    def addReadOrWrite(self, op, pid, dirid, fileid, off, len):
        "op: read/write"
        path = self.getFilepath(dir=dirid, pid=pid, file_id=fileid)
        entry = str(pid)+";"+path+";"+op.lower()+";"+str(off)+";"+str(len)+"\n"
        self.workload += entry

    def addReadOrWrite2(self, op, pid, path, off, len):
        "op: read/write"
        fullpath = self.getFullpath(path)
        entry = str(pid)+";"+fullpath+";"+op.lower()+";"+str(off)+";"+str(len)+"\n"
        self.workload += entry

    def addUniOp(self, op, pid, dirid, fileid):
        "op: open/close/fsync"
        path = self.getFilepath(dir=dirid, pid=pid, file_id=fileid)
        entry = str(pid)+";"+path+";"+op.lower()+"\n";
        self.workload += entry

    def addUniOp2(self, op, pid, path):
        """
        All functions with suffix '2' use path instead of (dirid, fileid)
        op: open/close/fsync
        """
        fullpath = self.getFullpath(path)
        entry = str(pid)+";"+fullpath+";"+op.lower()+"\n";
        self.workload += entry

    def addDirOp(self, op, pid, dirid):
        path = self.getDirpath(dir=dirid, pid=pid)
        entry = str(pid)+";"+path+";"+op.lower()+"\n";
        self.workload += entry

    def addDirOp2(self, op, pid, path):
        fullpath = self.getFullpath(path)
        entry = str(pid)+";"+fullpath+";"+op.lower()+"\n";
        self.workload += entry

    def addOSOp(self, op, pid):
        """
        op: sync(call sync())
        This assigned pid should do this
        """
        entry = str(pid)+";"+"NA"+";"+op.lower()+"\n";
        self.workload += entry

    def addSetaffinity(self, pid, cpuid):
        entry = str(pid)+";"+"NA"+";"+"sched_setaffinity;"+str(cpuid)+'\n'
        self.workload += entry

    def display(self):
        print self.workload

    def setParameters(self,
              np, startOff, nwrites_per_file, nfile_per_dir, ndir_per_pid,
              wsize, wstride, rootdir, tofile, fsync_per_write, fsync_before_close):
        self.np = np
        self.startOff = startOff

        self.nwrites_per_file = nwrites_per_file
        self.nfile_per_dir = nfile_per_dir
        self.ndir_per_pid = ndir_per_pid

        self.wsize = wsize
        self.wstride = wstride

        self.rootdir = rootdir
        self.tofile = tofile

        self.fsync_per_write = fsync_per_write
        self.fsync_before_close = fsync_before_close

    def saveWorkloadToFile(self):
         self.save2file(self.workload, self.tofile)

    def save2file(self, workload_str, tofile=""):
        if tofile != "":
            with open(tofile, 'w') as f:
                f.write(workload_str)
                f.flush()
            print "save2file. workload saved to file"
        else:
            print "save2file. no output file assigned"

    def produce_rmdir (self, np, ndir_per_pid, rootdir, pid=0, tofile=""):
        workload = ""
        for p in range(np):
            for dir in range(ndir_per_pid):
                path = self.getDirpath(p, dir)
                entry = str(p)+";"+path+";"+"rm"+"\n";
                workload += entry

        return workload

    def produce (self,
              np, startOff, nwrites_per_file, nfile_per_dir, ndir_per_pid,
              wsize, wstride, rootdir, tofile="",
              fsync_per_write=False,
              fsync_before_close=True):
        self.np = np
        self.startOff = startOff

        # pid->dir->file->writes
        self.nwrites_per_file = nwrites_per_file
        self.nfile_per_dir = nfile_per_dir
        self.ndir_per_pid = ndir_per_pid

        self.wsize = wsize
        self.wstride = wstride
        self.fsync_per_write = fsync_per_write
        self.fsync_before_close = fsync_before_close

        self.rootdir = rootdir
        self.tofile = tofile

        self.workload = self._produce()

        if tofile != "":
            self.saveWorkloadToFile()

        return self.workload


    def getFilepath(self, dir, pid, file_id ):
        fname = ".".join( ['pid',str(pid).zfill(5), 'file',
            str(file_id).zfill(5)] )
        dirname = self.getDirpath(pid, dir)
        return os.path.join(dirname, fname)

    def getDirpath(self, pid, dir):
        dirname = "pid" + str(pid).zfill(5) + ".dir" + str(dir).zfill(5) + "/"
        return os.path.join(self.rootdir, dirname)

    def getFullpath(self, path):
        return os.path.join(self.rootdir, path)

    def _produce(self):
        workload = ""

        # make dir
        for p in range(self.np):
            for dir in range(self.ndir_per_pid):
                path = os.path.join(self.rootdir, self.getDirpath(p, dir))
                entry = str(p)+";"+path+";"+"mkdir"+"\n";
                workload += entry

        # Open file
        for fid in range(self.nfile_per_dir):
            for dir in range(self.ndir_per_pid):
                for p in range(self.np):
                    path = self.getFilepath(dir, p, fid)
                    entry = str(p)+";"+path+";"+"open"+"\n";
                    workload += entry

        #cur_off[pid][dir][fid]
        cur_off = [[[self.startOff for x in xrange(self.nfile_per_dir)] for x in xrange(self.ndir_per_pid)] for x in xrange(self.np)]
        for w_index in range(self.nwrites_per_file):
            for fid in range(self.nfile_per_dir):
                for dir in range(self.ndir_per_pid):
                    for p in range(self.np):
                        size = self.wsize
                        path = self.getFilepath(dir, p, fid)

                        entry = str(p)+";"+path+";"+"write"+";"+str(cur_off[p][dir][fid])+";"+str(size)+"\n"

                        cur_off[p][dir][fid] += self.wstride

                        workload += entry

                        if self.fsync_per_write:
                            entry = str(p)+";"+path+";"+"fsync"+"\n";
                            workload += entry

        # fsync file
        if self.fsync_before_close:
            for fid in range(self.nfile_per_dir):
                for dir in range(self.ndir_per_pid):
                    for p in range(self.np):
                        path = self.getFilepath(dir, p, fid)
                        entry = str(p)+";"+path+";"+"fsync"+"\n";
                        workload += entry


        # close file
        for fid in range(self.nfile_per_dir):
            for dir in range(self.ndir_per_pid):
                for p in range(self.np):
                    path = self.getFilepath(dir, p, fid)
                    entry = str(p)+";"+path+";"+"close"+"\n";
                    workload += entry

        return workload

class SysCall(dict):
    def __init__(self, dic):
        super(SysCall, self).__init__(dic)
        assert not self.has_key("NA")

    def __str__(self):

        if self['name'] in ("write", "read"):
            items = ['pid', 'path', 'name', 'offset', 'count']
        elif self['name'] in ("open", "close", "fsync", "mkdir"):
            items = ['pid', 'path', 'name']
        elif self['name'] in ("sync",):
            items = ['pid', 'NA', 'name']
            self['NA'] = 'NA'
        elif self['name'] in ("sched_setaffinity",):
            items = ['pid', "NA", "name", 'cpuid']
            self['NA'] = 'NA'
        else:
            raise RuntimeError("Syscall {} is not supported."\
                .format(self['name']))

        if set(items) != set(self.keys()):
            raise RuntimeError("{} != {}".format(set(items), set(self.keys())))

        entry = ';'.join([str(self[k]) for k in items])

        return entry


class WorkloadList(object):
    """The class encapsulate operations in a more intuitive way."""
    def __init__(self, mountpoint):
        self.action_list = []
        self.mountpoint = mountpoint

    def get_abs_path(self, path):
        if not os.path.isabs(path):
            path = os.path.join(self.mountpoint, path)
        return path

    def add_call(self, **kwargs):
        # change path if necessary
        if kwargs.has_key('path'):
            kwargs['path'] = self.get_abs_path(kwargs['path'])

        self.action_list.append(SysCall(kwargs))

    def __str__(self):
        return '\n'.join([str(x) for x in self.action_list])


if __name__ == '__main__':
    wl = WorkloadList('/tmp')
    wl.add_call(name='mkdir', pid=0, path='mydir')
    wl.add_call(name='open', pid=0, path='mypath')
    wl.add_call(name='write', pid=0, path='mypath', offset=0, count=4096)
    wl.add_call(name='read', pid=0, path='mypath', offset=0, count=4096)
    wl.add_call(name='fsync', pid=0, path='mypath')
    wl.add_call(name='close', pid=0, path='mypath')
    wl.add_call(name='sync', pid=0)
    wl.add_call(name='sched_setaffinity', pid=0, cpuid=0)

    print wl
    print str(wl)

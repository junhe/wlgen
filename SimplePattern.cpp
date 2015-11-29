#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>

#include "SimplePattern.h"
#include "Util.h"

SimplePattern::SimplePattern(int file_size, bool fsync, bool sync, 
        int write_size, int n_writes, enum PATTERN pattern, 
        const char *file_path, string tag)
    : _file_size(file_size), _fsync(fsync), _sync(sync), _write_size(write_size), _n_writes(n_writes),
    _pattern(pattern), _file_path(file_path), _tag(tag)
{
    string pat_str;
    if (_pattern == SEQUENTIAL)
        pat_str = "sequential";
    else
        pat_str = "random";

    cout << "--- Workload summary ---" << endl;
    cout << "filesize    " << _file_size << endl;
    cout << "fsync       " << _fsync << endl;
    cout << "sync        " << _sync << endl;
    cout << "writesize   " << _write_size << endl;
    cout << "pattern     " << pat_str << endl;
    cout << "path        " << _file_path << endl;
    cout << "tag         " << _tag << endl;

}

void SimplePattern::run()
{
    int i;
    int fd;
    char *buf;
    off_t offset;
    ssize_t n_chunks;

    fd = open(_file_path.c_str(), O_CREAT | O_RDWR, 0666);
    if (fd == -1) {
        perror("error opening file");
        exit(1);
    }

    buf = (char *)malloc(_write_size);
    n_chunks = _file_size / _write_size;

    srand(1);

    if (n_chunks > RAND_MAX) {
        cerr << "n_chunks is larger than RAND_MAX, we will not be able to "
            << "generate random number in the range of 0...n_chunks." << endl;
        exit(1);
    }

    for ( i = 0; i < _n_writes; i++) {
        if (_pattern == SEQUENTIAL) {
            offset = (i % n_chunks) * _write_size;
        } else if (_pattern == RANDOM) {
            offset = (rand() % n_chunks) * _write_size;
        }
        // cout << "offset " << offset << endl;
        Util::PwriteN(buf, _write_size, offset, fd);

        if (_fsync == true) {
            // cout << "fsync" << endl;
            fsync(fd);
        } 
    }

    if (_sync == true) {
        // cout << "sync" << endl;
        sync();
    } 
    close(fd);

    free(bug);
}


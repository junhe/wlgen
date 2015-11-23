#ifndef __SIMPLEPATTERN_H__
#define __SIMPLEPATTERN_H__

#include <string>
#include <iostream>
#include <stdlib.h>
#include <string.h>

using namespace std;

enum PATTERN { SEQUENTIAL, RANDOM };

class SimplePattern {
    public:
        SimplePattern(int file_size, int write_size, int n_writes, 
            enum PATTERN pattern, const char *file_path);
        void run();

    private:
        int _file_size;
        int _write_size;;
        int _n_writes;
        string _file_path;
        enum PATTERN _pattern;
};


#endif

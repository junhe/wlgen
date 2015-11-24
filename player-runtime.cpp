#include <iostream>
// #include <mpi.h>
#include <string>
#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>

#include "SimplePattern.h"

using namespace std;

class WorkloadConfig {
    public:
        int file_size;
        bool fsync;
        bool sync;
        int write_size;;
        int n_writes;
        string file_path;
        enum PATTERN pattern;

        void display() {
            cout << "file_size " << file_size << endl
                 << "write_size " << write_size << endl 
                 << "n_writes " << n_writes << endl 
                 << "file_path " << file_path << endl 
                 << "pattern " << pattern << endl;
        }
};


void print_usage(char **argv)
{
    printf("Usage: %s -f file_size(bytes) -w write_size(bytes) -n n_writes -p "
        "pattern(sequential|random) -y fsync(0|1) -s sync(0|1) -l file_path\n", argv[0]);
}

void parse_args(int argc, char**argv, WorkloadConfig &wlconf)
{
    const char *config = "f:w:n:p:l:y:s:";
    char c;
    int index;

    if (argc != 15) {
        cout << "argc " << argc << endl;
        print_usage(argv);
        exit(1);
    }

    opterr = 0;
    while ((c = getopt (argc, argv, config)) != -1)
        switch (c)
        {
            case 'f':
                wlconf.file_size = atoi(optarg); // optarg points to the argument of c
                break;
            case 'y':
                wlconf.fsync = bool(atoi(optarg)); // optarg points to the argument of c
                break;
            case 's':
                wlconf.sync = bool(atoi(optarg)); // optarg points to the argument of c
                break;
            case 'w':
                wlconf.write_size = atoi(optarg); // optarg points to the argument of c
                break;
            case 'n':
                wlconf.n_writes = atoi(optarg); // optarg points to the argument of c
                break;
            case 'p':
                {
                    string s(optarg); // for easier comparison
                    if ( s == "sequential" ) {
                        wlconf.pattern = SEQUENTIAL;
                    } else if ( s == "random" ) {
                        wlconf.pattern = RANDOM;
                    } else {
                        cout << "pattern " << optarg << " not supported." 
                            << endl;
                        print_usage(argv);
                        exit(1);
                    }
                    break;
                }
            case 'l':
                wlconf.file_path = optarg; // optarg points to the argument of c
                break;
            case '?':
                /* When getopt encounters an unknown option character or an option with a missing required argument, it stores that option character in this variable. You can use this for providing your own diagnostic messages. */

                if (isprint (optopt))
                  fprintf (stderr, "Unknown option `-%c'.\n", optopt);
                else
                  fprintf (stderr,
                           "Unknown option character `\\x%x'.\n",
                           optopt);
                cout << "unkown";
                cout << "encounters an unknown option or option missing required arguments" << endl;
                print_usage(argv);
                exit(1);
            default:
                cout << "default" << endl;
                print_usage(argv);
                exit(1);
        }

    /* This variable is set by getopt to the index of the next element of the argv array to be processed. Once getopt has found all of the option arguments, you can use this variable to determine where the remaining non-option arguments begin. The initial value of this variable is 1. */
    for (index = optind; index < argc; index++)
        printf ("Non-option argument %s\n", argv[index]);
}


int main(int argc, char **argv)
{
    struct timeval start, end, result;
    WorkloadConfig wlconf;

    parse_args(argc, argv, wlconf);

    // wlconf.display();

    SimplePattern simplepattern(wlconf.file_size, 
            wlconf.fsync,
            wlconf.sync,
            wlconf.write_size, wlconf.n_writes, 
            wlconf.pattern, wlconf.file_path.c_str());

    // SimplePattern simplepattern(64, 32, 10, SEQUENTIAL, "/tmp/littletest");
    // SimplePattern simplepattern(64, 32, 10, RANDOM, "/tmp/littletest");

    gettimeofday(&start, NULL);

    // run the workload
    simplepattern.run();

    gettimeofday(&end, NULL);

    timersub(&end, &start, &result);
    printf("duration %ld.%ld\n", result.tv_sec, result.tv_usec);
    printf("start    %ld.%ld\n", start.tv_sec, start.tv_usec);
    printf("end      %ld.%ld\n", end.tv_sec, end.tv_usec);

    return 0;
}




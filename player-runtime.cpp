#include <iostream>
// #include <mpi.h>
#include <string>
#include <stdlib.h>
#include <assert.h>
#include <stdio.h>
#include <sys/time.h>
#include <time.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#include "SimplePattern.h"

using namespace std;

class WorkloadConfig {
    public:
        int file_size;
        bool file_size_set;
        bool fsync;
        bool fsync_set;
        bool sync;
        bool sync_set;
        int write_size;
        bool write_size_set;
        int n_writes;
        bool n_writes_set;
        string file_path;
        bool file_path_set;
        enum PATTERN pattern;
        bool pattern_set;
        string tag;
        bool tag_set;
        string markerfile;
        bool markerfile_set;

        void display() {
            cout << "file_size  " << file_size << endl
                 << "write_size " << write_size << endl 
                 << "n_writes   " << n_writes << endl 
                 << "file_path  " << file_path << endl 
                 << "tag        " << tag << endl 
                 << "fsync      " << fsync << endl 
                 << "sync       " << sync << endl 
                 << "markerfile " << markerfile << endl 
                 << "pattern    " << pattern << endl;
        }

        WorkloadConfig() {
            file_size_set = false;
            fsync_set = false;
            sync_set = false;
            write_size_set = false;
            n_writes_set = false;
            file_path_set = false;
            pattern_set = false;
            tag_set = false;
            markerfile_set = false;
        }

        bool is_well_set() {
            if (file_size_set == false ||
                fsync_set == false ||
                sync_set == false ||
                write_size_set == false ||
                n_writes_set == false ||
                file_path_set == false ||
                pattern_set == false ||
                tag_set == false ||
                markerfile_set == false) {
                return false;
            } else {
                return true;
            }
        }
};


void print_usage(char **argv)
{
    printf("Usage: %s -f file_size(bytes) -w write_size(bytes) -n n_writes -p "
        "pattern(sequential|random) -y fsync(0|1) -s sync(0|1) -l file_path "
        "-t tag -m marker-file\n", argv[0]);
    printf("Example: ./player-runtime -f 1000 -w 100 -n 10 -p random -y 1 "
        "-s 1 -l ./here -t tag001 -m /dev/null\n");
}

void parse_args(int argc, char**argv, WorkloadConfig &wlconf)
{
    const char *config = "f:w:n:p:l:y:s:t:m:";
    char c;
    int index;

    opterr = 0;
    while ((c = getopt (argc, argv, config)) != -1)
        switch (c)
        {
            case 'm':
                wlconf.markerfile = optarg; // optarg points to the argument of c
                wlconf.markerfile_set = true;
                break;
            case 't':
                wlconf.tag = optarg; // optarg points to the argument of c
                wlconf.tag_set = true;
                break;
            case 'f':
                wlconf.file_size = atoi(optarg); // optarg points to the argument of c
                wlconf.file_size_set = true;
                break;
            case 'y':
                wlconf.fsync = bool(atoi(optarg)); // optarg points to the argument of c
                wlconf.fsync_set = true;
                break;
            case 's':
                wlconf.sync = bool(atoi(optarg)); // optarg points to the argument of c
                wlconf.sync_set = true;
                break;
            case 'w':
                wlconf.write_size = atoi(optarg); // optarg points to the argument of c
                wlconf.write_size_set = true;
                break;
            case 'n':
                wlconf.n_writes = atoi(optarg); // optarg points to the argument of c
                wlconf.n_writes_set = true;
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
                    wlconf.pattern_set = true;
                    break;
                }
            case 'l':
                wlconf.file_path = optarg; // optarg points to the argument of c
                wlconf.file_path_set = true;
                break;
            case '?':
                /* When getopt encounters an unknown option character or an 
                 * option with a missing required argument, it stores that 
                 * option character in this variable. You can use this for 
                 * providing your own diagnostic messages. */

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

void append_to_marker_file(const char *filepath, const char *mark)
{
    int fd;
    int len;
    string markstr(mark);

    fd = open(filepath, O_APPEND | O_WRONLY);
    if (fd == -1) {
        perror("cannot open file.");
        exit(1);
    }

    markstr = "MARK:" + markstr + '\n';
    write(fd, markstr.c_str(), markstr.length());

    close(fd);
}

int main(int argc, char **argv)
{
    struct timeval start, end, result;
    WorkloadConfig wlconf;

    parse_args(argc, argv, wlconf);

    if (! wlconf.is_well_set()) {
        printf("Some required options are not set!\n");
        print_usage(argv);
        exit(1);
    }

    // wlconf.display();

    SimplePattern simplepattern(wlconf.file_size, 
            wlconf.fsync,
            wlconf.sync,
            wlconf.write_size, wlconf.n_writes, 
            wlconf.pattern, wlconf.file_path.c_str(), wlconf.tag);

    // SimplePattern simplepattern(64, 32, 10, SEQUENTIAL, "/tmp/littletest");
    // SimplePattern simplepattern(64, 32, 10, RANDOM, "/tmp/littletest");

    gettimeofday(&start, NULL);

    // run the workload
    simplepattern.run();

    gettimeofday(&end, NULL);

    timersub(&end, &start, &result);

    if (wlconf.markerfile.length() > 0) {
        append_to_marker_file(wlconf.markerfile.c_str(), wlconf.file_path.c_str());
    }

    cout <<"pid     " << getpid() << endl;
    printf("--- Performance ---\n");
    printf("duration %ld.%ld\n", result.tv_sec, result.tv_usec);
    printf("start    %ld.%ld\n", start.tv_sec, start.tv_usec);
    printf("end      %ld.%ld\n", end.tv_sec, end.tv_usec);

    return 0;
}



